"""
Multi-Model AI Financial Writer Pro - Streamlit Cloud Version
Supports Anthropic Claude, OpenAI GPT, and Google Gemini
"""

import streamlit as st
from typing import Dict, Any, Optional
import json
from datetime import datetime
from pathlib import Path
import time
from loguru import logger

# Page configuration
st.set_page_config(
    page_title="AI Financial Writer Pro - Multi Model",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
from src.utils.diff_utils import (
    create_diff_html,
    create_word_diff,
    extract_modifications,
    create_modification_summary,
    get_change_statistics,
    calculate_similarity
)
from src.database import get_db_manager
from src.utils.example_templates import ExampleTemplates

# Custom CSS for modern UI
st.markdown("""
<style>
    /* Main App Styling */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        animation: slideDown 0.5s ease-out;
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Card Styling */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.8);
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* Model Selection Cards */
    .model-selector {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .model-selector:hover {
        border-color: #667eea;
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
    }
    
    .model-selector.selected {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
    }
    
    /* Provider Badges */
    .provider-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
        transition: all 0.3s ease;
    }
    
    .provider-badge:hover {
        transform: scale(1.05);
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
    
    /* Metric Values */
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        background: white;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
        color: white;
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Text Area Styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Select Box Styling */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
</style>
""", unsafe_allow_html=True)

class MultiModelFinancialWritingApp:
    """Multi-Model Financial Writing AI Application"""
    
    def __init__(self):
        self.config = config
        self.multi_model_agent = None
        self.db = get_db_manager()  # Initialize database manager
        self.example_templates = ExampleTemplates()  # Initialize example templates
        self._initialize_session_state()
        self._load_statistics_from_db()
    
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
            st.session_state.selected_model = config.ANTHROPIC_MODEL if config.DEFAULT_PROVIDER == "Anthropic" else None
        if 'draft_document' not in st.session_state:
            st.session_state.draft_document = None
        if 'refinement_history' not in st.session_state:
            st.session_state.refinement_history = []
        if 'critique_history' not in st.session_state:
            st.session_state.critique_history = []
    
    def _load_statistics_from_db(self):
        """Load statistics from database"""
        try:
            db_stats = self.db.get_statistics(days=30)
            st.session_state.stats = {
                'total_documents': db_stats['total_documents'],
                'avg_quality': db_stats['avg_quality'],
                'avg_iterations': db_stats['avg_iterations'],
                'total_time': db_stats['total_time'],
                'models_used': db_stats.get('by_provider', {}),
                'daily_stats': db_stats.get('daily_stats', []),
                'by_document_type': db_stats.get('by_document_type', {})
            }
        except Exception as e:
            logger.warning(f"Could not load statistics from database: {str(e)}")
    
    def render_header(self):
        """Render animated header"""
        st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800;">
                🤖 AI Financial Writer Pro
            </h1>
            <p style="margin-top: 0.8rem; font-size: 1.2rem; opacity: 0.95;">
                차세대 금융 문서 작성 AI 플랫폼
            </p>
            <div style="margin-top: 1rem;">
                <span class="provider-badge anthropic-badge">Anthropic Claude</span>
                <span class="provider-badge openai-badge">OpenAI GPT</span>
                <span class="provider-badge google-badge">Google Gemini</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar_model_selector(self):
        """Render model selection in sidebar"""
        st.sidebar.markdown("## 🤖 AI 모델 설정")
        
        available_models = ModelFactory.get_available_models()
        providers_available = []
        
        # Check available providers
        if config.ANTHROPIC_API_KEY:
            providers_available.append("Anthropic")
        if config.OPENAI_API_KEY:
            providers_available.append("OpenAI")
        if config.GOOGLE_API_KEY:
            providers_available.append("Google")
        
        if not providers_available:
            st.sidebar.error("⚠️ API 키가 설정되지 않았습니다.")
            return providers_available
        
        # Provider selection
        st.sidebar.markdown("### 📦 AI 제공자")
        selected_provider = st.sidebar.radio(
            "제공자 선택",
            options=providers_available,
            index=providers_available.index(st.session_state.selected_provider) if st.session_state.selected_provider in providers_available else 0,
            label_visibility="collapsed",
            help="사용할 AI 제공자를 선택하세요"
        )
        
        if selected_provider != st.session_state.selected_provider:
            st.session_state.selected_provider = selected_provider
            st.session_state.selected_model = None
            st.rerun()
        
        # Model selection for current provider
        if selected_provider in available_models:
            st.sidebar.markdown("### 🎯 모델 선택")
            
            models = available_models[selected_provider]
            model_options = list(models.keys())
            model_labels = list(models.values())
            
            # Set default model index
            if st.session_state.selected_model and st.session_state.selected_model in model_options:
                default_index = model_options.index(st.session_state.selected_model)
            else:
                default_index = 0
                st.session_state.selected_model = model_options[0]
            
            selected_model = st.sidebar.selectbox(
                "모델",
                options=model_options,
                format_func=lambda x: models[x],
                index=default_index,
                label_visibility="collapsed",
                help="사용할 AI 모델을 선택하세요"
            )
            
            if selected_model != st.session_state.selected_model:
                st.session_state.selected_model = selected_model
            
            # Model features
            with st.sidebar.expander("🌟 모델 특징", expanded=False):
                if selected_provider == "Anthropic":
                    st.markdown("""
                    **Claude 특징:**
                    - 📚 긴 컨텍스트 처리 (200K 토큰)
                    - 🎯 높은 정확도와 일관성
                    - 💡 뛰어난 추론 능력
                    - 🔒 안전하고 신뢰할 수 있는 응답
                    """)
                elif selected_provider == "OpenAI":
                    st.markdown("""
                    **GPT 특징:**
                    - 🌍 다양한 언어 지원
                    - 🎨 창의적인 콘텐츠 생성
                    - 🔧 강력한 코드 생성
                    - 📊 데이터 분석 능력
                    """)
                elif selected_provider == "Google":
                    st.markdown("""
                    **Gemini 특징:**
                    - ⚡ 빠른 응답 속도
                    - 🖼️ 멀티모달 지원
                    - 💰 비용 효율적
                    - 🔄 실시간 업데이트
                    """)
        
        return providers_available
    
    def render_stats(self):
        """Render animated statistics"""
        st.markdown("### 📊 통계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric(
                "📄 총 생성 문서",
                st.session_state.stats['total_documents'],
                "+1" if st.session_state.stats['total_documents'] > 0 else None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            quality_value = st.session_state.stats['avg_quality']
            quality_delta = (quality_value - 0.7) * 100 if quality_value > 0 else 0
            st.metric(
                "⭐ 평균 품질",
                f"{quality_value:.1%}",
                f"+{quality_delta:.0f}%" if quality_delta > 0 else None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric(
                "🔄 평균 반복",
                f"{st.session_state.stats['avg_iterations']:.1f}회",
                None
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            if st.session_state.stats['models_used']:
                most_used = max(st.session_state.stats['models_used'].items(), key=lambda x: x[1])
                st.metric(
                    "🏆 주 사용 모델",
                    most_used[0].split(' - ')[0],
                    f"{most_used[1]}회"
                )
            else:
                st.metric("🏆 주 사용 모델", "-", None)
            st.markdown('</div>', unsafe_allow_html=True)
    
    def process_document(self, input_data: Dict[str, Any], is_refinement: bool = False, use_loop_agent: bool = True) -> Dict[str, Any]:
        """Process document through the pipeline with optional LoopAgent"""
        try:
            # Initialize multi-model agent if not already done
            if not self.multi_model_agent:
                agent_config = config.get_agent_config()
                self.multi_model_agent = MultiModelAgent(agent_config)
            
            # Show progress with animation
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
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
            
            # Animated progress
            with progress_placeholder.container():
                progress_bar = st.progress(0)
                for i in range(0, 101, 5):
                    progress_bar.progress(i)
                    if i < 30:
                        status_placeholder.info(f"🔧 모델 준비 중... ({provider})")
                    elif i < 70:
                        status_placeholder.info(f"✍️ 문서 생성 중... ({provider})")
                    else:
                        status_placeholder.info("🔍 품질 검증 중...")
                    time.sleep(0.1)
            
            # Check if we should use LoopAgent for iterative improvement
            if use_loop_agent and not is_refinement:
                # Use LoopAgent for comprehensive critique and refinement
                status_placeholder.info("🔄 ADK LoopAgent로 문서를 반복적으로 개선하는 중...")
                
                # Prepare config for LoopAgent
                loop_config = config.get_agent_config()
                loop_config['provider'] = provider
                loop_config['model'] = model
                
                # Also set provider-specific model keys
                if provider == "Anthropic":
                    loop_config['anthropic_model'] = model
                elif provider == "OpenAI":
                    loop_config['openai_model'] = model
                elif provider == "Google":
                    loop_config['google_model'] = model
                
                # Create and run LoopAgent
                from src.agents.loop_agent import LoopAgent
                loop_agent = LoopAgent(loop_config)
                
                # Run the loop agent with comprehensive improvement
                loop_result = loop_agent.run({
                    "document_type": input_data.get('document_type'),
                    "context": input_data.get('requirements'),
                    "tone": input_data.get('tone'),
                    "recipient": input_data.get('recipient', ''),
                    "subject": input_data.get('subject', ''),
                    "additional_context": input_data.get('additional_context', ''),
                    "provider": provider,
                    "model": model
                })
                
                # Extract results
                final_doc = loop_result.get('final_document', '')
                quality_score = loop_result.get('quality_score', 0.0)
                iterations = loop_result.get('iterations', 1)
                
                # Save draft from first iteration
                if loop_result.get('history') and len(loop_result['history']) > 0:
                    first_iteration = loop_result['history'][0].get('result', {})
                    draft_doc = first_iteration.get('draft', final_doc)
                    st.session_state.draft_document = draft_doc
                    st.session_state.refinement_history = [{
                        'version': '초안',
                        'content': draft_doc,
                        'timestamp': datetime.now().isoformat(),
                        'model': f"{provider} - {model}"
                    }]
                    
                    # Save critique history for diff analysis
                    st.session_state.critique_history = []
                    
                    # Add refinement history from loop iterations
                    for i, hist in enumerate(loop_result['history'], 1):
                        result = hist.get('result', {})
                        refined_content = result.get('refined_content', '')
                        critique = result.get('critique', '')
                        
                        if refined_content:
                            st.session_state.refinement_history.append({
                                'version': f'개선 {i}',
                                'content': refined_content,
                                'timestamp': hist.get('timestamp', datetime.now().isoformat()),
                                'model': f"{provider} - {model}",
                                'quality_score': result.get('quality_score', 0)
                            })
                        
                        if critique:
                            st.session_state.critique_history.append({
                                'iteration': i,
                                'critique': critique,
                                'quality_score': result.get('quality_score', 0),
                                'issues': result.get('issues_found', []),
                                'suggestions': result.get('suggestions', [])
                            })
                
                # Update status
                status_placeholder.success(
                    f"✅ LoopAgent 완료! "
                    f"총 {iterations}회 반복, "
                    f"품질 점수: {quality_score:.2f}, "
                    f"종료 사유: {loop_result.get('exit_reason', 'Unknown')}"
                )
                
            else:
                # Simple generation without LoopAgent
                prompt = self._create_prompt(input_data)
                
                # Generate response
                response = self.multi_model_agent.generate(
                    prompt,
                    provider=provider,
                    temperature=input_data.get('temperature', 0.7),
                    max_tokens=input_data.get('max_tokens', 2048)
                )
                
                final_doc = response.content
                
                # Save draft if first generation
                if not is_refinement and not st.session_state.draft_document:
                    st.session_state.draft_document = response.content
                    st.session_state.refinement_history = [{
                        'version': '초안',
                        'content': response.content,
                        'timestamp': datetime.now().isoformat(),
                        'model': f"{provider} - {response.model_used}"
                    }]
                
                # Calculate quality score for simple generation
                term_validation = validate_financial_terms(final_doc)
                compliance_check = check_compliance(final_doc, input_data.get("document_type", "email"))
                quality_score = calculate_quality_score(final_doc, term_validation, compliance_check)
                iterations = 1
            
            # Clear progress
            progress_placeholder.empty()
            status_placeholder.empty()
            
            # Final validation (for all paths)
            term_validation = validate_financial_terms(final_doc)
            compliance_check = check_compliance(final_doc, input_data.get("document_type", "email"))
            final_score = quality_score if use_loop_agent and not is_refinement else calculate_quality_score(final_doc, term_validation, compliance_check)
            
            # Update model usage stats
            model_used = model if use_loop_agent and not is_refinement else response.model_used if 'response' in locals() else model
            model_key = f"{provider} - {model_used}"
            if model_key not in st.session_state.stats['models_used']:
                st.session_state.stats['models_used'][model_key] = 0
            st.session_state.stats['models_used'][model_key] += 1
            
            result = {
                "success": True,
                "final_document": final_doc,
                "quality_score": final_score,
                "iterations": iterations if 'iterations' in locals() else 1,
                "total_time": 5.0,
                "provider": provider,
                "model_used": model_used,
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
            progress_placeholder.empty()
            status_placeholder.empty()
            return {"error": str(e), "success": False}
    
    def _create_prompt(self, input_data: Dict[str, Any]) -> str:
        """Create prompt for document generation"""
        doc_type = config.DOCUMENT_TYPES.get(input_data['document_type'], input_data['document_type'])
        
        prompt = f"""당신은 코스콤 금융영업부의 전문 문서 작성 AI입니다.
        
다음 요구사항과 추가 정보를 모두 반영하여 {doc_type}을(를) 작성해주세요:

[핵심 요구사항]
{input_data['requirements']}

[문서 스타일]
톤앤매너: {input_data['tone']}
"""
        
        if input_data.get('recipient'):
            prompt += f"\n\n[수신자 정보]\n수신자: {input_data['recipient']}"
            prompt += "\n- 수신자에게 적합한 호칭과 존칭을 사용하세요"
            prompt += "\n- 수신자의 입장과 관심사를 고려하여 작성하세요"
        
        if input_data.get('subject'):
            prompt += f"\n\n[제목/주제]\n{input_data['subject']}"
            prompt += "\n- 제목과 일관성 있는 내용으로 구성하세요"
            prompt += "\n- 핵심 메시지가 명확히 전달되도록 작성하세요"
        
        if input_data.get('additional_context'):
            prompt += f"\n\n[추가 컨텍스트 및 특별 지시사항]\n{input_data['additional_context']}"
            prompt += "\n- 추가 컨텍스트의 내용을 반드시 반영하세요"
            prompt += "\n- 특별히 강조된 사항은 문서에서 부각시켜 주세요"
        
        # Add length preference
        length_pref = input_data.get('length_preference', 'medium')
        
        prompt += """

[작성 기준]
1. 요구사항의 모든 내용을 빠짐없이 반영
2. 추가 정보와 컨텍스트를 적절히 활용
3. 금융 전문 용어를 정확하게 사용
4. 규정 준수 및 법적 요구사항 충족
5. 명확하고 논리적인 문장 구성
6. 적절한 구조와 형식 준수
7. 전문적이면서도 이해하기 쉬운 표현
8. 코스콤 금융영업부의 전문성과 신뢰성 반영
"""
        
        # Add length-specific instructions
        if length_pref == "short":
            prompt += "\n[문서 길이] ⚡ 간결하고 핵심적인 내용으로 1-2단락 이내로 작성"
        elif length_pref == "long":
            prompt += "\n[문서 길이] 📚 상세하고 종합적인 내용으로 5-7단락 이상 작성"
        else:
            prompt += "\n[문서 길이] 📄 적절한 길이로 3-4단락 정도로 작성"
        
        prompt += """

발신: 코스콤 금융영업부

문서를 작성해주세요:
"""
        
        return prompt
    
    def _update_stats(self, result: Dict[str, Any]):
        """Update statistics"""
        # Update session state stats
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
        
        # Stats are also automatically updated in database when saving document
    
    def run(self):
        """Run the application"""
        # Header
        self.render_header()
        
        # Sidebar with model selection and settings
        with st.sidebar:
            st.markdown("---")
            
            # Model selector in sidebar
            providers_available = self.render_sidebar_model_selector()
            
            if not providers_available:
                st.stop()
            
            st.markdown("---")
            
            # Model settings
            st.markdown("## ⚙️ 모델 설정")
            
            temperature = st.slider(
                "🌡️ Temperature (창의성)",
                min_value=0.0,
                max_value=1.0,
                value=config.TEMPERATURE,
                step=0.1,
                help="낮을수록 일관성 있고, 높을수록 창의적입니다"
            )
            
            max_tokens = st.number_input(
                "📝 최대 토큰 수",
                min_value=500,
                max_value=4000,
                value=config.MAX_OUTPUT_TOKENS,
                step=100,
                help="생성할 텍스트의 최대 길이"
            )
            
            st.markdown("---")
            
            # Document settings
            st.markdown("## 📄 문서 설정")
            
            doc_type = st.selectbox(
                "문서 유형",
                options=list(config.DOCUMENT_TYPES.keys()),
                format_func=lambda x: config.DOCUMENT_TYPES[x],
                help="작성할 문서의 유형을 선택하세요"
            )
            
            tone = st.select_slider(
                "톤앤매너",
                options=["formal", "professional", "professional_premium", "analytical", "urgent", "friendly"],
                value=st.session_state.get('example_tone', 'professional'),
                format_func=lambda x: {
                    "formal": "격식있는",
                    "professional": "전문적인",
                    "professional_premium": "프리미엄 (VIP용)",
                    "analytical": "분석적인",
                    "urgent": "긴급한",
                    "friendly": "친근한"
                }.get(x, x),
                help="문서의 톤을 선택하세요"
            )
            
            # Document length preference
            doc_length = st.select_slider(
                "📏 문서 길이",
                options=["short", "medium", "long"],
                value="medium",
                format_func=lambda x: {
                    "short": "간결 (1-2단락)",
                    "medium": "보통 (3-4단락)",
                    "long": "상세 (5-7단락+)"
                }.get(x, x),
                help="생성할 문서의 길이를 선택하세요"
            )
            
            # Advanced prompt settings
            with st.expander("🧪 고급 프롬프트 설정", expanded=False):
                use_context7 = st.checkbox(
                    "📚 Context7 패턴 사용",
                    value=True,
                    help="Context7 문서 구조 패턴과 금융 전문 용어를 적용합니다"
                )
                
                use_sequential = st.checkbox(
                    "🔄 Sequential Thinking 사용",
                    value=True,
                    help="체계적인 순차 사고 프레임워크를 적용합니다"
                )
                
                if st.button("🎯 고급 프롬프트 적용", use_container_width=True):
                    # Get current requirements from session state if available
                    current_requirements = st.session_state.get('requirements_input', '')
                    if current_requirements:
                        # Build a temporary example from current inputs
                        temp_example = {
                            'title': doc_type,
                            'requirements': current_requirements,
                            'recipient': st.session_state.get('recipient_input', ''),
                            'subject': st.session_state.get('subject_input', ''),
                            'additional_context': st.session_state.get('context_input', ''),
                            'tone': tone,
                            'length': doc_length
                        }
                        
                        enhanced_prompt = self.example_templates.generate_advanced_prompt(
                            temp_example,
                            use_context7=use_context7,
                            use_sequential=use_sequential,
                            length_preference=doc_length
                        )
                        
                        st.session_state.example_requirements = enhanced_prompt
                        st.success("✨ 고급 프롬프트가 적용되었습니다!")
                        st.rerun()
                    else:
                        st.warning("먼저 요구사항을 입력해주세요.")
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("## 🚀 빠른 실행")
            
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.history = []
                st.session_state.current_result = None
                st.rerun()
            
            if st.button("📊 통계 초기화", use_container_width=True):
                st.session_state.stats = {
                    'total_documents': 0,
                    'avg_quality': 0,
                    'avg_iterations': 0,
                    'total_time': 0,
                    'models_used': {}
                }
                st.rerun()
        
        # Main content area
        st.markdown("---")
        
        # Stats dashboard
        self.render_stats()
        
        st.markdown("---")
        
        # Tabs for different features
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "✍️ 문서 작성",
            "🔄 초안 vs 최종",
            "🔀 변경 사항 분석",
            "🔍 모델 비교",
            "📊 분석",
            "📚 이력"
        ])
        
        with tab1:
            col1, col2 = st.columns([1, 1], gap="large")
            
            with col1:
                st.markdown("### 📝 문서 요구사항")
                
                # Use example values if available
                req_value = st.session_state.get('example_requirements', '')
                requirements = st.text_area(
                    "요구사항",
                    value=req_value,
                    placeholder="작성하고자 하는 문서의 내용과 요구사항을 입력하세요...\n\n예시:\n- 신규 금융 상품 안내 이메일\n- 투자 제안서 초안\n- 규정 준수 보고서",
                    height=250,
                    label_visibility="collapsed",
                    key="requirements_input"
                )
                
                # Check if we have example data
                has_example = any([
                    'example_recipient' in st.session_state,
                    'example_subject' in st.session_state,
                    'example_context' in st.session_state
                ])
                
                with st.expander("📎 추가 정보", expanded=has_example):
                    recipient = st.text_input(
                        "수신자",
                        value=st.session_state.get('example_recipient', ''),
                        placeholder="예: 김철수 대표님",
                        key="recipient_input"
                    )
                    subject = st.text_input(
                        "제목",
                        value=st.session_state.get('example_subject', ''),
                        placeholder="예: 2024년 신규 투자 상품 안내",
                        key="subject_input"
                    )
                    additional_context = st.text_area(
                        "추가 컨텍스트",
                        value=st.session_state.get('example_context', ''),
                        placeholder="특별히 강조하거나 포함해야 할 내용을 입력하세요...",
                        height=100,
                        key="context_input"
                    )
                
                # Clean up example data after use
                if req_value and requirements != req_value:
                    for key in ['example_requirements', 'example_recipient', 'example_subject', 'example_context', 'example_tone']:
                        if key in st.session_state:
                            del st.session_state[key]
                
                # LoopAgent 사용 옵션
                use_loop = st.checkbox(
                    "🔄 ADK LoopAgent로 비평 및 개선 수행",
                    value=True,
                    help="체크하면 문서를 여러 번 비평하고 개선하여 품질을 높입니다."
                )
                
                col1_1, col1_2 = st.columns(2)
                with col1_1:
                    if st.button("🚀 문서 생성", type="primary", use_container_width=True):
                        if requirements:
                            if not st.session_state.selected_model:
                                st.warning("먼저 사이드바에서 AI 모델을 선택해주세요.")
                            else:
                                input_data = {
                                    "document_type": doc_type,
                                    "requirements": requirements,
                                    "tone": tone,
                                    "recipient": recipient,
                                    "subject": subject,
                                    "additional_context": additional_context,
                                    "temperature": temperature,
                                    "max_tokens": max_tokens,
                                    "length_preference": doc_length
                                }
                                
                                result = self.process_document(input_data, use_loop_agent=use_loop)
                                
                                st.session_state.current_result = result
                                # Save to database
                                doc_data = {
                                    "timestamp": datetime.now().isoformat(),
                                    "input": input_data,
                                    "result": result
                                }
                                
                                try:
                                    doc_id = self.db.save_document(doc_data)
                                    result['document_id'] = doc_id
                                except Exception as e:
                                    logger.error(f"Error saving to database: {str(e)}")
                                
                                st.session_state.history.append(doc_data)
                                
                                if result.get("success"):
                                    st.success(f"✅ 문서 생성 완료! (모델: {result.get('model_used', 'Unknown')})")
                                    st.balloons()
                                else:
                                    st.error(f"❌ 오류: {result.get('error')}")
                        else:
                            st.warning("요구사항을 입력해주세요.")
                
                with col1_2:
                    if st.button("🎲 예시 선택", use_container_width=True, key="example_selector_btn"):
                        st.session_state.show_example_selector = not st.session_state.get('show_example_selector', False)
                
                # Example selector dialog
                if st.session_state.get('show_example_selector', False):
                    with st.container():
                        st.markdown("### 📚 코스콤 금융영업부 최적화 예시")
                        
                        # Document type filter
                        example_category = st.selectbox(
                            "문서 유형 선택",
                            ["전체"] + [
                                "email (이메일)",
                                "proposal (제안서)",
                                "report (보고서)",
                                "official (공식문서)"
                            ],
                            key="example_category_select"
                        )
                        
                        # Get examples based on category
                        if example_category == "전체":
                            examples = []
                            for cat in ['email', 'proposal', 'report', 'official']:
                                examples.extend(self.example_templates.get_examples_by_category(cat))
                        else:
                            cat_key = example_category.split(' ')[0]
                            examples = self.example_templates.get_examples_by_category(cat_key)
                        
                        # Display examples in a grid
                        if examples:
                            for idx, example in enumerate(examples):
                                with st.expander(f"{example['title']} - {example['category']}", expanded=False):
                                    st.write(example.get('requirements', '')[:200] + "...")
                                    
                                    # Advanced options
                                    col_opt1, col_opt2, col_opt3 = st.columns(3)
                                    with col_opt1:
                                        use_c7 = st.checkbox(
                                            "Context7 패턴",
                                            value=True,
                                            key=f"c7_{idx}",
                                            help="Context7 문서 구조 패턴 적용"
                                        )
                                    with col_opt2:
                                        use_seq = st.checkbox(
                                            "Sequential",
                                            value=True,
                                            key=f"seq_{idx}",
                                            help="Sequential Thinking 적용"
                                        )
                                    with col_opt3:
                                        length_pref = st.select_slider(
                                            "길이",
                                            options=["short", "medium", "long"],
                                            value=example.get('length', 'medium'),
                                            key=f"length_{idx}"
                                        )
                                    
                                    if st.button(
                                        "✅ 이 예시 사용",
                                        key=f"use_example_{idx}",
                                        use_container_width=True,
                                        type="primary"
                                    ):
                                        # Generate advanced prompt
                                        advanced_prompt = self.example_templates.generate_advanced_prompt(
                                            example,
                                            use_context7=use_c7,
                                            use_sequential=use_seq,
                                            length_preference=length_pref
                                        )
                                        
                                        # Set the values
                                        st.session_state.example_requirements = advanced_prompt
                                        st.session_state.example_recipient = example.get('recipient', '')
                                        st.session_state.example_subject = example.get('subject', '')
                                        st.session_state.example_context = example.get('additional_context', '')
                                        st.session_state.example_tone = example.get('tone', 'professional')
                                        st.session_state.show_example_selector = False
                                        st.rerun()
                        
                        # Close button
                        if st.button("❌ 닫기", use_container_width=True):
                            st.session_state.show_example_selector = False
                            st.rerun()
            
            with col2:
                st.markdown("### 📄 생성된 문서")
                
                if st.session_state.current_result and st.session_state.current_result.get("success"):
                    result = st.session_state.current_result
                    
                    # Model info badge
                    provider = result.get('provider', 'Unknown')
                    model = result.get('model_used', 'Unknown')
                    
                    col2_1, col2_2 = st.columns([2, 1])
                    with col2_1:
                        st.markdown(f"""
                        <div style="padding: 0.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    color: white; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                            <strong>🤖 {provider}</strong> | {model}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2_2:
                        quality_score = result.get('quality_score', 0)
                        if quality_score >= 0.9:
                            quality_badge = "🏆 우수"
                            quality_color = "#00b894"
                        elif quality_score >= 0.8:
                            quality_badge = "✅ 양호"
                            quality_color = "#fdcb6e"
                        else:
                            quality_badge = "⚠️ 개선필요"
                            quality_color = "#d63031"
                        
                        st.markdown(f"""
                        <div style="padding: 0.5rem; background: {quality_color}; 
                                    color: white; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                            {quality_badge} {quality_score:.1%}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Document content
                    st.text_area(
                        "최종 문서",
                        value=result.get("final_document", ""),
                        height=350,
                        label_visibility="collapsed"
                    )
                    
                    # Metrics
                    col2_1, col2_2, col2_3 = st.columns(3)
                    with col2_1:
                        st.metric("⏱️ 처리 시간", f"{result.get('total_time', 0):.1f}초")
                    with col2_2:
                        doc_length = len(result.get("final_document", ""))
                        st.metric("📏 문서 길이", f"{doc_length:,}자")
                    with col2_3:
                        word_count = len(result.get("final_document", "").split())
                        st.metric("📝 단어 수", f"{word_count:,}개")
                    
                    # Download button
                    st.download_button(
                        label="📥 문서 다운로드",
                        data=result["final_document"],
                        file_name=f"document_{provider}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.info("💡 왼쪽에서 요구사항을 입력하고 '문서 생성' 버튼을 클릭하세요.")
                    
                    # Show example if available
                    if hasattr(st.session_state, 'example_text'):
                        st.markdown("#### 예시 요구사항:")
                        st.info(st.session_state.example_text)
        
        with tab2:
            st.markdown("### 🔄 초안 vs 최종 문서 비교")
            
            if st.session_state.draft_document and st.session_state.current_result:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📝 초안")
                    st.text_area(
                        "초안 문서",
                        value=st.session_state.draft_document,
                        height=400,
                        label_visibility="collapsed",
                        key="draft_compare"
                    )
                    
                    # Draft metrics
                    draft_terms = validate_financial_terms(st.session_state.draft_document)
                    draft_compliance = check_compliance(st.session_state.draft_document, "email")
                    draft_score = calculate_quality_score(st.session_state.draft_document, draft_terms, draft_compliance)
                    
                    st.metric("초안 품질", f"{draft_score:.1%}")
                    st.metric("초안 길이", f"{len(st.session_state.draft_document):,}자")
                
                with col2:
                    st.markdown("#### ✨ 최종 문서")
                    final_doc = st.session_state.current_result.get('final_document', '')
                    st.text_area(
                        "최종 문서",
                        value=final_doc,
                        height=400,
                        label_visibility="collapsed",
                        key="final_compare"
                    )
                    
                    # Final metrics
                    final_score = st.session_state.current_result.get('quality_score', 0)
                    st.metric("최종 품질", f"{final_score:.1%}")
                    st.metric("최종 길이", f"{len(final_doc):,}자")
                
                # Improvement analysis
                st.markdown("#### 📈 개선 분석")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    improvement = (final_score - draft_score) * 100
                    if improvement > 0:
                        st.success(f"품질 개선: +{improvement:.1f}%")
                    elif improvement < 0:
                        st.error(f"품질 하락: {improvement:.1f}%")
                    else:
                        st.info("품질 동일")
                
                with col2:
                    length_change = len(final_doc) - len(st.session_state.draft_document)
                    if length_change > 0:
                        st.info(f"길이 증가: +{length_change:,}자")
                    elif length_change < 0:
                        st.info(f"길이 감소: {length_change:,}자")
                    else:
                        st.info("길이 동일")
                
                with col3:
                    if st.button("♻️ 문서 재정제", use_container_width=True):
                        # Refine document again
                        refinement_prompt = f"다음 문서를 더 개선해주세요:\n\n{final_doc}"
                        input_data = st.session_state.current_result.get('input', {})
                        input_data['requirements'] = refinement_prompt
                        
                        with st.spinner("문서를 재정제하는 중..."):
                            refined_result = self.process_document(input_data, is_refinement=True)
                            if refined_result.get('success'):
                                st.session_state.current_result = refined_result
                                st.session_state.refinement_history.append({
                                    'version': f"정제 {len(st.session_state.refinement_history)}",
                                    'content': refined_result.get('final_document', ''),
                                    'timestamp': datetime.now().isoformat(),
                                    'model': f"{refined_result.get('provider')} - {refined_result.get('model_used')}"
                                })
                                st.success("문서가 재정제되었습니다!")
                                st.rerun()
                
                # Refinement history
                if len(st.session_state.refinement_history) > 1:
                    st.markdown("#### 📚 정제 이력")
                    for idx, version in enumerate(st.session_state.refinement_history):
                        with st.expander(f"{version['version']} - {version['model']}"):
                            st.text_area(
                                f"버전 {idx}",
                                value=version['content'][:500] + "...",
                                height=150,
                                label_visibility="collapsed",
                                key=f"version_{idx}"
                            )
            else:
                st.info("먼저 문서를 생성해주세요. 문서 작성 탭에서 요구사항을 입력하고 생성 버튼을 클릭하세요.")
        
        with tab3:
            st.markdown("### 🔀 변경 사항 상세 분석")
            
            if st.session_state.draft_document and st.session_state.current_result:
                # View mode selector
                view_mode = st.radio(
                    "분석 모드",
                    ["변경 사항 요약", "라인별 비교", "단어별 비교", "수정 이유 분석"],
                    horizontal=True
                )
                
                draft_doc = st.session_state.draft_document
                final_doc = st.session_state.current_result.get('final_document', '')
                
                if view_mode == "변경 사항 요약":
                    # Statistics
                    stats = get_change_statistics(draft_doc, final_doc)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(
                            "문서 유사도",
                            f"{stats['similarity']:.1f}%",
                            help="초안과 최종본의 텍스트 유사도"
                        )
                    with col2:
                        st.metric(
                            "길이 변화",
                            f"{stats['length_change']:+,}자",
                            f"{stats['length_change_percent']:+.1f}%"
                        )
                    with col3:
                        st.metric(
                            "단어 수 변화",
                            f"{stats['word_change']:+,}개",
                            help="총 단어 수의 변화"
                        )
                    with col4:
                        st.metric(
                            "문장 수 변화",
                            f"{stats['sentences_final'] - stats['sentences_original']:+,}개",
                            help="문장 개수의 변화"
                        )
                    
                    # Modification summary from critique history
                    if st.session_state.critique_history:
                        st.markdown("#### 📝 주요 수정 사항")
                        
                        all_modifications = []
                        for critique_item in st.session_state.critique_history:
                            critique_text = critique_item.get('critique', '')
                            if critique_text:
                                mods = extract_modifications(critique_text)
                                all_modifications.extend(mods)
                        
                        if all_modifications:
                            summary_html = create_modification_summary(all_modifications)
                            st.markdown(summary_html, unsafe_allow_html=True)
                        else:
                            st.info("수정 사항을 자동으로 추출할 수 없습니다.")
                    
                    # Quality improvement timeline
                    if st.session_state.critique_history:
                        st.markdown("#### 📈 품질 개선 추이")
                        
                        iterations = []
                        scores = []
                        for critique_item in st.session_state.critique_history:
                            iterations.append(f"반복 {critique_item['iteration']}")
                            scores.append(critique_item.get('quality_score', 0) * 100)
                        
                        # Simple chart using columns
                        chart_cols = st.columns(len(iterations))
                        for i, (iter_name, score) in enumerate(zip(iterations, scores)):
                            with chart_cols[i]:
                                st.metric(iter_name, f"{score:.0f}%")
                
                elif view_mode == "라인별 비교":
                    st.markdown("#### 📄 라인별 차이점")
                    
                    # Create line diff
                    diff_html = create_diff_html(draft_doc, final_doc, "초안", "최종")
                    st.markdown(diff_html, unsafe_allow_html=True)
                    
                    # Download diff as text
                    diff_text = f"=== 초안 ===\n{draft_doc}\n\n=== 최종 ===\n{final_doc}"
                    st.download_button(
                        "📥 비교 결과 다운로드",
                        diff_text,
                        file_name=f"diff_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                
                elif view_mode == "단어별 비교":
                    st.markdown("#### 📝 단어 수준 변경사항")
                    
                    word_diff_html, word_stats = create_word_diff(draft_doc, final_doc)
                    
                    # Show statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("추가된 단어", word_stats['added'])
                    with col2:
                        st.metric("삭제된 단어", word_stats['removed'])
                    with col3:
                        st.metric("총 변경", word_stats['total_changes'])
                    
                    # Show word diff
                    st.markdown(
                        f'<div style="background: white; padding: 1rem; border-radius: 8px; line-height: 1.8;">{word_diff_html}</div>',
                        unsafe_allow_html=True
                    )
                
                elif view_mode == "수정 이유 분석":
                    st.markdown("#### 🔍 수정 이유 및 근거")
                    
                    if st.session_state.critique_history:
                        for i, critique_item in enumerate(st.session_state.critique_history, 1):
                            with st.expander(f"반복 {i} - 품질 점수: {critique_item.get('quality_score', 0):.1%}"):
                                critique_text = critique_item.get('critique', '')
                                
                                # Display issues
                                issues = critique_item.get('issues', [])
                                if issues:
                                    st.markdown("**발견된 문제점:**")
                                    for issue in issues:
                                        st.markdown(f"- ⚠️ {issue}")
                                
                                # Display suggestions
                                suggestions = critique_item.get('suggestions', [])
                                if suggestions:
                                    st.markdown("**개선 제안:**")
                                    for suggestion in suggestions:
                                        st.markdown(f"- 💡 {suggestion}")
                                
                                # Display full critique
                                if critique_text:
                                    st.markdown("**상세 비평:**")
                                    st.text_area(
                                        "비평 내용",
                                        value=critique_text,
                                        height=200,
                                        label_visibility="collapsed",
                                        key=f"critique_{i}"
                                    )
                    else:
                        st.info("LoopAgent를 사용하여 문서를 생성하면 상세한 수정 이유를 확인할 수 있습니다.")
                
                # Export options
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📊 분석 보고서 생성", use_container_width=True):
                        # Generate comprehensive report
                        report = f"""# 문서 개선 분석 보고서
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 개요
- 초안 길이: {len(draft_doc):,}자
- 최종 길이: {len(final_doc):,}자
- 변경률: {((len(final_doc) - len(draft_doc)) / len(draft_doc) * 100):.1f}%
- 문서 유사도: {calculate_similarity(draft_doc, final_doc) * 100:.1f}%

## 2. 초안
{draft_doc}

## 3. 최종본
{final_doc}

## 4. 주요 변경 사항
{' '.join([f"- {mod['description']}" for critique in st.session_state.critique_history for mod in extract_modifications(critique.get('critique', ''))][:5])}
"""
                        st.download_button(
                            "📥 보고서 다운로드",
                            report,
                            file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown"
                        )
                
                with col2:
                    if st.button("🔄 재분석", use_container_width=True):
                        st.rerun()
            
            else:
                st.info("문서를 생성한 후 변경 사항 분석을 확인할 수 있습니다.")
        
        with tab4:
            st.markdown("### 🔍 여러 모델 비교")
            st.info("동일한 요구사항으로 여러 AI 모델의 결과를 비교해보세요.")
            
            compare_requirements = st.text_area(
                "비교할 문서 요구사항",
                placeholder="모든 모델에서 테스트할 요구사항을 입력하세요...",
                height=150,
                key="compare_requirements"
            )
            
            # Model selection for comparison
            st.markdown("#### 비교할 모델 선택")
            col1, col2, col3 = st.columns(3)
            
            compare_models = []
            with col1:
                if config.ANTHROPIC_API_KEY and st.checkbox("Anthropic Claude", value=True):
                    compare_models.append("Anthropic")
            with col2:
                if config.OPENAI_API_KEY and st.checkbox("OpenAI GPT", value=True):
                    compare_models.append("OpenAI")
            with col3:
                if config.GOOGLE_API_KEY and st.checkbox("Google Gemini", value=True):
                    compare_models.append("Google")
            
            if st.button("🔬 선택한 모델로 비교 생성", type="primary", use_container_width=True):
                if compare_requirements and compare_models:
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
                    
                    # Progress bar for comparison
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    results = {}
                    for idx, provider in enumerate(compare_models):
                        status_text.text(f"🤖 {provider} 모델로 생성 중...")
                        progress_bar.progress((idx + 1) / len(compare_models))
                        
                        try:
                            response = self.multi_model_agent.generate(prompt, provider=provider)
                            results[provider] = response
                        except Exception as e:
                            st.error(f"{provider} 오류: {str(e)}")
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display comparison results
                    if results:
                        st.markdown("#### 📊 비교 결과")
                        
                        # Create columns for side-by-side comparison
                        cols = st.columns(len(results))
                        
                        for idx, (provider, response) in enumerate(results.items()):
                            with cols[idx]:
                                st.markdown(f"##### {provider}")
                                
                                # Calculate quality score
                                term_validation = validate_financial_terms(response.content)
                                compliance_check = check_compliance(response.content, doc_type)
                                quality_score = calculate_quality_score(response.content, term_validation, compliance_check)
                                
                                # Quality badge
                                if quality_score >= 0.9:
                                    st.success(f"품질: {quality_score:.1%}")
                                elif quality_score >= 0.8:
                                    st.warning(f"품질: {quality_score:.1%}")
                                else:
                                    st.error(f"품질: {quality_score:.1%}")
                                
                                st.text_area(
                                    f"{provider} 결과",
                                    value=response.content,
                                    height=400,
                                    label_visibility="collapsed",
                                    key=f"compare_{provider}"
                                )
                                
                                st.metric("모델", response.model_used)
                                st.metric("문자 수", f"{len(response.content):,}")
                else:
                    if not compare_requirements:
                        st.warning("비교할 요구사항을 입력해주세요.")
                    if not compare_models:
                        st.warning("비교할 모델을 선택해주세요.")
        
        with tab4:
            st.markdown("### 📊 통계 및 분석")
            
            # Statistics period selector
            col1, col2 = st.columns([3, 1])
            with col1:
                stat_period = st.selectbox(
                    "통계 기간",
                    ["오늘", "지난 7일", "지난 30일", "전체"],
                    index=2
                )
            with col2:
                if st.button("🔄 새로고침", use_container_width=True):
                    self._load_statistics_from_db()
                    st.rerun()
            
            # Calculate period days
            if stat_period == "오늘":
                days = 1
            elif stat_period == "지난 7일":
                days = 7
            elif stat_period == "지난 30일":
                days = 30
            else:
                days = 365
            
            # Load statistics from database
            try:
                db_stats = self.db.get_statistics(days=days)
            except:
                db_stats = st.session_state.stats
            
            # Overall statistics
            st.markdown("#### 🎯 전체 통계")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📄 총 문서",
                    f"{db_stats.get('total_documents', 0):,}개",
                    delta=f"{len(st.session_state.history)}개 (세션)"
                )
            
            with col2:
                avg_quality = db_stats.get('avg_quality', 0)
                st.metric(
                    "🏆 평균 품질",
                    f"{avg_quality:.1%}",
                    delta="우수" if avg_quality >= 0.9 else "양호"
                )
            
            with col3:
                st.metric(
                    "🔄 평균 반복",
                    f"{db_stats.get('avg_iterations', 0):.1f}회"
                )
            
            with col4:
                total_time = db_stats.get('total_time', 0)
                st.metric(
                    "⏱️ 총 소요시간",
                    f"{total_time:.0f}초" if total_time < 3600 else f"{total_time/3600:.1f}시간"
                )
            
            # Provider statistics
            if db_stats.get('by_provider'):
                st.markdown("#### 🤖 모델별 통계")
                provider_cols = st.columns(len(db_stats['by_provider']))
                for idx, (provider, count) in enumerate(db_stats['by_provider'].items()):
                    with provider_cols[idx]:
                        st.metric(provider, f"{count}개")
            
            # Document type statistics
            if db_stats.get('by_document_type'):
                st.markdown("#### 📁 문서 유형별 통계")
                doc_type_cols = st.columns(min(len(db_stats['by_document_type']), 5))
                for idx, (doc_type, count) in enumerate(list(db_stats['by_document_type'].items())[:5]):
                    with doc_type_cols[idx % len(doc_type_cols)]:
                        st.metric(doc_type, f"{count}개")
            
            # Current document analysis (if available)
            if st.session_state.current_result and st.session_state.current_result.get("success"):
                st.markdown("---")
                st.markdown("### 📄 현재 문서 분석")
                result = st.session_state.current_result
                
                # Create beautiful analysis cards
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🎯 품질 지표")
                    
                    validation = result.get('validation', {})
                    
                    # Quality score visualization
                    quality_score = result.get('quality_score', 0)
                    st.progress(quality_score)
                    
                    # Detailed metrics
                    st.markdown(f"""
                    <div class="stat-card">
                        <h4>상세 평가</h4>
                        <ul>
                            <li>전체 품질: <strong>{quality_score:.1%}</strong></li>
                            <li>용어 정확도: <strong>{validation.get('terms', {}).get('score', 0):.1%}</strong></li>
                            <li>규정 준수: <strong>{'✅ 준수' if validation.get('compliance', {}).get('is_compliant') else '❌ 미준수'}</strong></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### 📈 문서 통계")
                    
                    doc = result.get('final_document', '')
                    
                    # Text statistics
                    char_count = len(doc)
                    word_count = len(doc.split())
                    sentence_count = doc.count('.') + doc.count('!') + doc.count('?')
                    
                    st.markdown(f"""
                    <div class="stat-card">
                        <h4>텍스트 분석</h4>
                        <ul>
                            <li>문자 수: <strong>{char_count:,}</strong></li>
                            <li>단어 수: <strong>{word_count:,}</strong></li>
                            <li>문장 수: <strong>{sentence_count:,}</strong></li>
                            <li>평균 문장 길이: <strong>{word_count/max(sentence_count, 1):.1f} 단어</strong></li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Model performance
                st.markdown("#### ⚡ 모델 성능")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🤖 사용 모델", result.get('provider', '-'))
                with col2:
                    st.metric("⏱️ 처리 시간", f"{result.get('total_time', 0):.1f}초")
                with col3:
                    st.metric("🔄 반복 횟수", result.get('iterations', 1))
            else:
                st.info("먼저 문서를 생성해주세요.")
        
        with tab5:
            if st.session_state.history:
                st.markdown("### 📚 문서 생성 이력")
                
                # History filter
                col1, col2 = st.columns([2, 1])
                with col1:
                    search_term = st.text_input("🔍 검색", placeholder="이력에서 검색...")
                with col2:
                    sort_order = st.selectbox("정렬", ["최신순", "오래된순", "품질순"])
                
                # Sort history
                sorted_history = st.session_state.history.copy()
                if sort_order == "최신순":
                    sorted_history.reverse()
                elif sort_order == "품질순":
                    sorted_history.sort(key=lambda x: x['result'].get('quality_score', 0), reverse=True)
                
                # Filter history
                if search_term:
                    sorted_history = [
                        item for item in sorted_history
                        if search_term.lower() in str(item).lower()
                    ]
                
                # Display history
                for idx, item in enumerate(sorted_history, 1):
                    timestamp = datetime.fromisoformat(item['timestamp'])
                    result = item['result']
                    
                    if result.get('success'):
                        with st.expander(
                            f"📄 문서 #{idx} | "
                            f"{timestamp.strftime('%Y-%m-%d %H:%M')} | "
                            f"{result.get('provider', 'Unknown')} | "
                            f"품질: {result.get('quality_score', 0):.1%}"
                        ):
                            col1, col2 = st.columns([1, 2])
                            
                            with col1:
                                st.markdown("**📋 요청 정보**")
                                st.write(f"문서 유형: {item['input']['document_type']}")
                                st.write(f"톤: {item['input']['tone']}")
                                st.write(f"모델: {result.get('model_used', '-')}")
                                st.write(f"품질: {result.get('quality_score', 0):.1%}")
                                st.write(f"시간: {result.get('total_time', 0):.1f}초")
                            
                            with col2:
                                st.markdown("**📄 생성된 문서**")
                                st.text_area(
                                    "문서 내용",
                                    value=result.get('final_document', ''),
                                    height=200,
                                    label_visibility="collapsed",
                                    key=f"history_{idx}"
                                )
                                
                                col1_btn, col2_btn = st.columns(2)
                                with col1_btn:
                                    st.download_button(
                                        label="📥 다운로드",
                                        data=result.get('final_document', ''),
                                        file_name=f"history_{idx}_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt",
                                        mime="text/plain",
                                        key=f"download_{idx}",
                                        use_container_width=True
                                    )
                                with col2_btn:
                                    if result.get('document_id'):
                                        st.caption(f"📌 DB ID: {result['document_id']}")
            else:
                st.info("아직 생성된 문서가 없습니다. 문서를 생성하면 여기에 이력이 표시됩니다.")
            
            # Export options
            st.markdown("---")
            st.markdown("### 💾 데이터 내보내기")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 JSON으로 내보내기", use_container_width=True):
                    try:
                        export_data = self.db.export_data("json")
                        st.download_button(
                            "📥 JSON 다운로드",
                            data=export_data,
                            file_name=f"adk_writer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Export 오류: {str(e)}")
            
            with col2:
                if st.button("📋 CSV로 내보내기", use_container_width=True):
                    try:
                        export_data = self.db.export_data("csv")
                        st.download_button(
                            "📥 CSV 다운로드",
                            data=export_data,
                            file_name=f"adk_writer_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Export 오류: {str(e)}")
            
            with col3:
                # Database statistics
                try:
                    db_stats = self.db.get_statistics(days=30)
                    st.metric("📊 전체 문서", f"{db_stats['total_documents']:,}개")
                except:
                    st.metric("📊 세션 문서", f"{len(st.session_state.history)}개")


def main():
    """Main entry point"""
    app = MultiModelFinancialWritingApp()
    app.run()


if __name__ == "__main__":
    main()