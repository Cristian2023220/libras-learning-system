from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.core.security import obter_usuario_atual
from backend.app.models.entities import Usuario, Nivel, Licao, ProgressoNivel
from backend.app.schemas.schemas import NivelResponse, LicaoResponse

router = APIRouter(prefix="/trilhas", tags=["Trilhas e Lições"])

@router.get("", response_model=List[NivelResponse])
def listar_trilhas(usuario: Usuario = Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    niveis = db.query(Nivel).order_by(Nivel.ordem).all()
    resultado = []

    for nivel in niveis:
        total_licoes = len(nivel.licoes)
        prog = db.query(ProgressoNivel).filter(
            ProgressoNivel.usuario_id == usuario.id,
            ProgressoNivel.nivel_id == nivel.id
        ).first()

        resultado.append(NivelResponse(
            id=nivel.id,
            slug=nivel.slug,
            titulo=nivel.titulo,
            dificuldade=nivel.dificuldade,
            descricao=nivel.descricao,
            ordem=nivel.ordem,
            icone_tag=nivel.icone_tag,
            total_licoes=total_licoes,
            licoes_concluidas=prog.licoes_concluidas if prog else 0,
            percentual_conclusao=prog.percentual_conclusao if prog else 0.0,
            desbloqueado=prog.desbloqueado if prog else (nivel.ordem == 1),
            licoes=nivel.licoes
        ))
    return resultado

@router.get("/licoes/{licao_id}", response_model=LicaoResponse)
def obter_detalhes_licao(licao_id: int, usuario: Usuario = Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    licao = db.query(Licao).filter(Licao.id == licao_id).first()
    if not licao:
        raise HTTPException(status_code=404, detail="Lição não encontrada.")
    return licao