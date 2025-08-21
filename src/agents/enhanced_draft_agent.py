"""
Enhanced Draft Writer Agent with Web Search Integration
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
from loguru import logger
from .base_agents import BaseLlmAgent, AgentResponse
from ..tools.web_search_tool import (
    create_web_search_enricher,
    enrich_document_with_search,
    WebSearchEnricher
)


class EnhancedDraftWriterAgent(BaseLlmAgent):
    """Enhanced agent that creates drafts enriched with web search results"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__("EnhancedDraftWriterAgent", model_config)
        self.templates = self._load_templates()
        self.search_enricher = None
        self._setup_search_enricher(model_config)
    
    def _setup_search_enricher(self, model_config: Dict[str, Any]):
        """Initialize web search enricher"""
        # Check for search API keys in config
        search_provider = model_config.get('search_provider', 'fallback')
        search_api_key = model_config.get('search_api_key')
        
        if search_provider == 'google':
            search_engine_id = model_config.get('google_search_engine_id')
            self.search_enricher = create_web_search_enricher(
                'google', search_api_key, search_engine_id=search_engine_id
            )
        elif search_provider == 'bing':
            self.search_enricher = create_web_search_enricher('bing', search_api_key)
        else:
            # Use fallback provider (no API key needed)
            self.search_enricher = create_web_search_enricher('fallback')
        
        logger.info(f"Initialized web search enricher with {search_provider} provider")
    
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

2. 시장 현황 및 전망
{market_analysis}

3. 투자 상품 설명
{product_description}

4. 예상 수익률
{expected_returns}

5. 리스크 관리
{risk_management}

6. 결론
{conclusion}

[참고 자료]
{references}
            """,
            "report": """
[분석 보고서]

문서번호: {doc_number}
작성일: {date}
제목: {title}

요약
{summary}

1. 배경 및 목적
{background}

2. 현황 분석
{current_analysis}

3. 시장 동향
{market_trends}

4. 상세 분석
{detailed_analysis}

5. 권고사항
{recommendations}

6. 참고 자료
{references}
            """
        }
    
    def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """Generate enhanced draft with web search integration"""
        doc_type = input_data.get("document_type", "email")
        requirements = input_data.get("requirements", "")
        tone = input_data.get("tone", "professional")
        recipient = input_data.get("recipient", "")
        subject = input_data.get("subject", "")
        additional_context = input_data.get("additional_context", "")
        enable_web_search = input_data.get("enable_web_search", False)
        search_config = input_data.get("search_config", {})
        
        # Step 1: Generate initial draft
        initial_draft = self._generate_initial_draft(
            doc_type, requirements, tone, recipient, subject, additional_context
        )
        
        # Step 2: Enrich with web search if enabled
        if enable_web_search and self.search_enricher:
            logger.info(f"Enriching document with web search results. Search provider: {getattr(self.search_enricher, 'provider', 'Unknown')}")
            logger.debug(f"Search config: {search_config}")
            enrichment_data = self._enrich_with_search(
                initial_draft, subject or requirements[:50], doc_type, search_config
            )
            logger.info(f"Enrichment data keys: {enrichment_data.keys() if enrichment_data else 'None'}")
            if enrichment_data:
                logger.info(f"Found {len(enrichment_data.get('relevant_information', []))} relevant sources")
            
            # Step 3: Generate enhanced draft with search results
            final_draft = self._generate_enhanced_draft(
                initial_draft, enrichment_data, doc_type, requirements, tone
            )
            
            metadata = {
                "agent": self.name,
                "document_type": doc_type,
                "tone": tone,
                "iteration": input_data.get("iteration", 1),
                "web_search_enabled": True,
                "search_queries": enrichment_data.get('search_queries', []),
                "sources_used": len(enrichment_data.get('relevant_information', [])),
                "enrichment_suggestions": enrichment_data.get('enrichment_suggestions', [])
            }
        else:
            final_draft = initial_draft
            metadata = {
                "agent": self.name,
                "document_type": doc_type,
                "tone": tone,
                "iteration": input_data.get("iteration", 1),
                "web_search_enabled": False
            }
        
        # Create response
        response = AgentResponse(
            content=final_draft,
            metadata=metadata,
            quality_score=0.75 if enable_web_search else 0.7,
            suggestions=self._extract_suggestions(enrichment_data) if enable_web_search else []
        )
        
        # Add web search results to response if available
        if enable_web_search and enrichment_data:
            response.web_search_results = enrichment_data
            logger.info(f"Added web search results to response: {len(enrichment_data.get('relevant_information', []))} sources")
        else:
            logger.warning(f"No web search results added to response. Web search enabled: {enable_web_search}, Enrichment data available: {bool(enrichment_data)}")
        
        return response
    
    def _generate_initial_draft(self, doc_type: str, requirements: str, 
                               tone: str, recipient: str, subject: str,
                               additional_context: str) -> str:
        """Generate initial draft without web search"""
        from datetime import datetime
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        current_year = datetime.now().year
        
        prompt = f"""
