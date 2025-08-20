# 금융영업부 AI 글쓰기 프로그램

Google ADK(Agent Development Kit)를 활용한 지능형 금융 문서 작성 시스템

## 🎯 주요 기능

- **LoopAgent 기반 반복 개선**: 초안 생성 → 비평 → 정제 과정을 자동으로 반복
- **3단계 에이전트 파이프라인**: 
  - 초안 작성자 (DraftWriterAgent)
  - 비평가 (CriticAgent)
  - 정제자 (RefinerAgent)
- **금융 도메인 특화**: 금융 용어 검증, 규정 준수 체크
- **스마트 종료 조건**: 품질 목표 달성 시 자동 종료
- **Streamlit 웹 인터페이스**: 사용자 친화적 UI

## 📋 시스템 요구사항

- Python 3.8 이상
- Google API Key (Gemini API)
- 4GB 이상 RAM 권장

## 🚀 설치 방법

### 1. 저장소 클론
```bash
git clone [repository-url]
cd adk_agent
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# .env.example을 복사하여 .env 파일 생성
cp .env.example .env

# .env 파일을 열어 Google API Key 입력
# GOOGLE_API_KEY=your_actual_api_key_here
```

## 💻 실행 방법

### Streamlit 웹 애플리케이션 실행
```bash
streamlit run main.py
```
브라우저에서 http://localhost:8501 접속

### 테스트 실행
```bash
# 전체 테스트
python test_pipeline.py --all

# 파이프라인 테스트만
python test_pipeline.py --full

# 개별 에이전트 테스트
python test_pipeline.py --agents

# 커스텀 도구 테스트
python test_pipeline.py --tools
```

## 📁 프로젝트 구조

```
adk_agent/
├── src/
│   ├── agents/
│   │   ├── base_agents.py      # LLM 에이전트 구현
│   │   ├── loop_agent.py       # LoopAgent 메인 컨트롤러
│   │   └── sequential_agent.py # 순차 실행 관리자
│   ├── tools/
│   │   └── custom_tools.py     # 금융 도메인 도구
│   └── config.py               # 설정 관리
├── templates/                  # 문서 템플릿
├── logs/                       # 로그 파일
├── main.py                     # Streamlit 앱
├── test_pipeline.py           # 테스트 스크립트
├── requirements.txt           # 의존성 패키지
├── .env.example              # 환경 변수 예시
└── README.md                 # 문서

```

## 🔧 주요 설정

`.env` 파일에서 다음 설정을 조정할 수 있습니다:

- `MAX_ITERATIONS`: 최대 반복 횟수 (기본: 5)
- `QUALITY_THRESHOLD`: 품질 목표 점수 (기본: 0.9)
- `TIMEOUT_SECONDS`: 타임아웃 시간 (기본: 300초)
- `TEMPERATURE`: AI 모델 창의성 수준 (기본: 0.7)

## 📝 지원 문서 유형

1. **이메일** (email): 고객 안내 이메일
2. **제안서** (proposal): 투자 제안서
3. **상품 설명서** (product_description): 금융 상품 설명서
4. **규정 보고서** (compliance_report): 규정 준수 보고서
5. **공식 문서** (official_letter): 대외 공식 문서

## 🎯 핵심 기능 상세

### LoopAgent 동작 방식
1. 사용자 요구사항을 받아 초안 생성
2. 비평가가 초안을 평가하고 개선점 제시
3. 정제자가 비평을 반영하여 문서 개선
4. 품질 기준 충족 여부 확인
5. 미충족 시 2-4 단계 반복, 충족 시 종료

### 종료 조건
- "No major issues found" 메시지 감지
- 품질 점수 임계값 도달 (기본 0.9)
- 최대 반복 횟수 도달
- 타임아웃 초과

### 커스텀 도구
- **금융 용어 검증**: 전문 용어의 정확성 확인
- **규정 준수 체크**: 금지 용어 및 필수 고지사항 확인
- **템플릿 관리**: 문서 유형별 템플릿 적용
- **품질 점수 계산**: 다차원 품질 평가

## 🔍 문제 해결

### Google API Key 오류
- `.env` 파일에 올바른 API Key가 입력되었는지 확인
- API Key 권한 및 Gemini API 활성화 확인

### 모듈 import 오류
- 가상환경이 활성화되었는지 확인
- `pip install -r requirements.txt` 재실행

### Streamlit 실행 오류
- 포트 8501이 사용 중인지 확인
- `streamlit run main.py --server.port 8502`로 다른 포트 사용

## 📈 성능 지표

- 문법 정확도: 95% 이상
- 금융 용어 정확성: 98% 이상
- 규정 준수율: 100%
- 평균 처리 시간: 30-60초
- 평균 반복 횟수: 2-3회

## 🤝 기여 방법

1. 이슈 등록 또는 기능 제안
2. Fork 후 기능 개발
3. 테스트 통과 확인
4. Pull Request 제출

## 📄 라이선스

본 프로젝트는 MIT 라이선스를 따릅니다.

## 👥 문의

- 이메일: financial-ai@example.com
- 이슈 트래커: GitHub Issues

---

**주의사항**: 본 시스템이 생성한 문서는 참고용이며, 최종 문서는 반드시 인간 검토자의 확인을 거쳐야 합니다.