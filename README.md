# Repository content
Jachkars Virtual museum's web page.
https://github.com/AzcarGabriel/jachkar-museum


## Backend

### Instalation
Using python 3.11.5, in the backend folder run
```
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
```
### Deploy
```
    uvicorn main:app --reload
```

## Frontend
### Instalation:
In the frontend folder, run:
```
    npm install
```
### Dev
```
    npm run dev
```

### Prod
run
```
    npm run build
```
copy the content from `frontend/build` to `backend/static`