# Usage

1. Run the FastAPI application :
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
please note that if you are using the api internally and don't want to expose it publically use this instead 
```bash
uvicorn api.main:app --reload
```

2. Open your browser and navigate to `http://server-ip:8000/docs` to access the interactive API documentation provided by Swagger UI.

[Return to README.md](../README.md)
