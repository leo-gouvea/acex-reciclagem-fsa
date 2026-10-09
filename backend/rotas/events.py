# Esse arquivo contém rotas relacionadas a eventos, como a criação de eventos e a obtenção de informações sobre eles. Assim como suas configurações e permissões de acesso. (Ex. Grupo A vs Grupo B)
# Será criado um código de adesão e gerenciamento desses eventos / usuários e a soma dos pontos para o evento sera a considerada a partir da data de criação do evento
# Essas rotas impactam diretamente na estrutura do banco de dados atual, necessitando de um incremento de campo em Perfil (Algo que ja era esperado posteriormente, mas que não foi implementado na primeira versão do banco de dados)
# Está claro que isso não representa EVENTOS, mas sim COMPETIÇÕES, mas para fins de organização e nomenclatura, será mantido o nome de eventos por enquanto.
import os
from datetime import datetime

import aiosqlite
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

# Importando do main para facilitar
from main import check_access
from utils.sqlite_datetime_validator import SQLiteDateTime

# Identificar rota de grupo e fora de main
router = APIRouter(
    prefix="/contests",
    tags=["Eventos e Competições"],
)

# Usando os para navegar entre os arquivos de forma segura entre sistemas operacionais diferentes
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")


# ==========================================
# SCHEMAS DE RETORNO (RESPONSES)
# ==========================================

class EventsReturn(BaseModel):
    """
    Modelo de dados para representar a lista de eventos existentes
    """
    id: int
    event_name: str
    event_description: str
    event_start_date: str
    event_end_date: str


class EventsGroupsReturn(BaseModel):
    """
    Modelo de dados para representar a lista de grupos de eventos existentes
    """
    id: int
    group_name: str
    event_id: int


class CreateEventReturn(BaseModel):
    """
    Modelo padrão de retorno para criação de evento realizada com sucesso.
    """
    message: str = "Evento criado com sucesso"
    event_id: int


class UpdateEventReturn(BaseModel):
    """
    Modelo padrão de retorno para atualização de evento realizada com sucesso.
    """
    message: str = "Evento atualizado com sucesso"
    event_id: int


class DeleteEventReturn(BaseModel):
    """
    Modelo padrão de retorno para deleção de evento realizada com sucesso.
    """
    message: str = "Evento deletado com sucesso"


# ==========================================
# SCHEMAS DE ENTRADA (REQUESTS)
# ==========================================

class EventCreate(BaseModel):
    """
    Modelo de dados para criar um novo evento.
    """
    event_name: str
    event_description: str
    event_start_date: SQLiteDateTime = Field(
        default_factory=datetime.now,
        examples=["2026-12-31 23:59:59"]
    )
    event_end_date: SQLiteDateTime = Field(
        default_factory=datetime.now,
        examples=["2026-12-31 23:59:59"]
    )


class EventUpdate(BaseModel):
    """
    Modelo de dados para atualizar um evento existente.
    """
    event_id: int
    event_name: str
    event_description: str
    event_start_date: SQLiteDateTime = Field(
        default_factory=datetime.now,
        examples=["2026-12-31 23:59:59"]
    )
    event_end_date: SQLiteDateTime = Field(
        default_factory=datetime.now,
        examples=["2026-12-31 23:59:59"]
    )


# ==========================================
# ROTAS / ENDPOINTS
# ==========================================

@router.get("/list", response_model=list[EventsReturn])
async def list_events():
    """
    Rota para listar todos os eventos disponíveis.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM events") as cursor:
            events = await cursor.fetchall()

        events_list = [
            EventsReturn(
                id=row["id"], 
                event_name=row["nm_event"], 
                event_description=row["ds_event_description"], 
                event_start_date=row["dt_event_start"], 
                event_end_date=row["dt_event_end"]
            ) 
            for row in events
        ]
        
    return events_list


@router.get("/groups/list", response_model=list[EventsGroupsReturn])
async def list_event_groups():
    """
    Rota para listar todos os grupos de eventos disponíveis.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT * FROM events_groups") as cursor:
            events = await cursor.fetchall()

        events_groups = [
            EventsGroupsReturn(
                id=row["id"], 
                group_name=row["group_name"], 
                event_id=row["fk_cd_event"]
            ) 
            for row in events
        ]
        
    return events_groups


@router.post("/create", status_code=status.HTTP_201_CREATED, response_model=CreateEventReturn)
async def create_event(event: EventCreate, user=Depends(check_access)):
    """
    Rota para criar um novo evento.
    """
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas administradores podem criar eventos.")

    # Converte os campos para string limpa usando as regras do SQLiteDateTime
    event_data = event.model_dump(mode="json")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "INSERT INTO events (nm_event, ds_event_description, dt_event_start, dt_event_end) VALUES (?, ?, ?, ?)",
            (
                event_data["event_name"], 
                event_data["event_description"], 
                event_data["event_start_date"], 
                event_data["event_end_date"]
            )
        ) as cursor:
            event_id = cursor.lastrowid
            
        await db.commit()

    return CreateEventReturn(event_id=event_id)


@router.patch("/update", status_code=status.HTTP_200_OK, response_model=UpdateEventReturn)
async def update_event(event: EventUpdate, user=Depends(check_access)):
    """
    Rota para atualizar um evento existente.
    """
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas administradores podem atualizar eventos.")

    # Converte os campos para string limpa usando as regras do SQLiteDateTime
    event_data = event.model_dump(mode="json")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            UPDATE events 
            SET nm_event = ?, ds_event_description = ?, dt_event_start = ?, dt_event_end = ? 
            WHERE id = ?
            """,
            (
                event_data["event_name"], 
                event_data["event_description"], 
                event_data["event_start_date"], 
                event_data["event_end_date"], 
                event_data["event_id"]
            )
        ) as cursor:
            if cursor.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")
            
        await db.commit()

    return UpdateEventReturn(event_id=event_data["event_id"])


@router.delete("/delete/{event_id}", status_code=status.HTTP_200_OK, response_model=DeleteEventReturn)
async def delete_event(event_id: int, user=Depends(check_access)):
    """
    Rota para deletar um evento existente.
    """
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado. Apenas administradores podem deletar eventos.")

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("DELETE FROM events WHERE id = ?", (event_id,)) as cursor:
            if cursor.rowcount == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento não encontrado.")
            
        await db.commit()

    return DeleteEventReturn()
