"""
Custom tools for financial document processing
"""

from typing import Dict, Any, List, Optional, Tuple
import re
import json
from datetime import datetime
from loguru import logger


class FinancialTermValidator:
    """Validate and check financial terminology"""
    
    def __init__(self):
        self.financial_terms = {
            "투자": ["investment", "투자"],
            "수익률": ["return rate", "yield", "수익률"],
            "리스크": ["risk", "위험", "리스크"],
            "포트폴리오": ["portfolio", "포트폴리오"],
            "자산": ["asset", "자산"],
            "부채": ["liability", "debt", "부채"],
            "유동성": ["liquidity", "유동성"],
            "변동성": ["volatility", "변동성"],
            "헤지": ["hedge", "헤지"],
            "파생상품": ["derivative", "파생상품"],
            "채권": ["bond", "채권"],
            "주식": ["stock", "equity", "주식"],
            "펀드": ["fund", "펀드"],
            "ETF": ["ETF", "상장지수펀드"],
            "선물": ["futures", "선물"],
            "옵션": ["option", "옵션"],
            "스왑": ["swap", "스왑"],
            "금리": ["interest rate", "금리"],
            "환율": ["exchange rate", "환율"],
            "신용등급": ["credit rating", "신용등급"]
        }
        
        self.term_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for term detection"""
        patterns = {}
        for category, terms in self.financial_terms.items():
            pattern = r'\b(' + '|'.join(re.escape(term) for term in terms) + r')\b'
            patterns[category] = re.compile(pattern, re.IGNORECASE)
        return patterns
    
    def validate(self, text: str) -> Dict[str, Any]:
        """
        Validate financial terms in text
        
        Args:
            text: Document text to validate
            
        Returns:
            Validation results with found terms and suggestions
        """
        results = {
            "valid": True,
            "found_terms": [],
            "missing_context": [],
            "suggestions": [],
            "score": 1.0
        }
        
        # Check for financial terms
        for category, pattern in self.term_patterns.items():
            matches = pattern.findall(text)
            if matches:
                results["found_terms"].append({
                    "category": category,
                    "terms": list(set(matches))
                })
        
        # Check for potentially missing context
        if "투자" in text.lower() and "리스크" not in text.lower():
            results["missing_context"].append("투자 언급 시 리스크 설명 권장")
            results["score"] -= 0.1
        
        if "수익률" in text.lower() and "기준" not in text.lower():
            results["missing_context"].append("수익률 언급 시 산정 기준 명시 필요")
            results["score"] -= 0.1
        
        # Generate suggestions
        if results["missing_context"]:
            results["valid"] = False
            results["suggestions"] = results["missing_context"]
        
        logger.info(f"Term validation complete. Score: {results['score']}")
        return results


class ComplianceChecker:
    """Check compliance with financial regulations"""
    
    def __init__(self):
        self.required_disclaimers = {
            "investment_risk": "투자 원금 손실 가능성에 대한 경고",
            "past_performance": "과거 수익률이 미래 수익을 보장하지 않음",
            "tax_implications": "세금 관련 사항은 개인별로 상이할 수 있음",
            "professional_advice": "전문가 상담 권유",
            "market_volatility": "시장 변동성에 대한 주의"
        }
        
        self.prohibited_terms = [
            "보장",
            "확실한 수익",
            "무위험",
            "손실 없음",
            "100% 안전"
        ]
    
    def check(self, text: str, doc_type: str) -> Dict[str, Any]:
        """
        Check document compliance
        
        Args:
            text: Document text to check
            doc_type: Type of document
            
        Returns:
            Compliance check results
        """
        results = {
            "compliant": True,
            "issues": [],
            "required_disclaimers": [],
            "prohibited_terms_found": [],
            "score": 1.0
        }
        
        # Check for prohibited terms
        for term in self.prohibited_terms:
            if term in text:
                results["prohibited_terms_found"].append(term)
                results["compliant"] = False
                results["score"] -= 0.2
                results["issues"].append(f"금지된 용어 사용: '{term}'")
        
        # Check required disclaimers based on document type
        if doc_type in ["proposal", "investment"]:
            if "리스크" not in text and "위험" not in text:
                results["required_disclaimers"].append(self.required_disclaimers["investment_risk"])
                results["score"] -= 0.15
            
            if "과거" in text and "수익" in text:
                if "보장하지 않" not in text:
                    results["required_disclaimers"].append(self.required_disclaimers["past_performance"])
                    results["score"] -= 0.1
        
        if results["required_disclaimers"] or results["prohibited_terms_found"]:
            results["compliant"] = False
        
        logger.info(f"Compliance check complete. Compliant: {results['compliant']}")
        return results


class TemplateManager:
    """Manage document templates for different types"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load document templates"""
        return {
            "email": {
                "structure": ["greeting", "introduction", "main_content", "call_to_action", "closing"],
                "tone": "professional_friendly",
                "max_length": 500,
                "template": """
제목: {subject}

안녕하십니까, {recipient}님

{introduction}

{main_content}

{call_to_action}

궁금하신 사항이 있으시면 언제든지 연락 주시기 바랍니다.

감사합니다.

{sender}
{position}
{company}
{contact}
                """
            },
            "proposal": {
                "structure": ["executive_summary", "background", "proposal", "benefits", "risks", "conclusion"],
                "tone": "formal_professional",
                "max_length": 2000,
                "template": """
[투자 제안서]

작성일: {date}
제안 대상: {client}
작성자: {author}

1. 개요
{executive_summary}

2. 배경 및 목적
{background}

3. 투자 제안
{proposal}

4. 기대 효과
{benefits}

5. 리스크 관리
{risks}

6. 결론 및 권고사항
{conclusion}

※ 본 제안서는 정보 제공 목적으로 작성되었으며, 투자 결정 전 전문가와 상담하시기 바랍니다.
                """
            },
            "report": {
                "structure": ["title", "summary", "analysis", "recommendations", "appendix"],
                "tone": "formal_analytical",
                "max_length": 3000,
                "template": """
[{report_type} 보고서]

문서번호: {doc_number}
작성일: {date}
작성부서: {department}

제목: {title}

요약
{summary}

상세 분석
{analysis}

권고사항
{recommendations}

첨부자료
{appendix}
                """
            }
        }
    
    def get_template(self, doc_type: str) -> Dict[str, Any]:
        """Get template for document type"""
        return self.templates.get(doc_type, self.templates["email"])
    
    def apply_template(self, content: Dict[str, str], doc_type: str) -> str:
        """
        Apply template to content
        
        Args:
            content: Dictionary with content for each template field
            doc_type: Type of document
            
        Returns:
            Formatted document text
        """
        template_info = self.get_template(doc_type)
        template = template_info["template"]
        
        # Fill in the template
        try:
            formatted = template.format(**content)
            return formatted
        except KeyError as e:
            logger.error(f"Missing template field: {e}")
            return template


