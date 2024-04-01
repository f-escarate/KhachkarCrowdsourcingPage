# Repository content
Jachkars Virtual museum's web page.
https://github.com/AzcarGabriel/jachkar-museum


## Backend

### Instalation
```
    pip install "fastapi[all]"
    pip install sqlalchemy
    pip install "python-jose[cryptography]"
    pip install bcrypt==4.0.1
    pip install "passlib[bcrypt]"
    pip install python-dotenv
```
### Deploy
```
    uvicorn main:app --reload
```

## Frontend
### Instalation:
Correr en la carpeta frontend
```
    npm install
```
### Dev
```
    npm run dev
```

### Prod
Correr
```
    npm run build
```
copy the content from `frontend/build` to `backend/static`