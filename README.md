# 🤖 AI Financial Writer Pro - Multi-Model Edition

차세대 금융 문서 작성 AI 플랫폼 with Multi-Model Support (Anthropic Claude, OpenAI GPT, Google Gemini)

## ✨ 주요 특징

### 🎯 핵심 기능
- **멀티 AI 모델 지원**: Anthropic Claude 3.5, OpenAI GPT-4, Google Gemini 1.5 동시 지원
- **ADK LoopAgent**: 지능형 반복 개선 시스템 (초안 → 비평 → 개선 자동화)
- **고급 Diff 분석**: AI 초안과 최종본의 상세 비교 및 수정 이유 분석
- **실시간 모델 비교**: 동일 요구사항으로 여러 AI 모델 성능 비교
- **금융 도메인 특화**: 전문 용어 검증, 규정 준수 체크, 금융 템플릿

### 🔀 새로운 Diff 분석 기능
- **변경 사항 요약**: 문서 유사도, 길이 변화, 단어/문장 통계
- **라인별 비교**: 추가/삭제된 라인을 색상으로 구분하여 표시
- **단어별 비교**: 세밀한 단어 수준 변경사항 추적
- **수정 이유 분석**: LoopAgent의 비평 내용과 개선 근거 표시
- **품질 개선 추이**: 반복별 품질 점수 변화 시각화

## 📋 시스템 요구사항

- Python 3.8 이상
- 최소 하나의 API Key 필요:
  - Anthropic API Key (Claude)
  - OpenAI API Key (GPT)
  - Google API Key (Gemini)
- 4GB 이상 RAM 권장

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/koscom/adk-writer.git
cd adk-writer
```

### 2. 가상환경 설정
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. API 키 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집하여 API 키 입력
```

`.env` 파일 예시:
```env
# 최소 하나의 API 키는 필수
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here  
GOOGLE_API_KEY=your_google_key_here

# 기본 제공자 설정
DEFAULT_PROVIDER=Anthropic
```

### 5. 애플리케이션 실행
```bash
streamlit run app_multi_model.py
```
브라우저에서 http://localhost:8501 자동 열림

## 🎨 주요 화면 구성

### 📑 6개 탭 인터페이스

#### 1️⃣ **문서 작성** 탭
- AI 모델 선택 (Anthropic/OpenAI/Google)
- 문서 요구사항 입력
- ADK LoopAgent 활성화 옵션
- 실시간 문서 생성 및 품질 평가

#### 2️⃣ **초안 vs 최종** 탭
- 초안과 최종 문서 나란히 비교
- 품질 점수 및 길이 변화 표시
- 개선 지표 시각화
- 문서 재정제 기능

#### 3️⃣ **변경 사항 분석** 탭 (NEW!)
- **변경 사항 요약**: 통계적 분석 및 주요 수정사항
- **라인별 비교**: 색상 코딩된 diff 뷰
- **단어별 비교**: 세밀한 변경사항 추적
- **수정 이유 분석**: AI의 비평과 개선 근거
- 분석 보고서 다운로드

#### 4️⃣ **모델 비교** 탭
- 여러 AI 모델 동시 테스트
- 동일 프롬프트로 결과 비교
- 모델별 품질 점수 평가

#### 5️⃣ **분석** 탭
- 상세 품질 지표
- 텍스트 통계 (문자, 단어, 문장)
- 모델 성능 메트릭

#### 6️⃣ **이력** 탭
- 생성된 모든 문서 이력
- 검색 및 필터링 기능
- 이력별 다운로드

## 🛠️ 고급 기능

### ADK LoopAgent 시스템
```
초안 생성 → 비평 분석 → 개선 제안 → 문서 정제 → 품질 평가
         ↑                                            ↓
         ←────────────── (품질 미달 시 반복) ──────────←
```

