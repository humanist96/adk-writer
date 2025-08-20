# Streamlit Cloud 배포 가이드

## 📋 배포 준비 사항

### 1. GitHub 리포지토리 설정
- Repository: `https://github.com/humanist96/adk-writer`
- Branch: `main`

### 2. Streamlit Cloud 계정
- https://streamlit.io/cloud 에서 GitHub 계정으로 로그인

## 🚀 배포 단계

### Step 1: GitHub에 코드 푸시
```bash
git add .
git commit -m "Initial commit: AI Financial Writer Pro"
git branch -M main
git remote add origin https://github.com/humanist96/adk-writer.git
git push -u origin main
```

### Step 2: Streamlit Cloud 설정

1. **Streamlit Cloud 대시보드 접속**
   - https://share.streamlit.io/ 접속
   - GitHub 계정으로 로그인

2. **새 앱 배포**
   - "New app" 버튼 클릭
   - Repository: `humanist96/adk-writer` 선택
   - Branch: `main` 선택
   - Main file path: `app.py` 입력

3. **Advanced settings**
   - Python version: 3.12 (또는 3.8+)
   - 클릭하여 확장

### Step 3: Secrets 설정

Streamlit Cloud 앱 설정에서 "Secrets" 탭을 클릭하고 다음 내용 입력:

```toml
[google]
api_key = "YOUR_GOOGLE_API_KEY"
project_id = "YOUR_PROJECT_ID"
location = "us-central1"

[model]
name = "gemini-1.5-flash"
temperature = 0.7
max_output_tokens = 2048

[app]
max_iterations = 5
quality_threshold = 0.9
timeout_seconds = 300
```

### Step 4: 배포 시작
- "Deploy!" 버튼 클릭
- 배포 진행 상황 모니터링 (약 3-5분 소요)

## 🔧 환경 설정

### requirements.txt
이미 설정되어 있음:
- google-generativeai
- streamlit
- plotly
- loguru
- python-dotenv
- 기타 필요 패키지

### 폴더 구조
```
adk-writer/
├── app.py                 # Streamlit Cloud 메인 파일
├── requirements.txt       # 패키지 의존성
├── .streamlit/
│   └── config.toml       # Streamlit 설정
├── src/
│   ├── config_cloud.py   # 클라우드 설정
│   ├── agents/           # AI 에이전트
│   └── tools/            # 커스텀 도구
├── static/               # 정적 파일
└── README.md             # 프로젝트 문서
```

## 🌐 배포 URL

배포 완료 후 다음과 같은 URL이 생성됩니다:
```
https://[app-name].streamlit.app/
```

## 🔍 문제 해결

### 1. API Key 오류
- Streamlit Cloud Secrets에 Google API Key가 올바르게 입력되었는지 확인
- API Key 권한 확인 (Gemini API 활성화 필요)

### 2. 모듈 import 오류
- requirements.txt 파일이 올바른지 확인
- Python 버전 호환성 확인

### 3. 메모리 오류
- Streamlit Cloud 무료 플랜: 1GB RAM 제한
- 필요시 유료 플랜 고려

### 4. 빌드 실패
- 로그 확인: Streamlit Cloud 대시보드에서 "Logs" 탭
- requirements.txt 의존성 충돌 확인

## 📊 모니터링

### Streamlit Cloud 대시보드
- 앱 상태 확인
- 사용자 분석
- 리소스 사용량 모니터링
- 에러 로그 확인

### 앱 관리
- 재시작: "Reboot app" 버튼
- 설정 변경: "Settings" 탭
- Secrets 업데이트: "Secrets" 탭

## 🔐 보안 주의사항

1. **절대 하지 말아야 할 것**
   - API Key를 코드에 하드코딩
   - secrets.toml을 GitHub에 커밋
   - .env 파일을 공개 리포지토리에 포함

2. **권장 사항**
   - Streamlit Secrets 사용
   - 환경별 설정 분리
   - 정기적인 API Key 갱신

## 📱 사용자 접근

배포 완료 후:
1. 제공된 URL로 접속
2. 웹 브라우저에서 바로 사용 가능
3. 모바일 기기에서도 접근 가능

## 🆘 지원

- Streamlit 문서: https://docs.streamlit.io/
- Streamlit 포럼: https://discuss.streamlit.io/
- GitHub Issues: https://github.com/humanist96/adk-writer/issues