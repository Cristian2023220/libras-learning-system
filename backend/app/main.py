from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.auth import router as auth_router
from backend.app.api.trilhas import router as trilhas_router
from backend.app.api.progresso import router as progresso_router

app = FastAPI(
    title="Sinaliza API - Plataforma Educacional de LIBRAS",
    description="API REST para autenticação, trilhas curriculares e persistência de métricas de Edge AI.",
    version="1.0.0"
)

# Configuração de CORS para comunicação fluida com o frontend Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos Roteadores da Aplicação
app.include_router(auth_router, prefix="/api")
app.include_router(trilhas_router, prefix="/api")
app.include_router(progresso_router, prefix="/api")

@app.get("/", tags=["Diagnóstico"])
def root():
    return {
        "status": "online",
        "projeto": "Sinaliza - LIBRAS Learning System",
        "documentacao": "/docs"
    }