class QualityScorer:
    """Calculate document quality scores"""
    
    def __init__(self):
        self.criteria_weights = {
            "grammar": 0.2,
            "terminology": 0.25,
            "structure": 0.2,
            "clarity": 0.15,
            "compliance": 0.2
        }
    
    def calculate_score(self, 
                       text: str,
                       term_validation: Dict[str, Any],
                       compliance_check: Dict[str, Any],
                       critique_feedback: Optional[str] = None) -> Tuple[float, Dict[str, float]]:
        """
        Calculate comprehensive quality score
        
        Args:
            text: Document text
            term_validation: Results from term validator
            compliance_check: Results from compliance checker
            critique_feedback: Optional feedback from critic agent
            
        Returns:
            Overall score and breakdown by criteria
        """
        scores = {
            "grammar": 0.9,  # Base score, can be enhanced with grammar checker
            "terminology": term_validation.get("score", 0.8),
            "structure": self._evaluate_structure(text),
            "clarity": self._evaluate_clarity(text),
            "compliance": compliance_check.get("score", 0.8)
        }
        
        # Adjust based on critique feedback if available
        if critique_feedback:
            if "문법" in critique_feedback and "오류" in critique_feedback:
                scores["grammar"] -= 0.2
            if "명확" in critique_feedback and "불명확" in critique_feedback:
                scores["clarity"] -= 0.15
        
        # Calculate weighted average
        overall_score = sum(scores[k] * self.criteria_weights[k] 
                          for k in scores.keys())
        
        logger.info(f"Quality score calculated: {overall_score:.2f}")
        return overall_score, scores
    
    def _evaluate_structure(self, text: str) -> float:
        """Evaluate document structure"""
        score = 0.8  # Base score
        
        # Check for proper paragraphing
        paragraphs = text.split('\n\n')
        if len(paragraphs) < 2:
            score -= 0.2
        elif len(paragraphs) > 10:
            score -= 0.1
        
        # Check for section headers (numbered or titled)
        if re.search(r'^\d+\.|\[.+\]|^#+', text, re.MULTILINE):
            score += 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _evaluate_clarity(self, text: str) -> float:
        """Evaluate text clarity"""
        score = 0.85  # Base score
        
        # Check sentence length
        sentences = re.split(r'[.!?]', text)
        avg_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if avg_length > 30:  # Too long
            score -= 0.2
        elif avg_length < 5:  # Too short
            score -= 0.1
        
        # Check for passive voice indicators (Korean)
        passive_indicators = ["되다", "되었", "되는", "됩니다", "되었습니다"]
        passive_count = sum(1 for indicator in passive_indicators if indicator in text)
        if passive_count > len(sentences) * 0.5:
            score -= 0.15
        
        return min(max(score, 0.0), 1.0)


# Tool function exports for agent integration
def validate_financial_terms(text: str) -> Dict[str, Any]:
    """Validate financial terms in document"""
    validator = FinancialTermValidator()
    return validator.validate(text)


def check_compliance(text: str, doc_type: str) -> Dict[str, Any]:
    """Check document compliance"""
    checker = ComplianceChecker()
    return checker.check(text, doc_type)


def apply_template(content: Dict[str, str], doc_type: str) -> str:
    """Apply document template"""
    manager = TemplateManager()
    return manager.apply_template(content, doc_type)


def calculate_quality_score(text: str, 
                           term_validation: Dict[str, Any] = None,
                           compliance_check: Dict[str, Any] = None,
                           critique_feedback: str = None) -> float:
    """Calculate document quality score"""
    if term_validation is None:
        term_validation = validate_financial_terms(text)
    if compliance_check is None:
        compliance_check = check_compliance(text, "general")
    
    scorer = QualityScorer()
    overall_score, _ = scorer.calculate_score(
        text, term_validation, compliance_check, critique_feedback
    )
    return overall_score


# Export all tools
__all__ = [
    'FinancialTermValidator',
    'ComplianceChecker',
    'TemplateManager',
    'QualityScorer',
    'validate_financial_terms',
    'check_compliance',
    'apply_template',
    'calculate_quality_score'
]