# Imports
import os # Essa importação serve para realizarmos uma leitura dos arquivos existentes para importação de rotas dinamicamente posteriormente
import importlib # Para efetivamente importar bibliotecas dinamicamente

# Bibliotecas de FastAPI (Ela é assíncrona)
from fastapi import FastAPI, Security, HTTPException, status, Depends, Request   
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
import jwt # Importado para trabalhar com logins e credenciais de Usuários (Tokens temporários)
# Uvicorn que usamos para rodar como servidor local
import uvicorn
# Para segurança de dados
from dotenv import load_dotenv

# Dados secretos
load_dotenv()
API_KEY = os.getenv("ECO_HORA_API_KEY")

# Nossa segurança da API
# Rede de pesca do cabeçalho da requisição (serve para identificação)
# Auto error desligado para evitar raise logo de cara e permitir as outras validações
header_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)

# Função de validação
def check_access(request: Request, key: str = Security(header_api_key)):

    # Verifica se existe chave vinda do header
    if key:
        if key != API_KEY:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado, Chave de API inválida.")
        else:
            # Posto para retornar algo mais conccreto
            return {"Origin": "System", "name": "Automation", "role": "Bot"}
        
    # Se não tem, tenta "comer o cookie" de acesso
    else:
        access_token = request.cookies.get("access_token")

    # Se não tem nenhuma validação
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado. Forneça uma chave de API ou realize login no site.")


    # Tratamento do Cookie
    try:
        decoded_user = jwt.decode(access_token, API_KEY, algorithms=["HS256"])
        return decoded_user

    # Se o Limite de tempo de login expirou (validade do cookie passou)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado, login expirado.")
    # Se o token é inválido
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado, token falso ou inválido.")


# Instanciamento (Inicia a nossa API)
app = FastAPI(title="API ACEX", description="API construída para o projeto ACEX 2026", version="0.2.0")
# dependencies=[Depends(check_key)] -> Removido de App para evitar BLoqueio de 100% das rotas

# Adicionado o CORS para que o front se comunique com o Back
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:808   0"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Construíndo a primeira rota (Uso para validação de funcionamento / Status)
@app.get("/", include_in_schema=False) # Excluído do esquema de telas 
async def root():
    # Se o status estiver ok
    response = {
        "status": "Funcionando!",
        "developers": "EcoHora Team.",
        "version": app.version
    }

    return response

# Para importação das rotas extras de foma dinamica
PASTA_DE_ROTAS = os.path.join(os.path.dirname(__file__), "rotas")
for modules in os.listdir(PASTA_DE_ROTAS):
    if modules.endswith(".py") and modules !=  "__pycache__":
        modules = modules[:-3]
        imported_modules = importlib.import_module(f"rotas.{modules}")

        if hasattr(imported_modules, "router"):
            app.include_router(imported_modules.router)

# Segurança de execução de arquivo somente por ele mesmo
if __name__ == "__main__":
    # Abertura do servidor, com portas padrão 8080, IP padrão 0.0 para visualização aberta.
    uvicorn.run(app, host="0.0.0.0", port=8080)