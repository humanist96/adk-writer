"""
Base agents for the writing pipeline using Google ADK
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
import google.generativeai as genai
from loguru import logger

@dataclass
class AgentResponse:
    """Standardized response format for all agents"""
    content: str
    metadata: Dict[str, Any]
    quality_score: float = 0.0
    issues_found: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "issues_found": self.issues_found or [],
            "suggestions": self.suggestions or []
        }


class BaseLlmAgent:
    """Base class for all LLM agents"""
    
    def __init__(self, name: str, model_config: Dict[str, Any]):
        self.name = name
        self.model_config = model_config
        self._setup_model()
        
    def _setup_model(self):
        """Initialize the Google Generative AI model"""
        genai.configure(api_key=self.model_config.get("api_key"))
        self.model = genai.GenerativeModel(
            model_name=self.model_config.get("model", "gemini-1.5-pro"),
            generation_config={
                "temperature": self.model_config.get("temperature", 0.7),
                "max_output_tokens": self.model_config.get("max_output_tokens", 2048),
            }
        )
        logger.info(f"Initialized {self.name} with model {self.model_config.get('model')}")
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using the LLM"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error in {self.name}: {str(e)}")
            raise
    
    def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Process input and return structured response"""
        raise NotImplementedError("Subclasses must implement process method")


class DraftWriterAgent(BaseLlmAgent):
    """Agent responsible for creating initial drafts"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__("DraftWriterAgent", model_config)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load document templates"""
        return {
            "email": """
주제: {subject}
수신: {recipient}
발신: {sender}

안녕하십니까, {recipient}님

{content}

감사합니다.
{sender} 드림
            """,
            "proposal": """
[투자 제안서]

제목: {title}
작성일: {date}
대상: {target}

1. 제안 개요
{overview}

2. 투자 상품 설명
{product_description}

3. 예상 수익률
{expected_returns}

4. 리스크 관리
{risk_management}

5. 결론
{conclusion}
            """,
            "official_letter": """
[공식 문서]

문서번호: {doc_number}
날짜: {date}
수신: {recipient}
발신: {sender}
제목: {subject}

{content}

[서명]
{signature}
            """
        }
    
    def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Generate initial draft based on input"""
        doc_type = input_data.get("document_type", "email")
        requirements = input_data.get("requirements", "")
        tone = input_data.get("tone", "professional")
        
        prompt = f"""
당신은 금융영업부의 전문 문서 작성자입니다.
다음 요구사항에 따라 {doc_type} 문서의 초안을 작성해주세요.

문서 유형: {doc_type}
톤앤매너: {tone}
요구사항: {requirements}

다음 사항을 반드시 포함해주세요:
1. 명확하고 전문적인 표현
2. 금융 업계 표준 용어 사용
3. 논리적인 구조
4. 적절한 인사말과 맺음말

초안을 작성해주세요:
"""
        
        draft_content = self.generate(prompt)
        
        return AgentResponse(
            content=draft_content,
            metadata={
                "agent": self.name,
                "document_type": doc_type,
                "tone": tone,
                "iteration": input_data.get("iteration", 1)
            },
            quality_score=0.7  # Initial draft baseline score
        )


class CriticAgent(BaseLlmAgent):
    """Agent responsible for critiquing and evaluating drafts"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__("CriticAgent", model_config)
        self.evaluation_criteria = {
            "grammar": "문법 및 맞춤법 정확성",
            "terminology": "금융 전문 용어의 적절성",
            "structure": "문서 구조의 논리성",
            "clarity": "내용의 명확성",
            "compliance": "금융 규정 준수 여부",
            "tone": "톤앤매너 일관성"
        }
    
    def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Critique the draft and provide feedback"""
        draft = input_data.get("draft", "")
        doc_type = input_data.get("document_type", "email")
        
        # Build evaluation prompt
        criteria_text = "\n".join([f"- {k}: {v}" for k, v in self.evaluation_criteria.items()])
        
        prompt = f"""
당신은 금융 문서 전문 비평가입니다.
다음 초안을 엄격하게 평가하고 구체적인 피드백을 제공해주세요.

문서 유형: {doc_type}

[초안]
{draft}

[평가 기준]
{criteria_text}

다음 형식으로 평가를 제공해주세요:

