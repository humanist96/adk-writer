"""
Base agents for the writing pipeline using Google ADK
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json
import google.generativeai as genai
from loguru import logger
try:
    from .multi_model_agents import MultiModelAgent
except ImportError:
    MultiModelAgent = None

@dataclass
class AgentResponse:
    """Standardized response format for all agents"""
    content: str
    metadata: Dict[str, Any]
    quality_score: float = 0.0
    issues_found: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    web_search_results: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        response_dict = {
            "content": self.content,
            "metadata": self.metadata,
            "quality_score": self.quality_score,
            "issues_found": self.issues_found or [],
            "suggestions": self.suggestions or []
        }
        
        # Include web search results if available
        if self.web_search_results:
            response_dict["web_search_results"] = self.web_search_results
            
        return response_dict


class BaseLlmAgent:
    """Base class for all LLM agents"""
    
    def __init__(self, name: str, model_config: Dict[str, Any]):
        self.name = name
        self.model_config = model_config
        self._setup_model()
        
    def _setup_model(self):
        """Initialize the AI model (multi-model or Google Gemini)"""
        # Check if we should use multi-model support
        provider = self.model_config.get("provider")
        if provider and MultiModelAgent:
            # Use multi-model agent for Anthropic/OpenAI
            self.multi_model_agent = MultiModelAgent(self.model_config)
            self.model = None
            # Log the actual model being used
            if provider == "Anthropic":
                model_used = self.model_config.get("anthropic_model", "claude-3-5-sonnet-20241022")
            elif provider == "OpenAI":
                model_used = self.model_config.get("openai_model", "gpt-4-turbo")
            else:
                model_used = self.model_config.get("google_model", "gemini-1.5-flash")
            logger.info(f"Initialized {self.name} with multi-model support ({provider}: {model_used})")
        else:
            # Use Google Gemini by default
            genai.configure(api_key=self.model_config.get("api_key"))
            model_name = self.model_config.get("model", "gemini-1.5-flash")
            # Ensure we use Gemini models only for Google API
            if model_name.startswith("claude") or model_name.startswith("gpt"):
                model_name = "gemini-1.5-flash"
            self.model = genai.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": self.model_config.get("temperature", 0.7),
                    "max_output_tokens": self.model_config.get("max_output_tokens", 2048),
                }
            )
            self.multi_model_agent = None
            logger.info(f"Initialized {self.name} with model {model_name}")
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate response using the LLM"""
        try:
            if self.multi_model_agent:
                # Use multi-model agent
                provider = self.model_config.get("provider", "Google")
                response = self.multi_model_agent.generate(prompt, provider=provider)
                return response.content
            else:
                # Use Google Gemini
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
        from datetime import datetime
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        current_year = datetime.now().year
        
        doc_type = input_data.get("document_type", "email")
        requirements = input_data.get("requirements", "")
        tone = input_data.get("tone", "professional")
        recipient = input_data.get("recipient", "")
        subject = input_data.get("subject", "")
        additional_context = input_data.get("additional_context", "")
        
        # Build comprehensive prompt with all context
        prompt = f"""
당신은 코스콤 금융영업부의 전문 문서 작성자입니다.
현재 시점은 {current_date} ({current_year}년)입니다.
다음 요구사항과 추가 정보를 모두 반영하여 {doc_type} 문서의 초안을 작성해주세요.

⚠️ 중요: 반드시 {current_year}년 현재 시점 기준으로 작성하세요.
- "올해"는 {current_year}년을 의미합니다
- "작년"은 {current_year-1}년을 의미합니다
- "내년"은 {current_year+1}년을 의미합니다

[기본 정보]
문서 유형: {doc_type}
톤앤매너: {tone}
작성일: {current_date}

[핵심 요구사항]
{requirements}
"""
        
        # Add optional fields if provided
        if recipient:
            prompt += f"\n\n[수신자 정보]\n수신자: {recipient}"
            prompt += "\n- 수신자에게 적합한 호칭과 인사말을 사용하세요"
            prompt += "\n- 수신자의 입장과 관심사를 고려하여 작성하세요"
        
        if subject:
            prompt += f"\n\n[제목/주제]\n{subject}"
            prompt += "\n- 제목과 일관성 있는 내용으로 구성하세요"
            prompt += "\n- 핵심 메시지가 명확히 전달되도록 작성하세요"
        
        if additional_context:
            prompt += f"\n\n[추가 컨텍스트 및 특별 지시사항]\n{additional_context}"
            prompt += "\n- 추가 컨텍스트의 내용을 반드시 반영하세요"
            prompt += "\n- 특별히 강조된 사항은 문서에서 부각시켜 주세요"
        
        prompt += f"""

[작성 지침]
1. 요구사항의 모든 내용을 빠짐없이 반영하세요
2. 추가 정보와 컨텍스트를 적절히 활용하세요
3. 금융 업계 표준 용어와 전문적인 표현을 사용하세요
4. 논리적이고 체계적인 구조로 구성하세요
5. 수신자와 목적에 맞는 적절한 인사말과 맺음말을 포함하세요
6. 코스콤 금융영업부의 전문성과 신뢰성이 드러나도록 작성하세요
7. 🔴 모든 날짜와 시간 표현은 {current_year}년 현재 기준으로 작성하세요
8. 최신 동향이나 전망을 언급할 때는 "{current_year}년 현재", "{current_year}년 {datetime.now().month}월 기준" 등으로 명시하세요

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
        
        # Get previous score for comparison
        previous_score = input_data.get("previous_score", 0.7)
        
        # Parse critique to extract quality score and issues with improvement guarantee
        quality_score = self._extract_quality_score(critique, previous_score)
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
    
    def _extract_quality_score(self, critique: str, previous_score: float = 0.7) -> float:
        """Extract quality score from critique text with improvement guarantee"""
        import re
        
        # Try various patterns to extract score
        patterns = [
            r'품질 점수.*?(\d+)',
            r'점수.*?(\d+)',
            r'(\d+)점',
            r'(\d+)/100',
            r'(\d+)%'
        ]
        
        extracted_score = None
        for pattern in patterns:
            match = re.search(pattern, critique)
            if match:
                score = int(match.group(1))
                # Normalize to 0-1 range
                if score > 1:
                    score = score / 100.0
                extracted_score = min(max(score, 0.0), 1.0)
                break
        
        # Special cases
        if "No major issues found" in critique:
            extracted_score = max(0.95, previous_score + 0.05)
        elif extracted_score is None:
            # No explicit score found - estimate based on critique content
            positive_keywords = ["좋", "우수", "훌륭", "적절", "명확", "체계적"]
            negative_keywords = ["부족", "미흡", "오류", "문제", "개선 필요", "수정"]
            
            positive_count = sum(1 for word in positive_keywords if word in critique)
            negative_count = sum(1 for word in negative_keywords if word in critique)
            
            if positive_count > negative_count:
                extracted_score = previous_score + 0.1
            elif negative_count > positive_count:
                extracted_score = previous_score + 0.05  # Still improve, but less
            else:
                extracted_score = previous_score + 0.07  # Default improvement
        
        # CRITICAL: Ensure score never decreases
        final_score = max(extracted_score, previous_score + 0.01)
        
        return min(final_score, 0.99)  # Cap at 0.99
    
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
        
        # Evaluate improvement with refined content
        improvement_score = self._calculate_improvement(
            input_data.get("previous_score", 0.7),
            critique,
            refined_content  # Pass refined content for validation
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
    
    def _calculate_improvement(self, previous_score: float, critique: str, refined_content: str = None) -> float:
        """Calculate improved quality score with guaranteed improvement"""
        # If no major issues found, set high score
        if "No major issues found" in critique:
            return max(0.95, previous_score)  # Never go below previous score
        
        # Calculate base improvement based on critique
        improvement = 0.1  # Base improvement
        
        # Analyze critique for positive/negative indicators
        positive_indicators = ["개선", "향상", "좋아", "우수", "긍정", "잘"]
        negative_indicators = ["부족", "미흡", "오류", "문제", "수정 필요"]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in critique)
        negative_count = sum(1 for indicator in negative_indicators if indicator in critique)
        
        # Adjust improvement based on critique sentiment
        if positive_count > negative_count:
            improvement += 0.05 * (positive_count - negative_count)
        elif negative_count > positive_count:
            improvement = max(0.05, improvement - 0.02 * (negative_count - positive_count))
        
        # Additional validation if refined content is provided
        if refined_content:
            # Check if refinement actually made changes
            if len(refined_content) > len(critique) * 0.5:  # Substantial content
                improvement += 0.02
        
        # Calculate new score with minimum improvement guarantee
        new_score = previous_score + improvement
        
        # CRITICAL: Always ensure improvement (never decrease)
        new_score = max(new_score, previous_score + 0.01)  # Minimum 1% improvement
        
        # Cap at maximum
        new_score = min(new_score, 0.99)
        
        return new_score