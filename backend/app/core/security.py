import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import Usuario

# Configurações de Criptografia e JWT
SECRET_KEY = "sinaliza-secret-key-tcc-libras-super-segura-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias de sessão

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro PBKDF2-HMAC-SHA256 com salt aleatório."""
    salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${hash_bytes.hex()}"

def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Valida se a senha informada corresponde ao hash com salt armazenado."""
    try:
        salt, hash_gravado = senha_hash.split("$")
        hash_candidato = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
        return secrets.compare_digest(hash_gravado, hash_candidato)
    except Exception:
        return False

def criar_token_acesso(dados: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Codifica o payload em um token JWT assinado."""
    payload = dados.copy()
    expiracao = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload.update({"exp": expiracao})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def obter_usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    """Injeção de dependência para proteger rotas autenticadas."""
    credenciais_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais de autenticação inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise credenciais_exception
    except JWTError:
        raise credenciais_exception

    usuario = db.query(Usuario).filter(Usuario.id == int(usuario_id)).first()
    if usuario is None:
        raise credenciais_exception
    return usuario