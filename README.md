### CapstoneDesign Travel Web Backend
##### ( 2024. 03. 22 ~ 2024. 08. 30 )


패키지 목록 다운받기
```
pip install -r requirements.txt
pip3 install -r requirements.txt
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
    },    
    "OPENAI_API_KEY": ""
}
```

실행
```
uvicorn app.main:app --reload
```

패키지 목록 업데이트
```
pip freeze > requirements.txt
pip3 freeze > requirements.txt
```