1. 전체 품질 점수 (0-100):
2. 발견된 주요 문제점:
3. 구체적인 개선 제안:
4. 긍정적인 측면:
5. 최종 평가:

만약 문서가 모든 기준을 충족하고 수정이 필요 없다면,
"No major issues found"라고 명시해주세요.
"""
        
        critique = self.generate(prompt)
        
        # Parse critique to extract quality score and issues
        quality_score = self._extract_quality_score(critique)
        issues = self._extract_issues(critique)
        suggestions = self._extract_suggestions(critique)
        
        return AgentResponse(
            content=critique,
            metadata={
                "agent": self.name,
                "document_type": doc_type,
                "iteration": input_data.get("iteration", 1)
            },
            quality_score=quality_score,
            issues_found=issues,
            suggestions=suggestions
        )
    
    def _extract_quality_score(self, critique: str) -> float:
        """Extract quality score from critique text"""
        import re
        # Try various patterns
        patterns = [
            r'품질 점수.*?(\d+)',
            r'점수.*?(\d+)',
            r'(\d+)점',
            r'(\d+)/100',
            r'(\d+)%'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, critique)
            if match:
                score = int(match.group(1))
                # Normalize to 0-1 range
                if score > 1:
                    score = score / 100.0
                return min(max(score, 0.0), 1.0)
        
        # If no score found but "No major issues found" is present
        if "No major issues found" in critique:
            return 0.95
        
        return 0.7  # Default score if not found
    
    def _extract_issues(self, critique: str) -> List[str]:
        """Extract issues from critique"""
        issues = []
        if "문제점" in critique:
            # Simple extraction logic - can be enhanced
            lines = critique.split('\n')
            capturing = False
            for line in lines:
                if "문제점" in line:
                    capturing = True
                    continue
                elif capturing and line.strip() and not line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    if line.strip().startswith('-'):
                        issues.append(line.strip()[1:].strip())
                elif capturing and ("제안" in line or "긍정" in line):
                    break
        return issues
    
    def _extract_suggestions(self, critique: str) -> List[str]:
        """Extract improvement suggestions from critique"""
        suggestions = []
        if "제안" in critique:
            lines = critique.split('\n')
            capturing = False
            for line in lines:
                if "제안" in line:
                    capturing = True
                    continue
                elif capturing and line.strip() and not line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                    if line.strip().startswith('-'):
                        suggestions.append(line.strip()[1:].strip())
                elif capturing and ("긍정" in line or "최종" in line):
                    break
        return suggestions


class RefinerAgent(BaseLlmAgent):
    """Agent responsible for refining drafts based on critique"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__("RefinerAgent", model_config)
    
    def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Refine the draft based on critique feedback"""
        draft = input_data.get("draft", "")
        critique = input_data.get("critique", "")
        doc_type = input_data.get("document_type", "email")
        
        prompt = f"""
당신은 금융 문서 정제 전문가입니다.
다음 초안과 비평을 바탕으로 개선된 최종 문서를 작성해주세요.

문서 유형: {doc_type}

[원본 초안]
{draft}

[비평 및 개선 제안]
{critique}

위의 비평을 모두 반영하여 다음 사항을 개선해주세요:
1. 지적된 문제점 수정
2. 제안된 개선사항 적용
3. 전문성과 명확성 향상
4. 금융 규정 준수 확인

개선된 최종 문서를 작성해주세요:
"""
        
        refined_content = self.generate(prompt)
        
        # Evaluate improvement
        improvement_score = self._calculate_improvement(
            input_data.get("previous_score", 0.7),
            critique
        )
        
        return AgentResponse(
            content=refined_content,
            metadata={
                "agent": self.name,
                "document_type": doc_type,
                "iteration": input_data.get("iteration", 1),
                "refined": True
            },
            quality_score=improvement_score
        )
    
    def _calculate_improvement(self, previous_score: float, critique: str) -> float:
        """Calculate improved quality score"""
        # If no major issues found, set high score
        if "No major issues found" in critique:
            return 0.95
        
        # Otherwise, incremental improvement
        improvement = 0.1  # Base improvement
        if "긍정" in critique:
            improvement += 0.05
        
        new_score = min(previous_score + improvement, 0.99)
        return new_score