from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import obter_usuario_atual
from backend.app.models.entities import (
    Usuario, Nivel, Licao, ProgressoNivel, HistoricoTentativa
)
from backend.app.schemas.schemas import (
    DashboardResponse, DesafioItem, TentativaCreate, TentativaResponse
)

router = APIRouter(tags=["Progresso e Gamificação"])

@router.get("/painel", response_model=DashboardResponse)
def carregar_dashboard(usuario: Usuario = Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    """Retorna os dados consolidados para renderizar a tela 'Meu Painel' do Figma."""
    # Nível ativo do usuário
    progresso_ativo = (
        db.query(ProgressoNivel)
        .filter(ProgressoNivel.usuario_id == usuario.id)
        .join(Nivel)
        .order_by(Nivel.ordem)
        .first()
    )

    trilha_titulo = "Vogais em LIBRAS"
    trilha_percentual = 0.0
    proxima_licao = None

    if progresso_ativo:
        trilha_titulo = progresso_ativo.nivel.titulo
        trilha_percentual = progresso_ativo.percentual_conclusao
        proxima_licao = (
            db.query(Licao)
            .filter(Licao.nivel_id == progresso_ativo.nivel_id)
            .order_by(Licao.ordem)
            .offset(progresso_ativo.licoes_concluidas)
            .first()
        )

    # Total geral de lições da plataforma
    total_aulas = db.query(Licao).count()
    aulas_feitas = sum(p.licoes_concluidas for p in usuario.progressos)

    # 3 Desafios dinâmicos do dia (espelhando a Tela 2 do Figma)
    desafios = []
    licoes_iniciais = db.query(Licao).order_by(Licao.ordem).limit(3).all()
    for licao in licoes_iniciais:
        concluida = any(
            t.licao_id == licao.id and t.sucesso for t in usuario.tentativas
        )
        desafios.append(DesafioItem(
            licao_id=licao.id,
            titulo=licao.titulo,
            subtitulo=licao.subtitulo or "",
            duracao_minutos=licao.duracao_minutos,
            dificuldade="Iniciante",
            concluida=concluida
        ))

    return DashboardResponse(
        usuario=usuario,
        aulas_concluidas=aulas_feitas,
        aulas_totais=total_aulas or 20,
        minutos_semana=usuario.minutos_estudo_semana,
        dias_consecutivos=usuario.dias_consecutivos,
        meta_dias_semana=usuario.meta_dias_semana,
        trilha_atual_titulo=trilha_titulo,
        trilha_atual_percentual=trilha_percentual,
        proxima_licao_id=proxima_licao.id if proxima_licao else None,
        proxima_licao_titulo=proxima_licao.titulo if proxima_licao else None,
        desafios_hoje=desafios
    )

@router.post("/tentativas", response_model=TentativaResponse)
def registrar_tentativa(dados: TentativaCreate, usuario: Usuario = Depends(obter_usuario_atual), db: Session = Depends(get_db)):
    """Recebe o feedback do avatar (Edge AI) e atualiza o progresso do aluno."""
    licao = db.query(Licao).filter(Licao.id == dados.licao_id).first()
    if not licao:
        raise HTTPException(status_code=404, detail="Lição não encontrada.")

    # Grava o histórico detalhado
    nova_tentativa = HistoricoTentativa(
        usuario_id=usuario.id,
        licao_id=dados.licao_id,
        gesto_id=dados.gesto_id,
        sucesso=dados.sucesso,
        confianca_obtida=dados.confianca_obtida,
        tempo_estabilizacao_ms=dados.tempo_estabilizacao_ms
    )
    db.add(nova_tentativa)

    # Se a tentativa foi validada com sucesso, atualiza o progresso da trilha
    percentual_retorno = 0.0
    if dados.sucesso:
        prog = db.query(ProgressoNivel).filter(
            ProgressoNivel.usuario_id == usuario.id,
            ProgressoNivel.nivel_id == licao.nivel_id
        ).first()

        if prog:
            total_licoes_nivel = db.query(Licao).filter(Licao.nivel_id == licao.nivel_id).count()
            if prog.licoes_concluidas < licao.ordem:
                prog.licoes_concluidas = licao.ordem
                prog.percentual_conclusao = round((prog.licoes_concluidas / total_licoes_nivel) * 100, 1)
                prog.ultima_licao_id = licao.id
            percentual_retorno = prog.percentual_conclusao

        # Incrementa o tempo de prática do aluno
        usuario.minutos_estudo_semana += max(1, round(licao.duracao_minutos / 2))

    db.commit()
    db.refresh(nova_tentativa)

    return TentativaResponse(
        id=nova_tentativa.id,
        sucesso=nova_tentativa.sucesso,
        data_hora=nova_tentativa.data_hora,
        progresso_atualizado=percentual_retorno
    )