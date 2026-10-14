import os

import jwt
from fastapi import Request, Security, HTTPException, status
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv

# Dados secretos
load_dotenv()
API_KEY = os.getenv("ECO_HORA_API_KEY")
JWT_SECRET = os.getenv("JWT_SECRET", API_KEY)


# Nossa segurança da API
header_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)

# Função de validação
def check_access(request: Request, key: str = Security(header_api_key)):

    # Verifica se existe chave vinda do header
    if key:
        if key != API_KEY:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado, Chave de API inválida.")
        return {"Origin": "System", "name": "Automation", "role": "Bot"}
        
    # Se não tem, tenta "comer o cookie" de acesso
    access_token = request.cookies.get("access_token")

    # Se não tem nenhuma validação
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado. Forneça uma chave de API ou realize login no site.")

    # Tratamento do Cookie
    try:
        # Ajustado para usar o segredo correto do JWT
        decoded_user = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        return decoded_user

    # Se o Limite de tempo de login expirou (validade do cookie passou)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado, login expirado.")
    # Se o token é inválido
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado, token falso ou inválido.")

