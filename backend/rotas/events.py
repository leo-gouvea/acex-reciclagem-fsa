# Esse arquivo contém rotas relacionadas a eventos, como a criação de eventos e a obtenção de informações sobre eles. Assim como suas configurações e permissões de acesso. (Ex. Grupo A vs Grupo B)
# Será criado um código de adesão e gerenciamento desses eventos / usuários e a soma dos pontos para o evento sera a considerada a partir da data de criação do evento
# Essas rotas impactam diretamente na estrutura do banco de dados atual, necessitando de um incremento de campo em Perfil (Algo que ja era esperado posteriormente, mas que não foi implementado na primeira versão do banco de dados)
import os

import aiosqlite
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

# Importando do main para facilitar
from main import check_access

# Identificar rota de grupo e fora de main
router = APIRouter(
        prefix="/contests",
        tags=["Eventos e Competições"],
    )

# Usando os para navegar entre os arquivos de forma segura entre sistemas operacionais diferentes
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")

