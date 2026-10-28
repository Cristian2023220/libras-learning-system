from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import (
    gerar_hash_senha, verificar_senha, criar_token_acesso, obter_usuario_atual
)
from backend.app.models.entities import Usuario, Nivel, ProgressoNivel
from backend.app.schemas.schemas import UsuarioCadastro, UsuarioLogin, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/cadastro", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def cadastrar(dados: UsuarioCadastro, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.email == dados.email).first():
        raise HTTPException(status_code=400, detail="Este e-mail já está registrado na plataforma.")

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil="Exploradora iniciante",
        minutos_estudo_semana=0,
        dias_consecutivos=1,
        meta_dias_semana=5
    )
    db.add(novo_usuario)
    db.flush()

    # Inicializa o progresso para a primeira trilha cadastrada
    primeiro_nivel = db.query(Nivel).order_by(Nivel.ordem).first()
    if primeiro_nivel:
        progresso = ProgressoNivel(
            usuario_id=novo_usuario.id,
            nivel_id=primeiro_nivel.id,
            licoes_concluidas=0,
            percentual_conclusao=0.0,
            desbloqueado=True
        )
        db.add(progresso)

    db.commit()
    db.refresh(novo_usuario)

    token = criar_token_acesso({"sub": str(novo_usuario.id)})
    return {"access_token": token, "token_type": "bearer", "usuario": novo_usuario}

@router.post("/login", response_model=TokenResponse)
def login(dados: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )

    token = criar_token_acesso({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}

@router.get("/me", response_model=UsuarioResponse)
def obter_perfil(usuario: Usuario = Depends(obter_usuario_atual)):
    return usuario