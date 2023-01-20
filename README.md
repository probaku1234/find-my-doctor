## 프로젝트 소개
의사들을 검색하고 진료 요청을 보낼 수 있는 간단한 backend 서버입니다.
Django, Django Rest Framework을 이용해 구현했습니다.


## 프로젝트 세팅
python 3.8이상의 버전이 필요합니다.
아래 커맨드로 패키지들을 설치합니다.

```bash
pip install -r requirements.txt
```

## 지원하는 API
각 모델들의 기본 CRUD API는 `http://127.0.0.1:8000/api/` 에서 접근할 수 있습니다.

삭제, 수정: `http://127.0.0.1:8000/api/{model name}/{pk}`

`model name`: [`medical_department` , `business_hour`, `"treatment_request`, `doctor`, `patient`]

진료 요청 검색: `http://127.0.0.1:8000/api/treatment_request/`

진료 요청: `http://127.0.0.1:8000/api/treatment_request/{pk}/`

진료 요청 승낙: `http://127.0.0.1:8000/api/treatment_request/{pk}/accept_request/`

위의 API들은 해당 주소에 접근하면 간편하게 쓸 수 있도록 UI가 지원됩니다.

문자열을 통한 의사 검색: `http://127.0.0.1:8000/api/doctor/search_by_text`

파라미터: `query`

날짜를 통한 의사 검색: `http://127.0.0.1:8000/api/doctor/search_by_date`

파라미터: `requested_time`

위의 API들은 UI가 지원되지 않으니 매뉴얼로 요청해야 합니다.

## 데이터 삽입하기
모든 데이터는 `db.sqlite3`에 저장됩니다.

### 환자
해당 URL에서 간편하게 추가할 수 있습니다.
`http://127.0.0.1:8000/api/patient/`

### 의사
의사 데이터를 만들기 위해서는 먼저 `business_hour`와 `medical_department` 데이터를 추가해야됩니다.
아래 URL에서 추가 할 수 있습니다.
`http://127.0.0.1:8000/api/medical_department/`
`http://127.0.0.1:8000/api/business_hour/`

`http://127.0.0.1:8000/api/doctor/` 에서 추가한 시간과 진료과를 고르고 post 버튼을 누르면 새로운 데이터가 삽입됩니다.







## test
모든 테스트 코드들은 `findMyDoctor/tests.py`에 있습니다.
아래 커맨드로 테스트 코드들을 실행할 수 있습니다.
```
python manage.py test
```


