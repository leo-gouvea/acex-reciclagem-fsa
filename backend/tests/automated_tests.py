#  Aqui são guardados alguns testes automatizados de funções da API usando pytest e httpx
# Comando para iniciar o teste: pytest test_integracao.py -v
import os
import shutil

import pytest
from fastapi.testclient import TestClient
from main import app
from utils.jwt_validation import check_access

# Importar rotas de reciulcagem para modfidicar alguns atributos
from rotas import recycling

# Criando as rotas dos arquivos para o OS não se perder
# Pega a pasta atual (automations), volta uma (backend) e entra na pasta database
PASTA_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_REAL = os.path.join(PASTA_RAIZ, "database", "ecohora.db")
DB_TESTE = os.path.join(PASTA_RAIZ, "database", "test_ecohora.db")

# O "Mordomo" dos testes (Fixture)
# Ele funciona sobre cada loop / teste / função
@pytest.fixture(autouse=True)
def preparar_banco_de_teste(monkeypatch):
    # AÇÃO ANTES DOS TESTES COMEÇAREM:
    # Cria a cópia exata do banco original
    shutil.copy(DB_REAL, DB_TESTE)
    
    # O monkeypatch invade o arquivo recycling.py e troca a variável DB_PATH para apontar para o clone
    monkeypatch.setattr(recycling, "DB_PATH", DB_TESTE)
    
    # A palavra 'yield' para um fluxo dinamico de gerador,que cria uma pausa sem finalizar a função
    yield
    
    # AÇÃO DEPOIS QUE OS TESTES TERMINAREM:
    # O yield acorda, e o comando abaixo apaga o banco clonado do Ubuntu (Meu OS)
    if os.path.exists(DB_TESTE):
        pass
        os.remove(DB_TESTE)

# Cria um "navegador/cliente" falso para testar a nossa API
client = TestClient(app)

# Função para fingir que existe um usuário logado
def usuario_falso_logado():
    return {"id": 2, "role": "Aluno", "ra": "123456"}

# Troca o sistema de login real pelo nosso usuário falso durante o teste
app.dependency_overrides[check_access] = usuario_falso_logado


def test_registro_direto_desativado_exige_qr_code():
    dados_envio = {
        "fk_cd_material": 4,
        "nr_weight_kilograms": 2.0
    }

    resposta = client.post("/recycling/recycle", json=dados_envio)

    assert resposta.status_code == 410
    assert "QR Code" in resposta.json()["detail"]

