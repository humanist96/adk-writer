"""
Advanced Premium Financial Writing AI System with Modern UI
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import difflib
import time

from src.config import config
from src.agents.loop_agent import LoopAgent
from src.tools.custom_tools import (
    validate_financial_terms,
    check_compliance,
    apply_template,
    calculate_quality_score
)
from loguru import logger

# Configure logger
logger.add("logs/app_{time}.log", rotation="1 day", retention="7 days")

# Page configuration
st.set_page_config(
    page_title="AI Financial Writer Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    css_file = Path("static/styles.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Additional inline styles for Streamlit components
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom container styles */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    /* Premium gradient text */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    /* Modern button */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 12px;
        color: #64748b;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Progress styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: white;
        border-radius: 12px;
        border: 2px solid #e2e8f0;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    
    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

class PremiumFinancialWritingApp:
    """Premium Financial Writing AI Application"""
    
    def __init__(self):
        self.config = config
        self.loop_agent = None
        self._initialize_agent()
        self._initialize_session_state()
    
    def _initialize_agent(self):
        """Initialize the LoopAgent with configuration"""
        try:
            config.validate()
            self.loop_agent = LoopAgent(config.get_agent_config())
            logger.info("LoopAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LoopAgent: {str(e)}")
            st.error(f"초기화 실패: {str(e)}")
    
    def _initialize_session_state(self):
        """Initialize session state variables"""
        if 'history' not in st.session_state:
            st.session_state.history = []
        if 'current_result' not in st.session_state:
            st.session_state.current_result = None
        if 'comparison_mode' not in st.session_state:
            st.session_state.comparison_mode = False
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        if 'stats' not in st.session_state:
            st.session_state.stats = {
                'total_documents': 0,
                'avg_quality': 0,
                'avg_iterations': 0,
                'total_time': 0
            }
    
    def render_header(self):
        """Render premium header"""
        st.markdown("""
        <div class="app-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     padding: 2rem; border-radius: 16px; margin-bottom: 2rem;">
            <div class="header-content" style="color: white;">
                <div class="logo-section">
                    <h1 style="font-size: 2.5rem; margin: 0;">
                        💼 AI Financial Writer Pro
                    </h1>
                    <p style="font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem;">
                        차세대 금융 문서 작성 AI 플랫폼 | Powered by Google Gemini & ADK
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_stats_dashboard(self):
        """Render statistics dashboard"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="stat-card fade-in">
                <div class="metric-label">총 생성 문서</div>
                <div class="metric-value gradient-text" style="font-size: 2rem;">
                    {}</div>
                <div class="metric-change positive">+12% 이번 주</div>
            </div>
            """.format(st.session_state.stats['total_documents']), unsafe_allow_html=True)
        
        with col2:
            avg_quality = st.session_state.stats['avg_quality']
            st.markdown("""
            <div class="stat-card fade-in">
                <div class="metric-label">평균 품질 점수</div>
                <div class="metric-value gradient-text" style="font-size: 2rem;">
                    {:.1%}</div>
                <div class="metric-change positive">+5% 향상</div>
            </div>
            """.format(avg_quality), unsafe_allow_html=True)
        
        with col3:
            avg_iter = st.session_state.stats['avg_iterations']
            st.markdown("""
            <div class="stat-card fade-in">
                <div class="metric-label">평균 반복 횟수</div>
                <div class="metric-value gradient-text" style="font-size: 2rem;">
                    {:.1f}</div>
                <div class="metric-change">최적화됨</div>
            </div>
            """.format(avg_iter), unsafe_allow_html=True)
        
        with col4:
            total_time = st.session_state.stats['total_time']
            st.markdown("""
            <div class="stat-card fade-in">
                <div class="metric-label">총 처리 시간</div>
                <div class="metric-value gradient-text" style="font-size: 2rem;">
                    {:.0f}s</div>
                <div class="metric-change">-20% 단축</div>
            </div>
            """.format(total_time), unsafe_allow_html=True)
    
    def render_document_comparison(self, original: str, refined: str):
        """Render document comparison view"""
        st.markdown("### 📊 문서 비교 분석")
        
        # Create two columns for comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="comparison-panel original">
                <div class="comparison-header">
                    <div class="comparison-title">
                        📝 초안
                        <span class="badge-original">Original</span>
                    </div>
                </div>
                <div class="comparison-content">
                    {}
                </div>
            </div>
            """.format(original.replace('\n', '<br>')), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="comparison-panel refined">
                <div class="comparison-header">
                    <div class="comparison-title">
                        ✨ 최종본
                        <span class="badge-refined">Refined</span>
                    </div>
                </div>
                <div class="comparison-content">
                    {}
                </div>
            </div>
            """.format(refined.replace('\n', '<br>')), unsafe_allow_html=True)
        
        # Show differences
        with st.expander("🔍 상세 변경 사항 보기"):
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                refined.splitlines(keepends=True),
                fromfile='초안',
                tofile='최종본',
                n=3
            )
            diff_text = ''.join(diff)
            st.code(diff_text, language='diff')
    
    def render_quality_chart(self, history: List[Dict]):
        """Render quality improvement chart"""
        if not history:
            return
        
        iterations = [h['iteration'] for h in history]
        scores = [h['result'].get('quality_score', 0) * 100 for h in history]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=iterations,
            y=scores,
            mode='lines+markers',
            name='품질 점수',
            line=dict(
                color='rgb(102, 126, 234)',
                width=3,
                shape='spline'
            ),
            marker=dict(
                size=10,
                color='rgb(102, 126, 234)',
                line=dict(color='white', width=2)
            ),
            fill='tozeroy',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        fig.update_layout(
            title='품질 개선 추이',
            xaxis_title='반복 횟수',
            yaxis_title='품질 점수 (%)',
            height=400,
            template='plotly_white',
            hovermode='x unified',
            showlegend=False
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
    
    def process_document(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process document through the writing pipeline"""
        if not self.loop_agent:
            return {"error": "Agent not initialized"}
        
        try:
            # Show processing animation
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress updates
            for i in range(5):
                progress_bar.progress((i + 1) * 20)
                status_text.text(f"처리 중... 단계 {i+1}/5")
                time.sleep(0.5)
            
            # Run the loop agent pipeline
            result = self.loop_agent.run(input_data)
            
            progress_bar.progress(100)
            status_text.text("완료!")
            
            # Perform final validation
            if result.get("success"):
                final_doc = result.get("final_document", "")
                
                # Validate terms and compliance
                term_validation = validate_financial_terms(final_doc)
                compliance_check = check_compliance(
                    final_doc, 
                    input_data.get("document_type", "email")
                )
                
                # Calculate final quality score
                final_score = calculate_quality_score(
                    final_doc,
                    term_validation,
                    compliance_check
                )
                
                result["validation"] = {
                    "terms": term_validation,
                    "compliance": compliance_check,
                    "final_score": final_score
                }
                
                # Update stats
                self._update_stats(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            return {"error": str(e)}
    
    def _update_stats(self, result: Dict[str, Any]):
        """Update statistics"""
        stats = st.session_state.stats
        stats['total_documents'] += 1
        
        # Update average quality
        current_quality = result.get('quality_score', 0)
        stats['avg_quality'] = (
            (stats['avg_quality'] * (stats['total_documents'] - 1) + current_quality) 
            / stats['total_documents']
        )
        
        # Update average iterations
        current_iter = result.get('iterations', 0)
        stats['avg_iterations'] = (
            (stats['avg_iterations'] * (stats['total_documents'] - 1) + current_iter)
            / stats['total_documents']
        )
        
        # Update total time
        stats['total_time'] += result.get('total_time', 0)
    
    def render_sidebar(self):
        """Render premium sidebar"""
        with st.sidebar:
            st.markdown("## ⚙️ 설정")
            
            # Document type selection with icons
            doc_types = {
                "email": "📧 이메일",
                "proposal": "📋 제안서",
                "product_description": "📦 상품 설명서",
                "compliance_report": "📊 규정 보고서",
                "official_letter": "📜 공식 문서"
            }
            
            doc_type = st.selectbox(
                "문서 유형",
                options=list(doc_types.keys()),
                format_func=lambda x: doc_types[x]
            )
            
            # Tone selection with visual indicators
            tone_options = {
                "formal": "🎩 격식있는",
                "professional": "💼 전문적인",
                "professional_friendly": "🤝 전문적이면서 친근한",
                "friendly": "😊 친근한"
            }
            
            tone = st.select_slider(
                "톤앤매너",
                options=list(tone_options.keys()),
                value="professional",
                format_func=lambda x: tone_options[x]
            )
            
            st.divider()
            
            # Advanced settings
            with st.expander("🎛️ 고급 설정"):
                quality_threshold = st.slider(
                    "품질 임계값",
                    min_value=0.5,
                    max_value=1.0,
                    value=config.QUALITY_THRESHOLD,
                    step=0.05,
                    help="목표 품질 점수"
                )
                
                max_iterations = st.number_input(
                    "최대 반복 횟수",
                    min_value=1,
                    max_value=10,
                    value=config.MAX_ITERATIONS,
                    help="품질 개선을 위한 최대 반복 횟수"
                )
                
                temperature = st.slider(
                    "창의성 수준",
                    min_value=0.0,
                    max_value=1.0,
                    value=config.TEMPERATURE,
                    step=0.1,
                    help="높을수록 더 창의적인 결과"
                )
            
            st.divider()
            
            # Theme toggle
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🌙 다크 모드", use_container_width=True):
                    st.session_state.theme = 'dark'
            with col2:
                if st.button("☀️ 라이트 모드", use_container_width=True):
                    st.session_state.theme = 'light'
            
            st.divider()
            
            # Export options
            st.markdown("### 📤 내보내기")
            if st.button("📊 통계 리포트 생성", use_container_width=True):
                self._generate_report()
            
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.history = []
                st.session_state.current_result = None
                st.rerun()
        
        return doc_type, tone, quality_threshold, max_iterations, temperature
    
    def _generate_report(self):
        """Generate statistics report"""
        stats = st.session_state.stats
        report = f"""
# AI Financial Writer Pro - 통계 리포트
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 주요 지표
- 총 생성 문서: {stats['total_documents']}개
- 평균 품질 점수: {stats['avg_quality']:.1%}
- 평균 반복 횟수: {stats['avg_iterations']:.1f}회
- 총 처리 시간: {stats['total_time']:.0f}초

## 성과 분석
- 품질 목표 달성률: {(stats['avg_quality'] / 0.9 * 100):.1f}%
- 효율성 지수: {(1 / max(stats['avg_iterations'], 1) * 100):.1f}%
        """
        st.download_button(
            label="📥 리포트 다운로드",
            data=report,
            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )
    
    def run(self):
        """Run the application"""
        # Load CSS
        load_css()
        
        # Apply theme
        if st.session_state.theme == 'dark':
            st.markdown('<div class="dark-mode">', unsafe_allow_html=True)
        
        # Render header
        self.render_header()
        
        # Render stats dashboard
        self.render_stats_dashboard()
        
        # Get sidebar settings
        doc_type, tone, quality_threshold, max_iterations, temperature = self.render_sidebar()
        
        # Main content tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "✍️ 문서 작성", 
            "📊 비교 분석", 
            "📈 성과 지표",
            "📚 문서 이력"
        ])
        
        with tab1:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📝 문서 요구사항")
                
                requirements = st.text_area(
                    "요구사항 입력",
                    placeholder="작성하고자 하는 문서의 내용과 요구사항을 입력하세요...",
                    height=200,
                    label_visibility="collapsed"
                )
                
                with st.expander("📎 추가 정보"):
                    recipient = st.text_input("수신자", placeholder="예: 김철수 고객님")
                    subject = st.text_input("제목", placeholder="예: VIP 혜택 안내")
                    additional_context = st.text_area(
                        "추가 컨텍스트",
                        placeholder="추가적인 배경 정보나 특별 요구사항...",
                        height=100
                    )
                
                if st.button("🚀 문서 생성", type="primary", use_container_width=True):
                    if requirements:
                        # Prepare input data
                        input_data = {
                            "document_type": doc_type,
                            "requirements": requirements,
                            "tone": tone,
                            "recipient": recipient,
                            "subject": subject,
                            "additional_context": additional_context,
                            "quality_threshold": quality_threshold,
                            "max_iterations": max_iterations,
                            "temperature": temperature
                        }
                        
                        # Process document
                        with st.spinner("AI가 문서를 작성하고 있습니다..."):
                            result = self.process_document(input_data)
                        
                        # Store results
                        st.session_state.current_result = result
                        st.session_state.history.append({
                            "timestamp": datetime.now().isoformat(),
                            "input": input_data,
                            "result": result
                        })
                        
                        if result.get("success"):
                            st.success("✅ 문서 생성 완료!")
                            st.balloons()
                        else:
                            st.error(f"❌ 오류: {result.get('error')}")
                    else:
                        st.warning("⚠️ 문서 요구사항을 입력해주세요.")
            
            with col2:
                st.markdown("### 📄 생성된 문서")
                
                if st.session_state.current_result and st.session_state.current_result.get("success"):
                    result = st.session_state.current_result
                    
                    # Display final document
                    st.text_area(
                        "최종 문서",
                        value=result.get("final_document", ""),
                        height=400,
                        label_visibility="collapsed"
                    )
                    
                    # Display metrics
                    col2_1, col2_2, col2_3 = st.columns(3)
                    with col2_1:
                        st.metric(
                            "품질 점수",
                            f"{result.get('quality_score', 0):.1%}",
                            f"+{(result.get('quality_score', 0) - 0.7) * 100:.0f}%"
                        )
                    with col2_2:
                        st.metric(
                            "반복 횟수",
                            result.get("iterations", 0),
                            f"{result.get('iterations', 0) - 3}"
                        )
                    with col2_3:
                        st.metric(
                            "처리 시간",
                            f"{result.get('total_time', 0):.1f}s",
                            f"-{max(0, 60 - result.get('total_time', 0)):.0f}s"
                        )
                    
                    # Download options
                    col2_4, col2_5 = st.columns(2)
                    with col2_4:
                        st.download_button(
                            label="📥 문서 다운로드",
                            data=result["final_document"],
                            file_name=f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with col2_5:
                        st.download_button(
                            label="📊 전체 결과 (JSON)",
                            data=json.dumps(result, ensure_ascii=False, indent=2),
                            file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                else:
                    st.info("📝 문서를 생성하려면 왼쪽에서 요구사항을 입력하고 '문서 생성' 버튼을 클릭하세요.")
        
        with tab2:
            if st.session_state.current_result and st.session_state.current_result.get("success"):
                result = st.session_state.current_result
                history = result.get("history", [])
                
                if history and len(history) > 0:
                    # Get first draft and final version
                    first_draft = history[0]['result'].get('draft', '')
                    final_doc = result.get('final_document', '')
                    
                    # Render comparison
                    self.render_document_comparison(first_draft, final_doc)
                    
                    # Show improvement metrics
                    st.markdown("### 📊 개선 지표")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        initial_score = history[0]['result'].get('quality_score', 0)
                        final_score = result.get('quality_score', 0)
                        improvement = (final_score - initial_score) * 100
                        st.metric(
                            "품질 개선도",
                            f"+{improvement:.1f}%",
                            f"초기: {initial_score:.1%} → 최종: {final_score:.1%}"
                        )
                    
                    with col2:
                        word_count_initial = len(first_draft.split())
                        word_count_final = len(final_doc.split())
                        st.metric(
                            "단어 수 변화",
                            f"{word_count_final - word_count_initial:+d}",
                            f"{word_count_initial} → {word_count_final}"
                        )
                    
                    with col3:
                        iterations = result.get('iterations', 0)
                        st.metric(
                            "개선 반복",
                            f"{iterations}회",
                            "최적화 완료"
                        )
                else:
                    st.info("비교할 문서 이력이 없습니다.")
            else:
                st.info("먼저 문서를 생성해주세요.")
        
        with tab3:
            if st.session_state.history:
                # Quality trend chart
                st.markdown("### 📈 품질 추이")
                
                # Get latest result with history
                if st.session_state.current_result and st.session_state.current_result.get("history"):
                    self.render_quality_chart(st.session_state.current_result["history"])
                
                # Performance metrics
                st.markdown("### ⚡ 성능 지표")
                
                # Create performance chart
                fig = go.Figure()
                
                # Add traces for different metrics
                iterations_data = [h['result'].get('iterations', 0) for h in st.session_state.history]
                time_data = [h['result'].get('total_time', 0) for h in st.session_state.history]
                quality_data = [h['result'].get('quality_score', 0) * 100 for h in st.session_state.history]
                
                fig.add_trace(go.Bar(
                    name='반복 횟수',
                    x=list(range(1, len(iterations_data) + 1)),
                    y=iterations_data,
                    marker_color='lightblue',
                    yaxis='y'
                ))
                
                fig.add_trace(go.Scatter(
                    name='품질 점수 (%)',
                    x=list(range(1, len(quality_data) + 1)),
                    y=quality_data,
                    mode='lines+markers',
                    marker_color='purple',
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    title='문서별 성능 지표',
                    xaxis=dict(title='문서 번호'),
                    yaxis=dict(title='반복 횟수', side='left'),
                    yaxis2=dict(title='품질 점수 (%)', overlaying='y', side='right'),
                    hovermode='x unified',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("아직 생성된 문서가 없습니다.")
        
        with tab4:
            if st.session_state.history:
                st.markdown("### 📚 문서 생성 이력")
                
                # Display history in reverse order (newest first)
                for idx, item in enumerate(reversed(st.session_state.history), 1):
                    with st.expander(
                        f"📄 문서 #{len(st.session_state.history) - idx + 1} - "
                        f"{datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M')}"
                    ):
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            st.markdown("**입력 정보**")
                            st.write(f"문서 유형: {item['input']['document_type']}")
                            st.write(f"톤: {item['input']['tone']}")
                            st.write(f"요구사항: {item['input']['requirements'][:100]}...")
                        
                        with col2:
                            st.markdown("**결과**")
                            result = item['result']
                            if result.get('success'):
                                st.write(f"품질 점수: {result.get('quality_score', 0):.1%}")
                                st.write(f"반복 횟수: {result.get('iterations', 0)}")
                                st.write(f"처리 시간: {result.get('total_time', 0):.1f}초")
                                
                                # Preview button
                                if st.button(f"미리보기", key=f"preview_{idx}"):
                                    st.text_area(
                                        "문서 내용",
                                        value=result.get('final_document', ''),
                                        height=200,
                                        key=f"doc_{idx}"
                                    )
                            else:
                                st.error(f"오류: {result.get('error')}")
            else:
                st.info("아직 생성된 문서가 없습니다.")


def main():
    """Main application entry point"""
    app = PremiumFinancialWritingApp()
    app.run()


if __name__ == "__main__":
    main()