# Esse arquivo contém rotas relacionadas a eventos, como a criação de eventos e a obtenção de informações sobre eles. Assim como suas configurações e permissões de acesso. (Ex. Grupo A vs Grupo B)
# Será criado um código de adesão e gerenciamento desses eventos / usuários e a soma dos pontos para o evento sera a considerada a partir da data de criação do evento
# Essas rotas impactam diretamente na estrutura do banco de dados atual, necessitando de um incremento de campo em Perfil (Algo que ja era esperado posteriormente, mas que não foi implementado na primeira versão do banco de dados)
# Está claro que isso não representa EVENTOS, mas sim COMPETIÇÕES, mas para fins de organização e nomenclatura, será mantido o nome de eventos por enquanto.
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


class EventsReturn(BaseModel):
    """
    Modelo de dados para representar a lista de eventos existentes
    """
    id: int
    event_name: str

@router.get("/list", response_model=list[EventsReturn])
async def list_events():
    """
    Rota para listar todos os eventos disponíveis.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # configuração para vir como dicionario ou sql row
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("SELECT * FROM events")
        events = await cursor.fetchall()
        await cursor.close()

        events = [EventsReturn(id=row["id"], event_name=row["nm_event"]) for row in events]
        
    return events


class EventsGroupsReturn(BaseModel):
    """
    Modelo de dados para representar a lista de grupos de eventos existentes
    """
    id: int
    group_name: str
    event_id: int

@router.get("/groups/list", response_model=list[EventsGroupsReturn])
async def list_event_groups():
    """
    Rota para listar todos os grupos de eventos disponíveis.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # configuração para vir como dicionario ou sql row
        db.row_factory = aiosqlite.Row

        cursor = await db.execute("SELECT * FROM events_groups")
        events = await cursor.fetchall()
        await cursor.close()

        events = [EventsGroupsReturn(id=row["id"], group_name=row["group_name"], event_id=row["fk_cd_event"]) for row in events]
        
    return events


