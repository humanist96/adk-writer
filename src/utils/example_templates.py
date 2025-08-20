"""
Example templates optimized for KOSCOM Financial Sales Department
Includes Context7 patterns and Sequential thinking techniques
"""

from typing import Dict, List, Any
import random

class ExampleTemplates:
    """Advanced example templates with Context7 and Sequential thinking"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
        self.context7_patterns = self._initialize_context7_patterns()
        self.sequential_templates = self._initialize_sequential_templates()
    
    def _initialize_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize KOSCOM-optimized example templates"""
        return {
            "email": [
                {
                    "title": "🎯 프리미엄 자산관리 서비스 안내",
                    "category": "VIP 고객 대상",
                    "requirements": "고액 자산가를 위한 프리미엄 자산관리 서비스 안내 이메일을 작성해주세요. VIP 고객 대상으로 전문적이면서도 품격있는 톤으로 작성하고, 맞춤형 포트폴리오 관리와 세무 자문 서비스를 강조해주세요.",
                    "recipient": "김철수 대표님",
                    "subject": "코스콤 프리미엄 자산관리 서비스 특별 안내",
                    "additional_context": "최소 가입 금액 10억원, 전담 PB 배정, 분기별 자산 리포트 제공, 세무/법무 자문 포함",
                    "tone": "professional_premium",
                    "length": "medium"
                },
                {
                    "title": "📈 신규 금융상품 출시 안내",
                    "category": "일반 고객 대상",
                    "requirements": "2024년 하반기 출시 예정인 AI 기반 로보어드바이저 펀드 상품을 소개하는 이메일을 작성해주세요. 기술적 우위와 수익률 전망을 균형있게 설명하고, 리스크 관리 방안도 포함해주세요.",
                    "recipient": "투자자 고객님",
                    "subject": "AI가 운용하는 차세대 투자 솔루션 출시",
                    "additional_context": "연 목표 수익률 8-12%, 최소 투자금액 1천만원, 중위험 중수익 상품, 언제든 환매 가능",
                    "tone": "professional",
                    "length": "long"
                },
                {
                    "title": "🔔 시장 긴급 공지",
                    "category": "긴급 안내",
                    "requirements": "금융시장 변동성 확대에 따른 긴급 투자 전략 안내 이메일을 작성해주세요. 간결하고 명확하게 핵심 메시지를 전달하고, 즉각적인 행동 지침을 포함해주세요.",
                    "recipient": "전체 고객",
                    "subject": "[긴급] 시장 변동성 대응 전략 안내",
                    "additional_context": "24시간 핫라인 운영, 긴급 상담 예약 가능, 포트폴리오 재조정 권고",
                    "tone": "urgent",
                    "length": "short"
                },
                {
                    "title": "🤝 파트너십 제안",
                    "category": "B2B 제안",
                    "requirements": "증권사와의 전략적 파트너십을 제안하는 공식 이메일을 작성해주세요. 코스콤의 기술력과 시너지 효과를 강조하고, 구체적인 협력 방안을 제시해주세요.",
                    "recipient": "○○증권 대표이사",
                    "subject": "코스콤-○○증권 전략적 파트너십 제안",
                    "additional_context": "API 연동, 공동 상품 개발, 수수료 분배 구조, 파일럿 프로젝트 제안",
                    "tone": "formal",
                    "length": "long"
                }
            ],
            "proposal": [
                {
                    "title": "💼 M&A 자문 서비스 제안서",
                    "category": "기업 금융",
                    "requirements": "중견기업 M&A 자문 서비스 제안서를 작성해주세요. 코스콤의 전문성과 성공 사례를 포함하고, 단계별 프로세스와 예상 일정을 명확히 제시해주세요.",
                    "recipient": "○○그룹 전략기획실",
                    "subject": "M&A 자문 서비스 제안",
                    "additional_context": "딜 규모 500-1000억원, 6개월 프로젝트, 성공 수수료 기반, 실사 지원 포함",
                    "tone": "professional",
                    "length": "long"
                },
                {
                    "title": "🏢 기업연금 운용 제안서",
                    "category": "퇴직연금",
                    "requirements": "대기업 임직원을 위한 DB/DC형 기업연금 운용 제안서를 작성해주세요. 안정성과 수익성의 균형을 강조하고, 맞춤형 포트폴리오 구성안을 포함해주세요.",
                    "recipient": "○○전자 인사팀",
                    "subject": "임직원 퇴직연금 운용 제안",
                    "additional_context": "임직원 5,000명, 연간 적립금 1,000억원, 원금보장형 40% + 실적배당형 60%",
                    "tone": "professional",
                    "length": "medium"
                },
                {
                    "title": "🌐 해외투자 상품 제안서",
                    "category": "글로벌 투자",
                    "requirements": "미국 기술주 중심의 해외투자 상품 제안서를 작성해주세요. 환헤지 전략과 세금 최적화 방안을 포함하고, 최근 시장 동향을 반영해주세요.",
                    "recipient": "프라이빗 뱅킹 고객",
                    "subject": "글로벌 테크 리더스 펀드 제안",
                    "additional_context": "NASDAQ 상위 10개 종목, 부분 환헤지(50%), 분기 배당, 3년 목표 수익률 연 15%",
                    "tone": "sophisticated",
                    "length": "long"
                }
            ],
            "report": [
                {
                    "title": "📊 분기 실적 보고서",
                    "category": "정기 보고",
                    "requirements": "2024년 3분기 포트폴리오 운용 실적 보고서를 작성해주세요. 수익률 분석, 리스크 지표, 향후 전망을 체계적으로 정리하고, 시각적 요소를 고려한 구성으로 작성해주세요.",
                    "recipient": "투자심의위원회",
                    "subject": "2024년 3분기 운용실적 보고",
                    "additional_context": "누적 수익률 12.5%, 샤프지수 1.8, 최대낙폭 -5.2%, 벤치마크 대비 +3.2%p 초과",
                    "tone": "analytical",
                    "length": "long"
                },
                {
                    "title": "⚖️ 컴플라이언스 보고서",
                    "category": "규정 준수",
                    "requirements": "금융감독원 제출용 내부통제 현황 보고서를 작성해주세요. 규정 준수 현황, 내부 감사 결과, 개선 조치 계획을 포함하여 공식적인 형식으로 작성해주세요.",
                    "recipient": "금융감독원",
                    "subject": "2024년 내부통제 현황 보고",
                    "additional_context": "점검 항목 150개, 준수율 98.5%, 개선 필요 사항 3건, 조치 완료 예정일 명시",
                    "tone": "formal",
                    "length": "long"
                },
                {
                    "title": "💡 시장 분석 리포트",
                    "category": "리서치",
                    "requirements": "2025년 국내 증시 전망 리포트를 작성해주세요. 거시경제 지표, 섹터별 분석, 투자 전략을 포함하고, 리스크 요인도 균형있게 다뤄주세요.",
                    "recipient": "기관투자자",
                    "subject": "2025년 한국 증시 전망",
                    "additional_context": "KOSPI 목표 3,200pt, GDP 성장률 2.3%, 금리 인하 2회 예상, IT/바이오 섹터 주목",
                    "tone": "analytical",
                    "length": "long"
                }
            ],
            "official": [
                {
                    "title": "📜 공식 계약서",
                    "category": "법적 문서",
                    "requirements": "투자일임계약서 초안을 작성해주세요. 법적 요건을 충족하고, 양 당사자의 권리와 의무를 명확히 명시해주세요.",
                    "recipient": "계약 당사자",
                    "subject": "투자일임계약서",
                    "additional_context": "계약금액 50억원, 계약기간 3년, 성과보수 체계, 중도해지 조항 포함",
                    "tone": "legal",
                    "length": "long"
                },
                {
                    "title": "🎖️ 시상식 축사",
                    "category": "대외 행사",
                    "requirements": "금융투자 대상 시상식 축사를 작성해주세요. 업계 발전에 대한 비전과 수상자에 대한 축하를 담아 격조있게 작성해주세요.",
                    "recipient": "시상식 참석자",
                    "subject": "2024 대한민국 금융투자대상 축사",
                    "additional_context": "코스콤 대표이사 명의, 5분 분량, 디지털 금융 혁신 강조, 미래 비전 제시",
                    "tone": "ceremonial",
                    "length": "medium"
                }
            ]
        }
    
    def _initialize_context7_patterns(self) -> Dict[str, str]:
        """Initialize Context7 documentation patterns for enhanced prompts"""
        return {
            "structure": """
[Context7 문서 구조 패턴]
1. 목적과 배경 (Purpose & Background)
   - 명확한 목표 설정
   - 비즈니스 컨텍스트 제공
   
2. 핵심 메시지 (Key Messages)
   - 3-5개의 주요 포인트
   - 우선순위별 정렬
   
3. 근거와 데이터 (Evidence & Data)
   - 정량적 지표 제시
   - 신뢰할 수 있는 출처 인용
   
4. 행동 촉구 (Call to Action)
   - 구체적인 다음 단계
   - 명확한 기한과 담당자
""",
            "financial_terminology": """
[금융 전문 용어 Context7 패턴]
- 수익률 (Return): YTD, CAGR, IRR 명시
- 리스크 (Risk): VaR, 샤프지수, 변동성 지표
- 포트폴리오 (Portfolio): 자산배분, 리밸런싱, 분산투자
- 규제 (Regulation): Basel III, IFRS, 자본적정성
- 시장 (Market): 벤치마크, 알파, 베타
""",
            "compliance": """
[규정 준수 Context7 체크리스트]
□ 금융투자업규정 준수
□ 개인정보보호 조항 포함
□ 리스크 고지 의무 이행
□ 이해상충 방지 명시
□ 적합성/적정성 원칙 준수
""",
            "tone_guide": """
[톤앤매너 Context7 가이드]
- Professional: 전문적이고 신뢰감 있는 어조
- Premium: 품격있고 차별화된 표현
- Urgent: 즉각적이고 명확한 메시지
- Analytical: 객관적이고 데이터 기반
- Formal: 공식적이고 격식있는 문체
"""
        }
    
    def _initialize_sequential_templates(self) -> Dict[str, List[str]]:
        """Initialize Sequential thinking templates for structured prompts"""
        return {
            "analysis_sequence": [
                "1. 현황 분석 (Current State Analysis)",
                "2. 문제점 도출 (Problem Identification)",
                "3. 해결방안 제시 (Solution Proposal)",
                "4. 실행 계획 (Implementation Plan)",
                "5. 예상 효과 (Expected Outcomes)",
                "6. 리스크 관리 (Risk Management)"
            ],
            "sales_sequence": [
                "1. 고객 니즈 파악 (Customer Needs)",
                "2. 상품 매칭 (Product Matching)",
                "3. 가치 제안 (Value Proposition)",
                "4. 차별화 포인트 (Differentiation)",
                "5. 반론 처리 (Objection Handling)",
                "6. 클로징 (Closing)"
            ],
            "investment_sequence": [
                "1. 시장 환경 분석 (Market Analysis)",
                "2. 투자 기회 발굴 (Opportunity Discovery)",
                "3. 리스크 평가 (Risk Assessment)",
                "4. 포트폴리오 구성 (Portfolio Construction)",
                "5. 모니터링 계획 (Monitoring Plan)",
                "6. 출구 전략 (Exit Strategy)"
            ],
            "compliance_sequence": [
                "1. 규정 검토 (Regulation Review)",
                "2. 현재 상태 점검 (Current Status Check)",
                "3. 갭 분석 (Gap Analysis)",
                "4. 개선 방안 (Improvement Measures)",
                "5. 이행 계획 (Implementation Timeline)",
                "6. 모니터링 체계 (Monitoring System)"
            ]
        }
    
    def get_random_example(self, doc_type: str = None) -> Dict[str, Any]:
        """Get a random example for the specified document type"""
        if doc_type and doc_type in self.templates:
            examples = self.templates[doc_type]
        else:
            # Get from all categories
            all_examples = []
            for examples_list in self.templates.values():
                all_examples.extend(examples_list)
            examples = all_examples
        
        if examples:
            return random.choice(examples)
        return {}
    
    def get_examples_by_category(self, doc_type: str) -> List[Dict[str, Any]]:
        """Get all examples for a specific document type"""
        return self.templates.get(doc_type, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available document categories"""
        return list(self.templates.keys())
    
    def apply_context7_pattern(self, example: Dict[str, Any], pattern_type: str = "structure") -> str:
        """Apply Context7 pattern to enhance the example"""
        base_requirements = example.get("requirements", "")
        context7_pattern = self.context7_patterns.get(pattern_type, "")
        
        enhanced_prompt = f"""
{base_requirements}

{context7_pattern}

[추가 컨텍스트]
- 수신자: {example.get('recipient', '')}
- 제목: {example.get('subject', '')}
- 상세 정보: {example.get('additional_context', '')}
- 문서 길이: {example.get('length', 'medium')}
"""
        return enhanced_prompt
    
    def apply_sequential_thinking(self, example: Dict[str, Any], sequence_type: str = "analysis_sequence") -> str:
        """Apply Sequential thinking to structure the prompt"""
        base_requirements = example.get("requirements", "")
        sequence = self.sequential_templates.get(sequence_type, [])
        
        enhanced_prompt = f"""
{base_requirements}

[Sequential Thinking Framework]
다음 순서에 따라 체계적으로 작성해주세요:
"""
        for step in sequence:
            enhanced_prompt += f"\n{step}"
        
        enhanced_prompt += f"""

[문서 세부사항]
- 수신자: {example.get('recipient', '')}
- 제목: {example.get('subject', '')}
- 추가 정보: {example.get('additional_context', '')}
- 톤앤매너: {example.get('tone', 'professional')}
- 길이: {example.get('length', 'medium')}
"""
        return enhanced_prompt
    
    def generate_advanced_prompt(self, example: Dict[str, Any], 
                                use_context7: bool = True,
                                use_sequential: bool = True,
                                length_preference: str = "medium") -> str:
        """Generate an advanced prompt with Context7 and Sequential thinking"""
        prompt = f"""
[코스콤 금융영업부 전문 문서 작성 요청]

📋 문서 유형: {example.get('title', '')}
🏷️ 카테고리: {example.get('category', '')}
"""
        
        # Add base requirements
        prompt += f"\n\n[핵심 요구사항]\n{example.get('requirements', '')}"
        
        # Apply Context7 if requested
        if use_context7:
            prompt += "\n\n" + self.context7_patterns.get("structure", "")
            prompt += "\n\n" + self.context7_patterns.get("financial_terminology", "")
        
        # Apply Sequential thinking if requested
        if use_sequential:
            # Determine appropriate sequence based on document type
            if "투자" in example.get('title', '') or "포트폴리오" in example.get('title', ''):
                sequence_type = "investment_sequence"
            elif "영업" in example.get('title', '') or "제안" in example.get('title', ''):
                sequence_type = "sales_sequence"
            elif "규정" in example.get('title', '') or "컴플라이언스" in example.get('title', ''):
                sequence_type = "compliance_sequence"
            else:
                sequence_type = "analysis_sequence"
            
            prompt += "\n\n[Sequential Thinking Framework]"
            for step in self.sequential_templates[sequence_type]:
                prompt += f"\n{step}"
        
        # Add document details
        prompt += f"""

[문서 상세 정보]
📨 수신자: {example.get('recipient', '')}
📌 제목: {example.get('subject', '')}
📝 추가 컨텍스트: {example.get('additional_context', '')}
🎯 톤앤매너: {example.get('tone', 'professional')}
📏 문서 길이: {length_preference}

[작성 지침]
1. 코스콤 금융영업부의 전문성을 반영
2. 금융 규정 및 컴플라이언스 준수
3. 명확하고 설득력 있는 메시지 전달
4. 데이터와 근거 기반의 내용 구성
5. 실행 가능한 구체적 제안 포함
"""
        
        # Add length-specific instructions
        if length_preference == "short":
            prompt += "\n\n⚡ 간결하고 핵심적인 내용으로 1-2단락 이내로 작성"
        elif length_preference == "long":
            prompt += "\n\n📚 상세하고 종합적인 내용으로 5-7단락 이상 작성"
        else:
            prompt += "\n\n📄 적절한 길이로 3-4단락 정도로 작성"
        
        return prompt
    
    def get_length_options(self) -> List[str]:
        """Get available length options"""
        return ["short", "medium", "long"]
    
    def get_tone_options(self) -> List[str]:
        """Get available tone options"""
        return [
            "professional",
            "professional_premium",
            "formal",
            "urgent",
            "analytical",
            "sophisticated",
            "ceremonial",
            "legal"
        ]