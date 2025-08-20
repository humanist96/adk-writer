"""
Test script for the Financial Writing AI Pipeline
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import config
from src.agents.loop_agent import LoopAgent
from src.tools.custom_tools import (
    validate_financial_terms,
    check_compliance,
    calculate_quality_score
)


def test_pipeline():
    """Test the complete writing pipeline"""
    
    # Load environment variables
    load_dotenv()
    
    # Validate configuration
    try:
        config.validate()
        print("✅ Configuration validated successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Initialize LoopAgent
    print("\n🚀 Initializing LoopAgent...")
    loop_agent = LoopAgent(config.get_agent_config())
    
    # Test cases
    test_cases = [
        {
            "name": "투자 제안서",
            "input": {
                "document_type": "proposal",
                "requirements": """
                고액 자산가를 위한 프리미엄 펀드 투자 제안서를 작성해주세요.
                - 대상: 순자산 50억 이상 고객
                - 상품: 글로벌 헤지펀드 포트폴리오
                - 예상 수익률: 연 12-15%
                - 최소 투자금액: 10억원
                - 투자 기간: 3년
                """,
                "tone": "professional",
                "recipient": "VIP 고객",
                "subject": "프리미엄 글로벌 헤지펀드 투자 제안"
            }
        },
        {
            "name": "고객 안내 이메일",
            "input": {
                "document_type": "email",
                "requirements": """
                금리 인상에 따른 예금 상품 변경 안내 이메일을 작성해주세요.
                - 기존 상품 만기 도래 안내
                - 새로운 특판 상품 소개
                - 금리 우대 조건 설명
                - 방문 예약 유도
                """,
                "tone": "professional_friendly",
                "recipient": "김철수 고객님",
                "subject": "특별 금리 우대 상품 안내"
            }
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"테스트 {i}: {test_case['name']}")
        print('='*60)
        
        # Run pipeline
        print("📝 문서 생성 중...")
        result = loop_agent.run(test_case['input'])
        
        if result.get("success"):
            print(f"✅ 성공!")
            print(f"   - 반복 횟수: {result['iterations']}")
            print(f"   - 품질 점수: {result['quality_score']:.2%}")
            print(f"   - 소요 시간: {result['total_time']:.2f}초")
            print(f"   - 종료 사유: {result['exit_reason']}")
            
            # Validate final document
            final_doc = result['final_document']
            print("\n📋 최종 문서 검증:")
            
            # Term validation
            term_validation = validate_financial_terms(final_doc)
            print(f"   - 금융 용어: {term_validation['score']:.2%}")
            
            # Compliance check
            compliance = check_compliance(final_doc, test_case['input']['document_type'])
            print(f"   - 규정 준수: {'✅' if compliance['compliant'] else '❌'} ({compliance['score']:.2%})")
            
            # Final quality score
            final_score = calculate_quality_score(final_doc, term_validation, compliance)
            print(f"   - 최종 점수: {final_score:.2%}")
            
            # Show document preview
            print("\n📄 문서 미리보기 (처음 500자):")
            print("-" * 40)
            print(final_doc[:500] + "..." if len(final_doc) > 500 else final_doc)
            print("-" * 40)
            
        else:
            print(f"❌ 실패: {result.get('error')}")
    
    print(f"\n{'='*60}")
    print("테스트 완료!")
    print('='*60)


def test_individual_agents():
    """Test individual agents separately"""
    from src.agents.base_agents import (
        DraftWriterAgent,
        CriticAgent,
        RefinerAgent
    )
    
    print("\n" + "="*60)
    print("개별 에이전트 테스트")
    print("="*60)
    
    model_config = config.get_agent_config()
    
    # Test DraftWriterAgent
    print("\n1. DraftWriterAgent 테스트")
    draft_agent = DraftWriterAgent(model_config)
    draft_result = draft_agent.process({
        "document_type": "email",
        "requirements": "신규 펀드 상품 출시 안내",
        "tone": "professional"
    })
    print(f"   ✅ 초안 생성 완료 (길이: {len(draft_result.content)}자)")
    
    # Test CriticAgent
    print("\n2. CriticAgent 테스트")
    critic_agent = CriticAgent(model_config)
    critic_result = critic_agent.process({
        "draft": draft_result.content,
        "document_type": "email"
    })
    print(f"   ✅ 비평 완료 (점수: {critic_result.quality_score:.2%})")
    print(f"   - 발견된 문제: {len(critic_result.issues_found)}개")
    print(f"   - 제안 사항: {len(critic_result.suggestions)}개")
    
    # Test RefinerAgent
    print("\n3. RefinerAgent 테스트")
    refiner_agent = RefinerAgent(model_config)
    refiner_result = refiner_agent.process({
        "draft": draft_result.content,
        "critique": critic_result.content,
        "document_type": "email",
        "previous_score": critic_result.quality_score
    })
    print(f"   ✅ 정제 완료 (개선된 점수: {refiner_result.quality_score:.2%})")


def test_custom_tools():
    """Test custom tool functions"""
    print("\n" + "="*60)
    print("커스텀 도구 테스트")
    print("="*60)
    
    sample_text = """
    안녕하십니까 고객님,
    
    이번에 출시된 글로벌 주식형 펀드는 높은 수익률을 보장합니다.
    연 20% 이상의 확실한 수익을 약속드리며, 원금 손실은 전혀 없습니다.
    
    투자 포트폴리오는 미국 주식 50%, 유럽 채권 30%, 신흥시장 20%로 구성됩니다.
    과거 3년간 평균 수익률은 18%였습니다.
    
    감사합니다.
    """
    
    # Test term validation
    print("\n1. 금융 용어 검증")
    term_result = validate_financial_terms(sample_text)
    print(f"   - 점수: {term_result['score']:.2%}")
    print(f"   - 발견된 용어: {len(term_result['found_terms'])}개")
    
    # Test compliance
    print("\n2. 규정 준수 검사")
    compliance_result = check_compliance(sample_text, "proposal")
    print(f"   - 준수 여부: {'✅' if compliance_result['compliant'] else '❌'}")
    print(f"   - 금지 용어: {compliance_result['prohibited_terms_found']}")
    print(f"   - 필요한 고지: {compliance_result['required_disclaimers']}")
    
    # Test quality score
    print("\n3. 품질 점수 계산")
    quality = calculate_quality_score(sample_text)
    print(f"   - 종합 점수: {quality:.2%}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Financial Writing AI Pipeline")
    parser.add_argument("--full", action="store_true", help="Run full pipeline test")
    parser.add_argument("--agents", action="store_true", help="Test individual agents")
    parser.add_argument("--tools", action="store_true", help="Test custom tools")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.all or (not any([args.full, args.agents, args.tools])):
        # Run all tests by default
        test_custom_tools()
        test_individual_agents()
        test_pipeline()
    else:
        if args.tools:
            test_custom_tools()
        if args.agents:
            test_individual_agents()
        if args.full:
            test_pipeline()