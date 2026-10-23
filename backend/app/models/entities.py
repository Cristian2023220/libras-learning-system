from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base
import enum

# --- ENUMS AUXILIARES ---
class NivelDificuldade(str, enum.Enum):
    INICIANTE = "iniciante"
    INTERMEDIARIO = "intermediario"
    AVANCADO = "avancado"

class TipoExercicio(str, enum.Enum):
    OBSERVACAO = "observacao"                  # Vídeo introdutório
    RECONHECIMENTO_VISUAL = "reconhecimento"  # Quiz de múltipla escolha sem câmera
    PRATICA_CAMERA = "pratica_camera"         # Edge AI com validação YOLO em tempo real

# --- 1. ENTIDADE USUARIO ---
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(180), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    perfil = Column(String(50), default="Explorador iniciante") # Exibido no card do perfil
    
    # Métricas de Hábito (Painel do Figma)
    minutos_estudo_semana = Column(Integer, default=0)
    dias_consecutivos = Column(Integer, default=1)
    meta_dias_semana = Column(Integer, default=5)
    
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    progressos = relationship("ProgressoNivel", back_populates="usuario", cascade="all, delete-orphan")
    tentativas = relationship("HistoricoTentativa", back_populates="usuario", cascade="all, delete-orphan")

# --- 2. ENTIDADE NIVEL ---
class Nivel(Base):
    __tablename__ = "niveis"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(50), unique=True, nullable=False) # Ex: 'primeiros-sinais'
    titulo = Column(String(100), nullable=False)           # Ex: 'Primeiros Sinais'
    dificuldade = Column(String(20), default=NivelDificuldade.INICIANTE)
    descricao = Column(Text, nullable=True)
    ordem = Column(Integer, nullable=False)                # 1, 2, 3
    icone_tag = Column(String(20), default="AE")           # Identificador de badge visual

    # Relacionamentos
    licoes = relationship("Licao", back_populates="nivel", order_by="Licao.ordem", cascade="all, delete-orphan")
    progressos = relationship("ProgressoNivel", back_populates="nivel")

# --- 3. ENTIDADE GESTO ---
class Gesto(Base):
    __tablename__ = "gestos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(60), nullable=False)              # Ex: 'Vogal E'
    rotulo_yolo = Column(String(20), unique=True, nullable=False) # Ex: 'E' (Classe exata do modelo)
    categoria = Column(String(50), default="alfabeto")     # alfabeto, palavra, frase
    descricao_tecnica = Column(Text, nullable=True)
    imagem_referencia_url = Column(String(255), nullable=True)

    # Relacionamentos
    licoes = relationship("Licao", back_populates="gesto_alvo")
    tentativas = relationship("HistoricoTentativa", back_populates="gesto")

# --- 4. ENTIDADE LICAO ---
class Licao(Base):
    __tablename__ = "licoes"

    id = Column(Integer, primary_key=True, index=True)
    nivel_id = Column(Integer, ForeignKey("niveis.id"), nullable=False)
    gesto_alvo_id = Column(Integer, ForeignKey("gestos.id"), nullable=True)
    
    titulo = Column(String(120), nullable=False)           # Ex: 'Conheça a vogal A'
    subtitulo = Column(String(200), nullable=True)        # Ex: 'Vídeo e primeiro contato com a vogal'
    tipo = Column(String(30), default=TipoExercicio.PRATICA_CAMERA)
    ordem = Column(Integer, nullable=False)                # Aula 1, 2, 3...
    duracao_minutos = Column(Integer, default=5)           # Ex: 3 min, 5 min
    video_demonstracao_url = Column(String(255), nullable=True)
    instrucoes_pedagogicas = Column(Text, nullable=True)

    # Relacionamentos
    nivel = relationship("Nivel", back_populates="licoes")
    gesto_alvo = relationship("Gesto", back_populates="licoes")
    tentativas = relationship("HistoricoTentativa", back_populates="licao")

# --- 5. ENTIDADE PROGRESSO_NIVEL ---
class ProgressoNivel(Base):
    __tablename__ = "progressos_nivel"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nivel_id = Column(Integer, ForeignKey("niveis.id"), nullable=False)
    
    licoes_concluidas = Column(Integer, default=0)
    percentual_conclusao = Column(Float, default=0.0)      # 0.0% a 100.0%
    desbloqueado = Column(Boolean, default=True)
    ultima_licao_id = Column(Integer, nullable=True)       # Para o botão 'Continuar aula'
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="progressos")
    nivel = relationship("Nivel", back_populates="progressos")

# --- 6. ENTIDADE HISTORICO_TENTATIVA ---
class HistoricoTentativa(Base):
    __tablename__ = "historico_tentativas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    licao_id = Column(Integer, ForeignKey("licoes.id"), nullable=False)
    gesto_id = Column(Integer, ForeignKey("gestos.id"), nullable=False)
    
    sucesso = Column(Boolean, nullable=False)              # True se validado pelo avatar
    confianca_obtida = Column(Float, nullable=False)       # Ex: 0.92 (92%)
    tempo_estabilizacao_ms = Column(Float, nullable=True)  # Tempo decorrido até atingir 100%
    data_hora = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    usuario = relationship("Usuario", back_populates="tentativas")
    licao = relationship("Licao", back_populates="tentativas")
    gesto = relationship("Gesto", back_populates="tentativas")