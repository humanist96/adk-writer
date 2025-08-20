# 🚀 Streamlit Cloud 배포 가이드

## 📋 배포 방법

### 1. Streamlit Cloud 접속
1. https://share.streamlit.io/ 접속
2. GitHub 계정으로 로그인

### 2. 새 앱 배포
1. **"New app"** 버튼 클릭
2. **Repository**: `humanist96/adk-writer` 선택
3. **Branch**: `main` 선택
4. **Main file path**: `app_multi_model.py` 입력 (멀티 모델 버전) 또는 `app.py` (기본 버전)

### 3. Secrets 설정 (중요!)

**Settings → Secrets** 탭에서 다음 내용을 입력:

```toml
# Google AI Configuration
[google]
api_key = "your_google_api_key_here"
project_id = "your_project_id_here"
location = "us-central1"

# Anthropic Configuration
[anthropic]
api_key = "your_anthropic_api_key_here"
model = "claude-3-5-sonnet-20241022"

# OpenAI Configuration
[openai]
api_key = "your_openai_api_key_here"
model = "gpt-4-turbo"

# Model Settings
[model]
name = "gemini-1.5-flash"
temperature = 0.7
max_output_tokens = 2048

# Application Settings
[app]
max_iterations = 5
quality_threshold = 0.9
timeout_seconds = 300
default_provider = "Anthropic"
```

### 4. Deploy 클릭
- **"Deploy!"** 버튼 클릭
- 배포 진행 상황 모니터링 (약 3-5분 소요)

## 🎯 배포 옵션

### 옵션 1: 멀티 모델 버전 (권장)
- **Main file**: `app_multi_model.py`
- **특징**: Anthropic Claude, OpenAI GPT, Google Gemini 모두 지원
- **장점**: 다양한 AI 모델 선택 가능, 모델 비교 기능

### 옵션 2: 기본 버전
- **Main file**: `app.py`
- **특징**: Google Gemini 기반
- **장점**: 심플한 인터페이스, 빠른 로딩

## 🌐 배포 후 URL
배포가 완료되면 다음과 같은 URL이 생성됩니다:
```
https://[app-name].streamlit.app/
```

## ⚠️ 주의사항
1. API 키는 반드시 Secrets에 입력 (코드에 하드코딩 금지)
2. 무료 플랜: 1GB RAM 제한
3. 월 사용량 제한 있음

## 🔧 문제 해결

### API Key 오류
- Secrets가 올바르게 입력되었는지 확인
- API 키 권한 확인

### 모듈 import 오류
- requirements.txt 확인
- Python 버전 호환성 확인

### 메모리 오류
- 무료 플랜 한계일 수 있음
- 유료 플랜 고려

## 📱 사용 방법
1. 배포된 URL 접속
2. AI 모델 선택 (멀티 모델 버전)
3. 문서 요구사항 입력
4. 생성 버튼 클릭
5. 결과 확인 및 다운로드

## 🆘 지원
- Streamlit 문서: https://docs.streamlit.io/
- GitHub Issues: https://github.com/humanist96/adk-writer/issues