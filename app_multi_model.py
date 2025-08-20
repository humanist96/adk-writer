"""
Multi-Model AI Financial Writer Pro - Streamlit Cloud Version
Supports Anthropic Claude, OpenAI GPT, and Google Gemini
"""

import streamlit as st
from typing import Dict, Any
import json
from datetime import datetime
from pathlib import Path
import time

# Try cloud config first, fallback to local
try:
    from src.config_cloud import config
except:
    from src.config import config

from src.agents.multi_model_agents import (
    ModelFactory,
    MultiModelAgent,
    MultiModelAgentResponse
)
from src.agents.loop_agent import LoopAgent
from src.tools.custom_tools import (
    validate_financial_terms,
    check_compliance,
    calculate_quality_score
)

# Configure page
st.set_page_config(
    page_title="AI Financial Writer Pro - Multi Model",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .model-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 2px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .model-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    
    .provider-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    
    .anthropic-badge {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        color: white;
    }
    
    .openai-badge {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        color: white;
    }
    
    .google-badge {
        background: linear-gradient(135deg, #4285f4 0%, #34a853 100%);
        color: white;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .comparison-panel {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
</style>
""", unsafe_allow_html=True)

class MultiModelFinancialWritingApp:
    """Multi-Model Financial Writing AI Application"""
    
    def __init__(self):
        self.config = config
        self.multi_model_agent = None
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'history' not in st.session_state:
            st.session_state.history = []
        if 'current_result' not in st.session_state:
            st.session_state.current_result = None
        if 'stats' not in st.session_state:
            st.session_state.stats = {
                'total_documents': 0,
                'avg_quality': 0,
                'avg_iterations': 0,
                'total_time': 0,
                'models_used': {}
            }
        if 'selected_provider' not in st.session_state:
            st.session_state.selected_provider = config.DEFAULT_PROVIDER
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = None
    
    def render_header(self):
        """Render header"""
        st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.5rem;">🤖 AI Financial Writer Pro - Multi Model</h1>
            <p style="margin-top: 0.5rem; opacity: 0.9;">
                차세대 금융 문서 작성 AI | Anthropic Claude • OpenAI GPT • Google Gemini
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_model_selector(self):
        """Render model selection UI"""
        st.markdown("## 🎯 AI 모델 선택")
        
        # Get available models
        available_models = ModelFactory.get_available_models()
        
        # Provider selection
        col1, col2, col3 = st.columns(3)
        
        providers_available = []
        
        with col1:
            if config.ANTHROPIC_API_KEY:
                providers_available.append("Anthropic")
                if st.button("🔴 Anthropic Claude", type="secondary" if st.session_state.selected_provider != "Anthropic" else "primary"):
                    st.session_state.selected_provider = "Anthropic"
                    st.rerun()
        
        with col2:
            if config.OPENAI_API_KEY:
                providers_available.append("OpenAI")
                if st.button("🔵 OpenAI GPT", type="secondary" if st.session_state.selected_provider != "OpenAI" else "primary"):
                    st.session_state.selected_provider = "OpenAI"
                    st.rerun()
        
        with col3:
            if config.GOOGLE_API_KEY:
                providers_available.append("Google")
                if st.button("🟢 Google Gemini", type="secondary" if st.session_state.selected_provider != "Google" else "primary"):
                    st.session_state.selected_provider = "Google"
                    st.rerun()
        
        # Model selection for current provider
        if st.session_state.selected_provider and st.session_state.selected_provider in available_models:
            st.markdown(f"### 모델 선택: {st.session_state.selected_provider}")
            
            models = available_models[st.session_state.selected_provider]
            
            # Create model cards
            cols = st.columns(2)
            for idx, (model_id, model_name) in enumerate(models.items()):
                with cols[idx % 2]:
                    if st.button(
                        f"{model_name}",
                        key=f"model_{model_id}",
                        help=f"모델 ID: {model_id}"
                    ):
                        st.session_state.selected_model = model_id
                        st.success(f"✅ {model_name} 선택됨")
            
            # Show current selection
            if st.session_state.selected_model:
                st.info(f"현재 선택된 모델: **{models.get(st.session_state.selected_model, st.session_state.selected_model)}**")
        
        return providers_available
    
    def render_stats(self):
        """Render statistics"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "총 생성 문서",
                st.session_state.stats['total_documents'],
                "+1" if st.session_state.stats['total_documents'] > 0 else None
            )
        
        with col2:
            st.metric(
                "평균 품질",
                f"{st.session_state.stats['avg_quality']:.1%}",
                f"+{(st.session_state.stats['avg_quality'] - 0.7) * 100:.0f}%" if st.session_state.stats['avg_quality'] > 0 else None
            )
        
        with col3:
            st.metric(
                "평균 반복",
                f"{st.session_state.stats['avg_iterations']:.1f}회",
                None
            )
        
        with col4:
            # Show most used model
            if st.session_state.stats['models_used']:
                most_used = max(st.session_state.stats['models_used'].items(), key=lambda x: x[1])
                st.metric(
                    "주로 사용된 모델",
                    most_used[0],
                    f"{most_used[1]}회 사용"
                )
            else:
                st.metric("주로 사용된 모델", "-", None)
    
    def process_document(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process document through the pipeline"""
        try:
            # Initialize multi-model agent if not already done
            if not self.multi_model_agent:
                agent_config = config.get_agent_config()
                self.multi_model_agent = MultiModelAgent(agent_config)
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Get selected provider and model
            provider = st.session_state.selected_provider
            model = st.session_state.selected_model
            
            if model:
                # Update config with selected model
                if provider == "Anthropic":
                    self.multi_model_agent.config['anthropic_model'] = model
                elif provider == "OpenAI":
                    self.multi_model_agent.config['openai_model'] = model
                elif provider == "Google":
                    self.multi_model_agent.config['google_model'] = model
            
            # Generate document using multi-model agent
            status_text.text(f"모델 준비 중... ({provider})")
            progress_bar.progress(20)
            
            # Create prompt for document generation
            prompt = self._create_prompt(input_data)
            
            status_text.text(f"문서 생성 중... ({provider})")
            progress_bar.progress(50)
            
            # Generate response
            response = self.multi_model_agent.generate(
                prompt,
                provider=provider,
                temperature=input_data.get('temperature', 0.7),
                max_tokens=input_data.get('max_tokens', 2048)
            )
            
            progress_bar.progress(80)
            status_text.text("품질 검증 중...")
            
            # Validation
            final_doc = response.content
            term_validation = validate_financial_terms(final_doc)
            compliance_check = check_compliance(final_doc, input_data.get("document_type", "email"))
            final_score = calculate_quality_score(final_doc, term_validation, compliance_check)
            
            progress_bar.progress(100)
            status_text.text("완료!")
            
            # Update model usage stats
            model_key = f"{provider} - {response.model_used}"
            if model_key not in st.session_state.stats['models_used']:
                st.session_state.stats['models_used'][model_key] = 0
            st.session_state.stats['models_used'][model_key] += 1
            
            result = {
                "success": True,
                "final_document": final_doc,
                "quality_score": final_score,
                "iterations": 1,
                "total_time": 5.0,
                "provider": provider,
                "model_used": response.model_used,
                "validation": {
                    "terms": term_validation,
                    "compliance": compliance_check,
                    "final_score": final_score
                }
            }
            
            # Update stats
            self._update_stats(result)
            
            return result
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _create_prompt(self, input_data: Dict[str, Any]) -> str:
        """Create prompt for document generation"""
        doc_type = config.DOCUMENT_TYPES.get(input_data['document_type'], input_data['document_type'])
        
        prompt = f"""당신은 전문적인 금융 문서 작성 AI입니다.
        
다음 요구사항에 맞는 {doc_type}을(를) 작성해주세요:

요구사항: {input_data['requirements']}
톤앤매너: {input_data['tone']}
"""
        
        if input_data.get('recipient'):
            prompt += f"\n수신자: {input_data['recipient']}"
        
        if input_data.get('subject'):
            prompt += f"\n제목: {input_data['subject']}"
        
        if input_data.get('additional_context'):
            prompt += f"\n추가 컨텍스트: {input_data['additional_context']}"
        
        prompt += """

다음 기준을 충족하는 전문적이고 정확한 문서를 작성해주세요:
1. 금융 전문 용어를 정확하게 사용
2. 규정 준수 및 법적 요구사항 충족
3. 명확하고 간결한 문장 구성
4. 적절한 구조와 형식
5. 전문적이면서도 이해하기 쉬운 표현
"""
        
        return prompt
    
    def _update_stats(self, result: Dict[str, Any]):
        """Update statistics"""
        stats = st.session_state.stats
        stats['total_documents'] += 1
        
        current_quality = result.get('quality_score', 0)
        stats['avg_quality'] = (
            (stats['avg_quality'] * (stats['total_documents'] - 1) + current_quality) 
            / stats['total_documents']
        )
        
        current_iter = result.get('iterations', 0)
        stats['avg_iterations'] = (
            (stats['avg_iterations'] * (stats['total_documents'] - 1) + current_iter)
            / stats['total_documents']
        )
        
        stats['total_time'] += result.get('total_time', 0)
    
    def run(self):
        """Run the application"""
        # Header
        self.render_header()
        
        # Model selector
        providers_available = self.render_model_selector()
        
        if not providers_available:
            st.error("⚠️ API 키가 설정되지 않았습니다. Streamlit secrets 또는 환경 변수를 확인해주세요.")
            st.stop()
        
        st.divider()
        
        # Stats
        self.render_stats()
        
        # Sidebar
        with st.sidebar:
            st.markdown("## ⚙️ 설정")
            
            # Model settings
            st.markdown("### 🤖 모델 설정")
            
            temperature = st.slider(
                "Temperature (창의성)",
                min_value=0.0,
                max_value=1.0,
                value=config.TEMPERATURE,
                step=0.1,
                help="낮을수록 일관성 있고, 높을수록 창의적입니다"
            )
            
            max_tokens = st.number_input(
                "최대 토큰 수",
                min_value=500,
                max_value=4000,
                value=config.MAX_OUTPUT_TOKENS,
                step=100
            )
            
            st.divider()
            
            # Document settings
            st.markdown("### 📄 문서 설정")
            
            doc_type = st.selectbox(
                "문서 유형",
                options=list(config.DOCUMENT_TYPES.keys()),
                format_func=lambda x: config.DOCUMENT_TYPES[x]
            )
            
            tone = st.select_slider(
                "톤앤매너",
                options=["formal", "professional", "professional_friendly", "friendly"],
                value="professional",
                format_func=lambda x: {
                    "formal": "격식있는",
                    "professional": "전문적인",
                    "professional_friendly": "전문적이면서 친근한",
                    "friendly": "친근한"
                }.get(x, x)
            )
            
            st.divider()
            
            with st.expander("🎨 모델별 특징"):
                st.markdown("""
                **Anthropic Claude**
                - 긴 컨텍스트 처리 우수
                - 논리적이고 체계적인 작성
                - 복잡한 분석에 강점
                
                **OpenAI GPT**
                - 범용성과 균형잡힌 성능
                - 창의적인 작성에 강점
                - 다양한 스타일 지원
                
                **Google Gemini**
                - 빠른 응답 속도
                - 효율적인 처리
                - 멀티모달 지원
                """)
            
            st.divider()
            
            if st.button("🔄 초기화"):
                st.session_state.history = []
                st.session_state.current_result = None
                st.rerun()
        
        # Main content
        tab1, tab2, tab3, tab4 = st.tabs(["✍️ 문서 작성", "🔍 모델 비교", "📊 비교 분석", "📚 이력"])
        
        with tab1:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📝 문서 요구사항")
                
                requirements = st.text_area(
                    "요구사항",
                    placeholder="작성하고자 하는 문서의 내용과 요구사항을 입력하세요...",
                    height=200,
                    label_visibility="collapsed"
                )
                
                with st.expander("추가 정보"):
                    recipient = st.text_input("수신자")
                    subject = st.text_input("제목")
                    additional_context = st.text_area("추가 컨텍스트", height=100)
                
                if st.button("🚀 문서 생성", type="primary"):
                    if requirements:
                        if not st.session_state.selected_model:
                            st.warning("먼저 AI 모델을 선택해주세요.")
                        else:
                            input_data = {
                                "document_type": doc_type,
                                "requirements": requirements,
                                "tone": tone,
                                "recipient": recipient,
                                "subject": subject,
                                "additional_context": additional_context,
                                "temperature": temperature,
                                "max_tokens": max_tokens
                            }
                            
                            with st.spinner(f"{st.session_state.selected_provider} AI가 문서를 작성 중입니다..."):
                                result = self.process_document(input_data)
                            
                            st.session_state.current_result = result
                            st.session_state.history.append({
                                "timestamp": datetime.now().isoformat(),
                                "input": input_data,
                                "result": result
                            })
                            
                            if result.get("success"):
                                st.success(f"✅ 문서 생성 완료! (모델: {result.get('model_used', 'Unknown')})")
                                st.balloons()
                            else:
                                st.error(f"❌ 오류: {result.get('error')}")
                    else:
                        st.warning("요구사항을 입력해주세요.")
            
            with col2:
                st.markdown("### 📄 생성된 문서")
                
                if st.session_state.current_result and st.session_state.current_result.get("success"):
                    result = st.session_state.current_result
                    
                    # Show model info
                    st.markdown(f"**사용된 모델**: {result.get('provider', 'Unknown')} - {result.get('model_used', 'Unknown')}")
                    
                    st.text_area(
                        "최종 문서",
                        value=result.get("final_document", ""),
                        height=350,
                        label_visibility="collapsed"
                    )
                    
                    col2_1, col2_2, col2_3 = st.columns(3)
                    with col2_1:
                        st.metric("품질 점수", f"{result.get('quality_score', 0):.1%}")
                    with col2_2:
                        st.metric("처리 시간", f"{result.get('total_time', 0):.1f}초")
                    with col2_3:
                        st.metric("모델", result.get('provider', '-'))
                    
                    st.download_button(
                        label="📥 문서 다운로드",
                        data=result["final_document"],
                        file_name=f"document_{result.get('provider', 'ai')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.info("문서를 생성하려면 왼쪽에서 요구사항을 입력하고 '문서 생성' 버튼을 클릭하세요.")
        
        with tab2:
            st.markdown("### 🔍 여러 모델 비교")
            st.info("동일한 요구사항으로 여러 AI 모델의 결과를 비교해보세요.")
            
            compare_requirements = st.text_area(
                "비교할 문서 요구사항",
                placeholder="모든 모델에서 테스트할 요구사항을 입력하세요...",
                height=150
            )
            
            if st.button("🔬 모든 모델로 생성", type="primary"):
                if compare_requirements:
                    if not self.multi_model_agent:
                        agent_config = config.get_agent_config()
                        self.multi_model_agent = MultiModelAgent(agent_config)
                    
                    # Create input data
                    input_data = {
                        "document_type": doc_type,
                        "requirements": compare_requirements,
                        "tone": tone,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    
                    prompt = self._create_prompt(input_data)
                    
                    # Compare across all available providers
                    with st.spinner("모든 모델로 문서를 생성 중입니다..."):
                        results = self.multi_model_agent.compare_models(prompt)
                    
                    # Display results
                    for provider, response in results.items():
                        with st.expander(f"{provider} - {response.model_used}"):
                            st.text_area(
                                f"{provider} 결과",
                                value=response.content,
                                height=300,
                                label_visibility="collapsed"
                            )
                            
                            # Calculate quality score
                            term_validation = validate_financial_terms(response.content)
                            compliance_check = check_compliance(response.content, doc_type)
                            quality_score = calculate_quality_score(response.content, term_validation, compliance_check)
                            
                            st.metric("품질 점수", f"{quality_score:.1%}")
                else:
                    st.warning("비교할 요구사항을 입력해주세요.")
        
        with tab3:
            if st.session_state.current_result and st.session_state.current_result.get("success"):
                result = st.session_state.current_result
                
                st.markdown("### 📊 문서 분석")
                
                # Quality metrics
                st.markdown("#### 품질 지표")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("전체 품질", f"{result.get('quality_score', 0):.1%}")
                
                with col2:
                    validation = result.get('validation', {})
                    st.metric("용어 정확도", f"{validation.get('terms', {}).get('score', 0):.1%}")
                
                with col3:
                    st.metric("규정 준수", "✅ 준수" if validation.get('compliance', {}).get('is_compliant') else "❌ 미준수")
                
                with col4:
                    st.metric("사용 모델", result.get('provider', '-'))
                
                # Document stats
                st.markdown("#### 문서 통계")
                doc = result.get('final_document', '')
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("문자 수", f"{len(doc):,}")
                with col2:
                    st.metric("단어 수", f"{len(doc.split()):,}")
                with col3:
                    st.metric("문장 수", f"{doc.count('.') + doc.count('!') + doc.count('?'):,}")
            else:
                st.info("먼저 문서를 생성해주세요.")
        
        with tab4:
            if st.session_state.history:
                st.markdown("### 📚 문서 생성 이력")
                
                for idx, item in enumerate(reversed(st.session_state.history), 1):
                    timestamp = datetime.fromisoformat(item['timestamp'])
                    result = item['result']
                    
                    with st.expander(
                        f"문서 #{len(st.session_state.history) - idx + 1} - "
                        f"{timestamp.strftime('%Y-%m-%d %H:%M')} - "
                        f"{result.get('provider', 'Unknown')}"
                    ):
                        st.write(f"**문서 유형**: {item['input']['document_type']}")
                        st.write(f"**톤**: {item['input']['tone']}")
                        st.write(f"**모델**: {result.get('provider', '-')} - {result.get('model_used', '-')}")
                        st.write(f"**품질 점수**: {result.get('quality_score', 0):.1%}")
                        st.write(f"**처리 시간**: {result.get('total_time', 0):.1f}초")
                        
                        if result.get('success'):
                            st.text_area(
                                "문서 내용",
                                value=result.get('final_document', ''),
                                height=200,
                                label_visibility="collapsed"
                            )
            else:
                st.info("아직 생성된 문서가 없습니다.")


def main():
    """Main entry point"""
    app = MultiModelFinancialWritingApp()
    app.run()


if __name__ == "__main__":
    main()