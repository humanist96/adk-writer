"""
Streamlit Cloud Deployment Version - AI Financial Writer Pro
Multi-Model Support: Anthropic Claude, OpenAI GPT, Google Gemini
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

# Check if multi-model support is available
try:
    from src.agents.multi_model_agents import (
        ModelFactory,
        MultiModelAgent,
        MultiModelAgentResponse
    )
    MULTI_MODEL_SUPPORT = True
except ImportError:
    MULTI_MODEL_SUPPORT = False
    from src.agents.loop_agent import LoopAgent

from src.tools.custom_tools import (
    validate_financial_terms,
    check_compliance,
    calculate_quality_score
)

# Configure page
st.set_page_config(
    page_title="AI Financial Writer Pro",
    page_icon="💼",
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

class FinancialWritingApp:
    """Financial Writing AI Application"""
    
    def __init__(self):
        self.config = config
        self.loop_agent = None
        self._initialize_agent()
        self._initialize_session_state()
    
    def _initialize_agent(self):
        """Initialize the LoopAgent"""
        try:
            config.validate()
            self.loop_agent = LoopAgent(config.get_agent_config())
        except Exception as e:
            st.error(f"초기화 실패: {str(e)}")
            st.stop()
    
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
                'total_time': 0
            }
    
    def render_header(self):
        """Render header"""
        st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0; font-size: 2.5rem;">💼 AI Financial Writer Pro</h1>
            <p style="margin-top: 0.5rem; opacity: 0.9;">
                차세대 금융 문서 작성 AI 플랫폼 | Powered by Google Gemini
            </p>
        </div>
        """, unsafe_allow_html=True)
    
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
            st.metric(
                "총 처리 시간",
                f"{st.session_state.stats['total_time']:.0f}초",
                None
            )
    
    def process_document(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process document through the pipeline"""
        if not self.loop_agent:
            return {"error": "Agent not initialized"}
        
        try:
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress
            for i in range(3):
                progress_bar.progress((i + 1) * 33)
                status_text.text(f"처리 중... 단계 {i+1}/3")
                time.sleep(0.5)
            
            # Run the loop agent
            result = self.loop_agent.run(input_data)
            
            progress_bar.progress(100)
            status_text.text("완료!")
            
            # Validation
            if result.get("success"):
                final_doc = result.get("final_document", "")
                
                term_validation = validate_financial_terms(final_doc)
                compliance_check = check_compliance(final_doc, input_data.get("document_type", "email"))
                final_score = calculate_quality_score(final_doc, term_validation, compliance_check)
                
                result["validation"] = {
                    "terms": term_validation,
                    "compliance": compliance_check,
                    "final_score": final_score
                }
                
                # Update stats
                self._update_stats(result)
            
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
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
        
        # Stats
        self.render_stats()
        
        # Sidebar
        with st.sidebar:
            st.markdown("## ⚙️ 설정")
            
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
            
            with st.expander("고급 설정"):
                quality_threshold = st.slider(
                    "품질 임계값",
                    min_value=0.5,
                    max_value=1.0,
                    value=config.QUALITY_THRESHOLD,
                    step=0.05
                )
                
                max_iterations = st.number_input(
                    "최대 반복 횟수",
                    min_value=1,
                    max_value=10,
                    value=config.MAX_ITERATIONS
                )
            
            st.divider()
            
            if st.button("🔄 초기화"):
                st.session_state.history = []
                st.session_state.current_result = None
                st.rerun()
        
        # Main content
        tab1, tab2, tab3 = st.tabs(["✍️ 문서 작성", "📊 비교 분석", "📚 이력"])
        
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
                        input_data = {
                            "document_type": doc_type,
                            "requirements": requirements,
                            "tone": tone,
                            "recipient": recipient,
                            "subject": subject,
                            "additional_context": additional_context,
                            "quality_threshold": quality_threshold,
                            "max_iterations": max_iterations
                        }
                        
                        with st.spinner("AI가 문서를 작성 중입니다..."):
                            result = self.process_document(input_data)
                        
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
                        st.warning("요구사항을 입력해주세요.")
            
            with col2:
                st.markdown("### 📄 생성된 문서")
                
                if st.session_state.current_result and st.session_state.current_result.get("success"):
                    result = st.session_state.current_result
                    
                    st.text_area(
                        "최종 문서",
                        value=result.get("final_document", ""),
                        height=400,
                        label_visibility="collapsed"
                    )
                    
                    col2_1, col2_2, col2_3 = st.columns(3)
                    with col2_1:
                        st.metric("품질 점수", f"{result.get('quality_score', 0):.1%}")
                    with col2_2:
                        st.metric("반복 횟수", result.get("iterations", 0))
                    with col2_3:
                        st.metric("처리 시간", f"{result.get('total_time', 0):.1f}초")
                    
                    st.download_button(
                        label="📥 문서 다운로드",
                        data=result["final_document"],
                        file_name=f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.info("문서를 생성하려면 왼쪽에서 요구사항을 입력하고 '문서 생성' 버튼을 클릭하세요.")
        
        with tab2:
            if st.session_state.current_result and st.session_state.current_result.get("success"):
                result = st.session_state.current_result
                history = result.get("history", [])
                
                if history and len(history) > 0:
                    st.markdown("### 📊 초안 vs 최종본 비교")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📝 초안")
                        first_draft = history[0]['result'].get('draft', '')
                        st.text_area("초안", value=first_draft, height=300, label_visibility="collapsed")
                    
                    with col2:
                        st.markdown("#### ✨ 최종본")
                        final_doc = result.get('final_document', '')
                        st.text_area("최종본", value=final_doc, height=300, label_visibility="collapsed")
                    
                    # Metrics
                    st.markdown("### 📈 개선 지표")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        initial_score = history[0]['result'].get('quality_score', 0)
                        final_score = result.get('quality_score', 0)
                        improvement = (final_score - initial_score) * 100
                        st.metric("품질 개선도", f"+{improvement:.1f}%")
                    
                    with col2:
                        st.metric("반복 횟수", f"{result.get('iterations', 0)}회")
                    
                    with col3:
                        st.metric("처리 시간", f"{result.get('total_time', 0):.1f}초")
            else:
                st.info("먼저 문서를 생성해주세요.")
        
        with tab3:
            if st.session_state.history:
                st.markdown("### 📚 문서 생성 이력")
                
                for idx, item in enumerate(reversed(st.session_state.history), 1):
                    with st.expander(f"문서 #{len(st.session_state.history) - idx + 1} - {datetime.fromisoformat(item['timestamp']).strftime('%Y-%m-%d %H:%M')}"):
                        st.write(f"**문서 유형**: {item['input']['document_type']}")
                        st.write(f"**톤**: {item['input']['tone']}")
                        st.write(f"**품질 점수**: {item['result'].get('quality_score', 0):.1%}")
                        st.write(f"**반복 횟수**: {item['result'].get('iterations', 0)}")
            else:
                st.info("아직 생성된 문서가 없습니다.")


def main():
    """Main entry point"""
    app = FinancialWritingApp()
    app.run()


if __name__ == "__main__":
    main()