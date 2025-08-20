"""
Main application entry point for Financial Writing AI System
"""

import streamlit as st
from typing import Dict, Any
import json
from datetime import datetime
from pathlib import Path

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


class FinancialWritingApp:
    """Main application class for Financial Writing AI"""
    
    def __init__(self):
        self.config = config
        self.loop_agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the LoopAgent with configuration"""
        try:
            config.validate()
            self.loop_agent = LoopAgent(config.get_agent_config())
            logger.info("LoopAgent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LoopAgent: {str(e)}")
            st.error(f"초기화 실패: {str(e)}")
    
    def process_document(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process document through the writing pipeline
        
        Args:
            input_data: User input including document type and requirements
            
        Returns:
            Processing results including final document
        """
        if not self.loop_agent:
            return {"error": "Agent not initialized"}
        
        try:
            # Run the loop agent pipeline
            result = self.loop_agent.run(input_data)
            
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
            
            return result
            
        except Exception as e:
            logger.error(f"Document processing error: {str(e)}")
            return {"error": str(e)}


def main():
    """Streamlit UI main function"""
    st.set_page_config(
        page_title="금융영업부 AI 글쓰기 도우미",
        page_icon="📝",
        layout="wide"
    )
    
    # Initialize session state
    if 'app' not in st.session_state:
        st.session_state.app = FinancialWritingApp()
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    # Header
    st.title("📝 금융영업부 AI 글쓰기 도우미")
    st.markdown("Google ADK 기반 LoopAgent를 활용한 지능형 문서 작성 시스템")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ 설정")
        
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
        
        st.subheader("품질 기준")
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
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📥 입력")
        
        # Document requirements input
        requirements = st.text_area(
            "문서 요구사항",
            placeholder="작성하고자 하는 문서의 내용과 요구사항을 입력하세요...",
            height=200
        )
        
        # Additional context
        with st.expander("추가 정보 (선택사항)"):
            recipient = st.text_input("수신자")
            subject = st.text_input("제목")
            additional_context = st.text_area("추가 컨텍스트", height=100)
        
        # Process button
        if st.button("🚀 문서 생성", type="primary", use_container_width=True):
            if requirements:
                with st.spinner("문서를 생성하고 있습니다..."):
                    # Prepare input data
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
                    
                    # Process document
                    result = st.session_state.app.process_document(input_data)
                    
                    # Store in history
                    st.session_state.history.append({
                        "timestamp": datetime.now().isoformat(),
                        "input": input_data,
                        "result": result
                    })
                    
                    # Show success/error message
                    if result.get("success"):
                        st.success(f"✅ 문서 생성 완료! (반복: {result.get('iterations')}회)")
                    else:
                        st.error(f"❌ 오류 발생: {result.get('error')}")
            else:
                st.warning("⚠️ 문서 요구사항을 입력해주세요.")
    
    with col2:
        st.header("📤 결과")
        
        if st.session_state.history:
            latest_result = st.session_state.history[-1]["result"]
            
            if latest_result.get("success"):
                # Display final document
                st.text_area(
                    "최종 문서",
                    value=latest_result.get("final_document", ""),
                    height=400,
                    key="final_doc"
                )
                
                # Display metrics
                col2_1, col2_2, col2_3 = st.columns(3)
                with col2_1:
                    st.metric(
                        "품질 점수",
                        f"{latest_result.get('quality_score', 0):.2%}"
                    )
                with col2_2:
                    st.metric(
                        "반복 횟수",
                        latest_result.get("iterations", 0)
                    )
                with col2_3:
                    st.metric(
                        "소요 시간",
                        f"{latest_result.get('total_time', 0):.1f}초"
                    )
                
                # Validation details
                with st.expander("검증 결과"):
                    validation = latest_result.get("validation", {})
                    
                    # Terms validation
                    terms = validation.get("terms", {})
                    st.write("**금융 용어 검증**")
                    st.write(f"- 점수: {terms.get('score', 0):.2%}")
                    st.write(f"- 발견된 용어: {len(terms.get('found_terms', []))}")
                    
                    # Compliance check
                    compliance = validation.get("compliance", {})
                    st.write("**규정 준수 검사**")
                    st.write(f"- 준수 여부: {'✅ 준수' if compliance.get('compliant') else '❌ 미준수'}")
                    st.write(f"- 점수: {compliance.get('score', 0):.2%}")
                    
                    if compliance.get("issues"):
                        st.write("**발견된 문제:**")
                        for issue in compliance["issues"]:
                            st.write(f"  - {issue}")
                
                # Iteration history
                with st.expander("반복 이력"):
                    history = latest_result.get("history", [])
                    for item in history:
                        st.write(f"**반복 {item['iteration']}**")
                        st.write(f"- 품질 점수: {item['result'].get('quality_score', 0):.2%}")
                        if item['result'].get('issues'):
                            st.write(f"- 발견된 문제: {len(item['result']['issues'])}개")
                        st.divider()
            else:
                st.error(f"처리 중 오류 발생: {latest_result.get('error')}")
        else:
            st.info("📝 문서를 생성하려면 왼쪽에서 요구사항을 입력하고 '문서 생성' 버튼을 클릭하세요.")
    
    # Footer with download options
    if st.session_state.history and st.session_state.history[-1]["result"].get("success"):
        st.divider()
        col3, col4, col5 = st.columns(3)
        
        with col3:
            # Download as text
            st.download_button(
                label="📄 텍스트로 다운로드",
                data=st.session_state.history[-1]["result"]["final_document"],
                file_name=f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        
        with col4:
            # Download as JSON (full result)
            st.download_button(
                label="📊 전체 결과 다운로드 (JSON)",
                data=json.dumps(st.session_state.history[-1], ensure_ascii=False, indent=2),
                file_name=f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col5:
            # Copy to clipboard button
            if st.button("📋 클립보드에 복사"):
                st.write("문서가 클립보드에 복사되었습니다!")
                st.toast("복사 완료!", icon="✅")


if __name__ == "__main__":
    main()