# Imports
import os # Essa importação serve para realizarmos uma leitura dos arquivos existentes para importação de rotas dinamicamente posteriormente
import importlib # Para efetivamente importar bibliotecas dinamicamente

# Bibliotecas de FastAPI (Ela é assíncrona)
from fastapi import FastAPI, Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader
# Uvicorn que usamos para rodar como servidor local
import uvicorn
# Para segurança de dados
from dotenv import load_dotenv

# Dados secretos
load_dotenv()
API_KEY = os.getenv("ECO_HORA_API_KEY")

# Nossa segurança da API
# Rede de pesca do cabeçalho da requisição (serve para identificação)
header_api_key = APIKeyHeader(name="X-API-Key", auto_error=True)

# Função de validação
def check_key(key: str = Security(header_api_key)):
    if key != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso negado, Chave de API inválida.")

    return key


# Instanciamento (Inicia a nossa API)
app = FastAPI(title="API ACEX", description="API construída para o projeto ACEX 2026", version="1.0.0", dependencies=[Depends(check_key)])


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