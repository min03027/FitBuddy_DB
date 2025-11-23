# 깃허브 업로드 가이드

## 현재 상태
✅ 로컬 git 저장소 초기화 완료
✅ 첫 커밋 완료

## 깃허브에 업로드하기

### 1. 깃허브에서 새 저장소 생성
1. https://github.com 접속
2. 우측 상단 "+" 클릭 → "New repository"
3. Repository name 입력 (예: `FitBuddy`)
4. Public 또는 Private 선택
5. "Create repository" 클릭

### 2. 원격 저장소 연결 및 푸시
```bash
cd "/Users/min/Downloads/AI_BootCamp 2"

# 원격 저장소 추가 (YOUR_USERNAME과 REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 브랜치 이름을 main으로 변경 (깃허브 기본값)
git branch -M main

# 깃허브에 푸시
git push -u origin main
```

### 3. 인증
- Personal Access Token 필요할 수 있음
- 또는 SSH 키 사용 가능

## 주의사항
⚠️ 가상환경(.venv)이 커밋에 포함되었습니다. 
다음 커밋부터는 .gitignore에 의해 제외됩니다.

## 다음 단계
프론트엔드 개발 시:
1. API 서버 실행: `python -m FitBuddy.api`
2. API 문서 확인: http://localhost:8000/docs
3. 프론트엔드에서 `http://localhost:8000/api/...` 엔드포인트 사용

