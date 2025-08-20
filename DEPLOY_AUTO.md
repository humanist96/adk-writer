# 🚀 Streamlit Cloud 자동 배포 가이드

## 배포 URL
앱이 이미 배포되어 있거나 곧 배포될 예정입니다:
- **URL**: https://adk-writer.streamlit.app/

## 📋 배포 상태 확인

### 1. Streamlit Cloud Dashboard
1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. "Your apps" 섹션에서 확인

### 2. 새 앱 배포 (첫 배포인 경우)
1. **New app** 버튼 클릭
2. 다음 정보 입력:
   - **Repository**: `humanist96/adk-writer`
   - **Branch**: `main`
   - **Main file path**: `app_multi_model.py`
3. **Advanced settings** 클릭

### 3. Secrets 설정 (중요!)
앱 설정에서 **Secrets** 탭 클릭 후 다음 내용 붙여넣기:

```toml
[google]
api_key = "your_google_api_key_here"
project_id = "your_project_id_here"
location = "us-central1"

[anthropic]
api_key = "your_anthropic_api_key_here"
model = "claude-3-5-sonnet-20241022"

[openai]
api_key = "your_openai_api_key_here"
model = "gpt-4-turbo-preview"

[model]
name = "gemini-1.5-flash"
temperature = 0.7
max_output_tokens = 2048

[app]
max_iterations = 5
quality_threshold = 0.9
timeout_seconds = 300
default_provider = "Anthropic"
```

### 4. Deploy 클릭
- **Deploy!** 버튼 클릭
- 배포 진행 상황 모니터링 (3-5분 소요)

## 🔄 자동 배포 설정

GitHub 리포지토리가 업데이트되면 Streamlit Cloud가 자동으로 재배포합니다.

### 이미 설정된 기능:
- ✅ GitHub 연동
- ✅ 자동 빌드 트리거
- ✅ 환경 변수 관리
- ✅ 의존성 자동 설치

## 📱 앱 접속 방법

배포 완료 후:
1. **직접 URL**: https://adk-writer.streamlit.app/
2. **대시보드**: Streamlit Cloud 대시보드에서 "View app" 클릭
3. **공유 링크**: 앱 우측 상단의 공유 버튼으로 링크 복사

## 🎯 주요 기능

### 현재 배포된 버전 기능:
- ✅ 멀티 AI 모델 지원 (Claude 3.5, GPT-4, Gemini)
- ✅ 사이드바 모델 선택기
- ✅ 초안 vs 최종 문서 비교
- ✅ 문서 재정제 기능
- ✅ 모델 간 비교
- ✅ 품질 분석 대시보드
- ✅ 문서 생성 이력 관리

## 🔧 문제 해결

### 배포 실패 시:
1. **로그 확인**: Streamlit Cloud 대시보드 → Logs
2. **의존성 확인**: requirements.txt 파일 확인
3. **Secrets 확인**: API 키가 올바른지 확인

### 일반적인 오류:
- **ModuleNotFoundError**: requirements.txt 업데이트 필요
- **API 오류**: Secrets의 API 키 확인
- **메모리 오류**: 코드 최적화 또는 유료 플랜 고려

## 📊 모니터링

### 대시보드에서 확인 가능한 정보:
- 앱 상태 (Running/Building/Error)
- 사용자 수
- 리소스 사용량
- 에러 로그
- 빌드 로그

## 🆘 지원

- **Streamlit 문서**: https://docs.streamlit.io/
- **GitHub Issues**: https://github.com/humanist96/adk-writer/issues
- **Streamlit 포럼**: https://discuss.streamlit.io/

## ✅ 배포 체크리스트

- [x] GitHub 리포지토리 준비
- [x] requirements.txt 파일 확인
- [x] app_multi_model.py 메인 파일 준비
- [x] .streamlit/config.toml 설정
- [x] Secrets 준비 (API 키)
- [ ] Streamlit Cloud에서 앱 생성
- [ ] Secrets 입력
- [ ] 배포 및 테스트

---

**참고**: API 키는 보안을 위해 반드시 Streamlit Cloud의 Secrets에만 입력하세요. 
코드에 직접 포함하거나 GitHub에 커밋하지 마세요.