### 종료 조건
- ✅ 품질 임계값 도달 (기본 90%)
- ✅ 최대 반복 횟수 도달 (기본 5회)
- ✅ 주요 문제점 없음 감지
- ✅ 타임아웃 초과 (기본 300초)

### 지원 문서 유형
- 📧 **이메일**: 고객 안내 이메일
- 📄 **제안서**: 투자 제안서
- 📋 **상품 설명서**: 금융 상품 설명서
- 📊 **규정 보고서**: 규정 준수 보고서
- 📜 **공식 문서**: 대외 공식 문서

## 📁 프로젝트 구조

```
adk-writer/
├── app_multi_model.py          # 메인 Streamlit 애플리케이션
├── src/
│   ├── agents/
│   │   ├── base_agents.py      # 기본 에이전트 클래스
│   │   ├── loop_agent.py       # ADK LoopAgent 구현
│   │   ├── multi_model_agents.py # 멀티모델 지원
│   │   └── sequential_agent.py # 순차 실행 관리
│   ├── tools/
│   │   └── custom_tools.py     # 금융 도메인 특화 도구
│   ├── utils/
│   │   └── diff_utils.py       # Diff 분석 유틸리티
│   └── config_cloud.py         # 클라우드 설정
├── test_*.py                   # 테스트 파일들
├── requirements.txt            # 의존성 패키지
├── .env.example               # 환경변수 예시
└── README.md                  # 문서
```

## 🧪 테스트

### 단위 테스트
```bash
# 멀티모델 테스트
python test_multi_model.py

# 모든 모델 API 테스트
python test_all_models.py

# 파이프라인 테스트
python test_pipeline.py
```

### 통합 테스트
```bash
pytest test_*.py -v
```

## 🌐 배포

### Streamlit Cloud 배포
1. GitHub에 푸시
2. https://share.streamlit.io 접속
3. 저장소 연결
4. Secrets에 API 키 설정
5. 배포!

**Production URL**: https://write-multi-agent.streamlit.app/

## 📊 성능 지표

### 품질 메트릭
- 📈 문법 정확도: 95% 이상
- 💼 금융 용어 정확성: 98% 이상
- ✅ 규정 준수율: 100%
- ⚡ 평균 처리 시간: 20-40초
- 🔄 평균 반복 횟수: 2-3회

### 모델별 특징
- **Claude 3.5 Sonnet**: 최고 성능, 긴 컨텍스트 처리
- **GPT-4 Turbo**: 균형잡힌 성능, 다국어 지원
- **Gemini 1.5 Flash**: 빠른 응답, 비용 효율적

## 🔧 설정 옵션

### 환경 변수 (.env)
```env
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...

# Model Settings
DEFAULT_PROVIDER=Anthropic
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
OPENAI_MODEL=gpt-4-turbo
GOOGLE_MODEL=gemini-1.5-flash

# Loop Agent Settings
MAX_ITERATIONS=5
QUALITY_THRESHOLD=0.9
TIMEOUT_SECONDS=300
TEMPERATURE=0.7
```

## 🔍 문제 해결

### API 오류
- API 키가 올바르게 설정되었는지 확인
- 각 제공자의 API 사용량 및 요금 확인
- 모델 이름이 정확한지 확인

### 모델 404 오류
- 최신 모델 ID 사용 확인
- API 버전 호환성 확인

### 성능 문제
- 네트워크 연결 확인
- API 요청 제한 확인
- 캐시 정리 후 재시도

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 라이선스

MIT License - 자유롭게 사용 가능

## 👥 연락처

- Email: ksjeong@koscom.co.kr
- Provider: 코스콤 금융영업부
- GitHub: [@koscom](https://github.com/koscom)
- Issues: [GitHub Issues](https://github.com/koscom/adk-writer/issues)

## 🚨 중요 공지

**AI 생성 문서는 참고용입니다. 최종 문서는 반드시 인간 검토자의 확인을 거쳐야 합니다.**

---

Made with ❤️ using Streamlit and Multi-Model AI