당신은 코스콤 금융영업부의 전문 문서 작성자입니다.
현재 시점은 {current_date} ({current_year}년)입니다.
다음 요구사항과 추가 정보를 모두 반영하여 {doc_type} 문서의 초안을 작성해주세요.

⚠️ 중요: 반드시 {current_year}년 현재 시점 기준으로 작성하세요.
- "올해"는 {current_year}년을 의미합니다
- "작년"은 {current_year-1}년을 의미합니다
- "내년"은 {current_year+1}년을 의미합니다
- 모든 날짜와 시간 표현은 {current_year}년 기준으로 작성하세요

[기본 정보]
문서 유형: {doc_type}
톤앤매너: {tone}
작성일: {current_date}

[핵심 요구사항]
{requirements}
"""
        
        if recipient:
            prompt += f"\n\n[수신자 정보]\n수신자: {recipient}"
            prompt += "\n- 수신자에게 적합한 호칭과 인사말을 사용하세요"
        
        if subject:
            prompt += f"\n\n[제목/주제]\n{subject}"
            prompt += "\n- 제목과 일관성 있는 내용으로 구성하세요"
        
        if additional_context:
            prompt += f"\n\n[추가 컨텍스트]\n{additional_context}"
        
        prompt += f"""

[작성 지침]
1. 요구사항의 모든 내용을 빠짐없이 반영하세요
2. 금융 업계 표준 용어와 전문적인 표현을 사용하세요
3. 논리적이고 체계적인 구조로 구성하세요
4. 코스콤 금융영업부의 전문성과 신뢰성이 드러나도록 작성하세요
5. 🔴 모든 날짜와 시간 표현은 {current_year}년 현재 기준으로 작성하세요
6. 최신 동향이나 전망을 언급할 때는 "{current_year}년 현재", "{current_year}년 {datetime.now().month}월 기준" 등으로 명시하세요

