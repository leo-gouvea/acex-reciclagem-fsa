# Imports
import os # Realiza a leitura dos arquivos existentes para importação de rotas dinamicamente
import importlib # Para efetivamente importar bibliotecas dinamicamente

# Bibliotecas de FastAPI (Ela é assíncrona)
from fastapi import FastAPI, Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
# Para repelir robôs de busca automática de consumir da API sem necessidade
from fastapi.responses import PlainTextResponse
import jwt # Para trabalhar com logins e credenciais de Usuários (Tokens temporários)
# Uvicorn que usamos para rodar como servidor local
import uvicorn
# Para segurança de dados
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


# Instanciamento (Inicia a nossa API)
version = "0.4.3"
title = "API ACEX"
description = """
API construída para o projeto ACEX 2026\n
O horário da API é definido no modelo **UTC TIMESTAMP, 3 horas a frente ao Brasil**.
"""
app = FastAPI(title=title, description=description, version=version)

# Adicionado o CORS para que o front se comunique com o Back
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://acex-reciclagem-fsa.vercel.app",
        "http://127.0.0.1:5500", # Live Server
    ],
    allow_origin_regex=r"https://acex-reciclagem-[a-zA-Z0-9]+-leogouvea\.vercel\.app", 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Construindo a primeira rota (Uso para validação de funcionamento / Status)
@app.get("/", include_in_schema=False) 
async def root():
    return {
        "status": "Funcionando!",
        "developers": "EcoHora Team.",
        "version": app.version
    }

# Rota efetiva dos robôs
@app.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
def robots():
    return "User-agent: *\nDisallow: /"


# Para importação das rotas extras de forma dinâmica
PASTA_DE_ROTAS = os.path.join(os.path.dirname(__file__), "rotas")

# Verificação preventiva caso a pasta de rotas ainda não exista no ambiente
if os.path.exists(PASTA_DE_ROTAS):
    for modules in os.listdir(PASTA_DE_ROTAS):
        if modules.endswith(".py") and modules != "__pycache__":
            modules = modules[:-3]
            imported_modules = importlib.import_module(f"rotas.{modules}")

            if hasattr(imported_modules, "router"):
                app.include_router(imported_modules.router)

# Segurança de execução de arquivo somente por ele mesmo
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True) # Melhorado para desenvolvimento local
