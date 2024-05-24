패키지 목록 다운받기
```
pip install -r requirements.txt
pip3 install -r requirements.txt
```
패키지 목록 업데이트
```
pip freeze > requirements.txt
pip3 freeze > requirements.txt
```

secrets.json 파일 만들기

```json
{
    "DATABASE_URL": {
        "user": "",
        "password": "",
        "host": "",
        "port": ,
        "dbname": ""
    }
}
```
실행
```
uvicorn app.main:app --reload
```
