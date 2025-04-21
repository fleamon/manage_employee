# manage_employee

## 개발환경

virtual env

- Python 3.12.7
- pip latest

## 설치

```
pip install -r requirements.txt
```

## 데이터베이스

- "Google Cloud Console" 에서 api 사용 세팅 후 google spread sheet로 관리됨

## web deploy 환경

- https://streamlit.io/cloud
- credentials 은 Streamlit Cloud의 해당 app secret으로 저장

## local 테스트 실행

- local test 아래 credentials 로 시작하는 라인 주석 해제 후
```bash
streamlit run app.py
```
