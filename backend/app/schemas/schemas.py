from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- AUTENTICAÇÃO ---
class UsuarioCadastro(BaseModel):
    nome: str
    email: EmailStr
    senha: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: str
    minutos_estudo_semana: int
    dias_consecutivos: int
    meta_dias_semana: int

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse

# --- GESTOS E LIÇÕES ---
class GestoResponse(BaseModel):
    id: int
    nome: str
    rotulo_yolo: str
    categoria: str
    imagem_referencia_url: Optional[str] = None

    class Config:
        from_attributes = True

class LicaoResponse(BaseModel):
    id: int
    nivel_id: int
    titulo: str
    subtitulo: Optional[str] = None
    tipo: str
    ordem: int
    duracao_minutos: int
    video_demonstracao_url: Optional[str] = None
    gesto_alvo: Optional[GestoResponse] = None

    class Config:
        from_attributes = True

class NivelResponse(BaseModel):
    id: int
    slug: str
    titulo: str
    dificuldade: str
    descricao: Optional[str] = None
    ordem: int
    icone_tag: str
    total_licoes: Optional[int] = 0
    licoes_concluidas: Optional[int] = 0
    percentual_conclusao: Optional[float] = 0.0
    desbloqueado: Optional[bool] = True
    licoes: List[LicaoResponse] = []

    class Config:
        from_attributes = True

# --- PAINEL (MEU PAINEL DO FIGMA) ---
class DesafioItem(BaseModel):
    licao_id: int
    titulo: str
    subtitulo: str
    duracao_minutos: int
    dificuldade: str
    concluida: bool

class DashboardResponse(BaseModel):
    usuario: UsuarioResponse
    aulas_concluidas: int
    aulas_totais: int
    minutos_semana: int
    dias_consecutivos: int
    meta_dias_semana: int
    trilha_atual_titulo: str
    trilha_atual_percentual: float
    proxima_licao_id: Optional[int] = None
    proxima_licao_titulo: Optional[str] = None
    desafios_hoje: List[DesafioItem] = []

# --- HISTÓRICO DE TENTATIVAS (EDGE AI) ---
class TentativaCreate(BaseModel):
    licao_id: int
    gesto_id: int
    sucesso: bool
    confianca_obtida: float
    tempo_estabilizacao_ms: Optional[float] = 0.0

class TentativaResponse(BaseModel):
    id: int
    sucesso: bool
    data_hora: datetime
    progresso_atualizado: float

    class Config:
        from_attributes = True