초안을 작성해주세요:
"""
        
        return self.generate(prompt)
    
    def _enrich_with_search(self, draft: str, title: str, 
                           doc_type: str, search_config: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich draft with web search results"""
        try:
            enrichment_data = self.search_enricher.enrich_document(
                document=draft,
                title=title,
                document_type=doc_type,
                search_config=search_config
            )
            
            logger.info(f"Found {len(enrichment_data.get('relevant_information', []))} relevant search results")
            return enrichment_data
            
        except Exception as e:
            logger.error(f"Error during web search enrichment: {str(e)}")
            return {
                'relevant_information': [],
                'enrichment_suggestions': [],
                'search_queries': []
            }
    
    def _generate_enhanced_draft(self, initial_draft: str, 
                                enrichment_data: Dict[str, Any],
                                doc_type: str, requirements: str,
                                tone: str) -> str:
        """Generate enhanced draft incorporating search results"""
        relevant_info = enrichment_data.get('relevant_information', [])
        suggestions = enrichment_data.get('enrichment_suggestions', [])
        
        if not relevant_info and not suggestions:
            return initial_draft
        
        # Prepare search results summary
        search_summary = self._prepare_search_summary(relevant_info)
        suggestions_text = self._prepare_suggestions_text(suggestions)
        
        from datetime import datetime
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        prompt = f"""
당신은 코스콤 금융영업부의 전문 문서 작성자입니다.
현재 시점은 {current_date} ({current_year}년 {current_month}월)입니다.
다음 초안을 웹 검색 결과와 제안사항을 반영하여 개선해주세요.

⚠️ 필수: 모든 내용을 {current_year}년 현재 시점 기준으로 작성하세요!

[원본 초안]
{initial_draft}

[웹 검색을 통해 발견한 관련 정보 - {current_year}년 최신 자료]
{search_summary}

[문서 개선 제안사항]
{suggestions_text}

[개선 지침]
1. 🔴 필수: 모든 날짜 표현을 {current_year}년 기준으로 작성하세요
   - "올해" = {current_year}년
   - "작년" = {current_year-1}년
   - "내년" = {current_year+1}년
   - "현재" = {current_year}년 {current_month}월
2. 검색된 최신 정보와 URL을 반드시 활용하여 시의성 있는 내용으로 작성하세요
3. 검색 결과의 구체적인 날짜, 수치, 사례를 인용하여 신뢰성을 높이세요
4. "{current_year}년 {current_month}월 기준", "{current_year}년 현재", "최근 발표된" 등 시간 표현을 명시하여 최신성을 강조하세요
5. 검색 결과의 URL과 출처를 참고 자료 섹션에 명확히 표시하세요
6. 문서 내용에 "최근 (출처)에 따르면", "({current_year}년 {current_month}월) 발표된 자료에 의하면" 등으로 출처와 시점을 명시하세요
7. 톤앤매너({tone})를 일관되게 유지하세요
8. 가장 최신 정보를 우선적으로 활용하고, 오래된 정보는 보조적으로만 사용하세요
9. 검색 결과가 제공한 URL들을 참고 자료 섹션에 모두 포함시키세요
10. 🔴 반드시 {current_year}년 현재 시점에서 작성된 문서임을 명확히 하세요

개선된 문서를 작성해주세요:
"""
        
        enhanced_draft = self.generate(prompt)
        
        # Always add references section when web search was used
        if relevant_info:
            from datetime import datetime
            current_year = datetime.now().year
            references = self._generate_references(relevant_info)
            # Add references section with clear visibility
            references_section = "\n\n" + "="*50 + "\n"
            references_section += f"📚 참고 자료 및 출처 ({current_year}년 최신)\n"
            references_section += "="*50 + "\n"
            references_section += references
            references_section += "\n" + "="*50
            enhanced_draft += references_section
            logger.info(f"Added {len(relevant_info)} references to the document")
        
        return enhanced_draft
    
    def _prepare_search_summary(self, relevant_info: List[Dict[str, Any]]) -> str:
        """Prepare summary of search results with emphasis on recent information"""
        if not relevant_info:
            return "검색 결과 없음"
        
        summary_lines = []
        summary_lines.append(f"🔍 총 {len(relevant_info)}개의 최신 정보를 발견했습니다.\n")
        
        for idx, info in enumerate(relevant_info[:5], 1):  # Show top 5
            summary_lines.append(f"{idx}. {info['title']}")
            
            # Add date if available
            if info.get('content_date'):
                summary_lines.append(f"   📅 {info['content_date']}")
            
            # Add URL
            if info.get('url'):
                summary_lines.append(f"   🔗 {info['url']}")
            
            # Add summary
            if info.get('summary'):
                summary = info['summary'][:150] + "..." if len(info['summary']) > 150 else info['summary']
                summary_lines.append(f"   📝 {summary}")
            
            # Add key facts
            if info.get('key_facts'):
                for fact in info['key_facts'][:2]:
                    if fact:
                        summary_lines.append(f"   • {fact}")
            
            summary_lines.append("")  # Empty line between entries
        
        return "\n".join(summary_lines)
    
    def _prepare_suggestions_text(self, suggestions: List[Dict[str, str]]) -> str:
        """Prepare suggestions text"""
        if not suggestions:
            return "추가 제안사항 없음"
        
        suggestion_lines = []
        for idx, suggestion in enumerate(suggestions[:3], 1):
            suggestion_lines.append(f"{idx}. {suggestion['suggestion']}")
            if suggestion.get('example'):
                suggestion_lines.append(f"   예시: {suggestion['example']}")
        
        return "\n".join(suggestion_lines)
    
    def _generate_references(self, relevant_info: List[Dict[str, Any]]) -> str:
        """Generate detailed references section with URLs and dates"""
        references = []
        for idx, info in enumerate(relevant_info[:10], 1):  # Show up to 10 references
            # Add title
            references.append(f"\n{idx}. {info['title']}")
            
            # Add URL (always show full URL for transparency)
            if info.get('url'):
                url = info['url']
                # Ensure URL is clickable
                if url.startswith('http'):
                    references.append(f"   🔗 URL: {url}")
                else:
                    references.append(f"   🔗 URL: {url} (상대 경로)")
            
            # Add content date if available
            if info.get('content_date'):
                references.append(f"   📅 게시일: {info['content_date']}")
            elif info.get('retrieved_at'):
                references.append(f"   📅 검색일: {info['retrieved_at'][:10]}")
            
            # Add summary if available
            if info.get('summary'):
                summary = info['summary'][:250] + "..." if len(info['summary']) > 250 else info['summary']
                references.append(f"   📝 요약: {summary}")
            
            # Add key facts if available
            if info.get('key_facts') and info['key_facts']:
                references.append(f"   💡 주요 정보:")
                for fact in info['key_facts'][:3]:
                    if fact:  # Check if fact is not empty
                        references.append(f"      • {fact}")
            
            # Add relevance and recency indicators
            if info.get('relevance'):
                references.append(f"   📊 관련도: {info['relevance']:.0%}")
            
            # Mark if recent
            if info.get('is_recent'):
                references.append(f"   ✨ 최신 정보")
        
        return "\n".join(references)
    
    def _extract_suggestions(self, enrichment_data: Dict[str, Any]) -> List[str]:
        """Extract suggestions for the response"""
        suggestions = []
        
        if enrichment_data and enrichment_data.get('enrichment_suggestions'):
            for suggestion in enrichment_data['enrichment_suggestions'][:3]:
                suggestions.append(suggestion.get('suggestion', ''))
        
        return [s for s in suggestions if s]  # Filter out empty suggestions