from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Docling API")

app.include_router(router)
