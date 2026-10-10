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
    
    
class UserAssignReturn(BaseModel):
    """
    Modelo padrão de retorno para atribuição de usuário a grupo de evento realizada com sucesso.
    """
    message: str = "Usuário atribuído ao grupo de evento com sucesso."


class UserUnassignReturn(BaseModel):
    """
    Modelo padrão de retorno para desinscrição de usuário de grupo de evento.
    """
    message: str = "Usuário desinscrito do grupo de evento com sucesso."
    

class AdminActionReturn(BaseModel):
    """
    Modelo padrão de retorno para ações de gerenciamento do Administrador.
    """
    message: str


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
    
    
class UserAssign(BaseModel):
    """
    Modelo de dados para atribuir um usuário a um grupo de evento.
    """
    group_id: int = Field(..., description="ID do grupo de evento ativo que o aluno escolheu.")


class AdminUserAssignRequest(BaseModel):
    """
    Modelo de dados para o Administrador vincular um aluno a um grupo.
    """
    user_id: int = Field(..., description="ID do usuário/aluno que será inscrito.")
    group_id: int = Field(..., description="ID do grupo de evento de destino.")

class AdminUserUnassignRequest(BaseModel):
    """
    Modelo de dados para o Administrador remover um aluno de um grupo.
    """
    user_id: int = Field(..., description="ID do usuário/aluno que será desvinculado.")


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


# O susuário só consegue se inscrever a um evento.
@router.post("/group/user/assign", status_code=status.HTTP_200_OK, response_model=UserAssignReturn)
async def assign_user_to_event_group(data: UserAssign, user=Depends(check_access)):
    """
    Rota para o próprio usuário autenticado se inscrever em um grupo de evento ativo.
    """
    # Recupera o ID do usuário diretamente da sessão/token injetado
    logged_user_id = user.get("id")

    async with aiosqlite.connect(DB_PATH) as db:
        # Valida se o grupo do evento realmente existe antes de tentar associar
        async with db.execute("SELECT id FROM events_groups WHERE id = ?", (data.group_id,)) as cursor:
            group = await cursor.fetchone()
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Grupo de evento não encontrado ou inativo."
                )

        # Atualiza o perfil do próprio usuário logado com o ID do grupo escolhido
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users
                SET fk_cd_event_group = ?
                WHERE id = ?
                """,
                (data.group_id, logged_user_id)
            )
            
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Erro ao processar inscrição. Usuário não encontrado."
                )
                
        await db.commit()

    return UserAssignReturn()


@router.delete("/group/user/unassign", status_code=status.HTTP_200_OK, response_model=UserUnassignReturn)
async def unassign_user_from_event_group(user=Depends(check_access)):
    """
    Rota para o próprio usuário autenticado se desinscrever do seu grupo atual (redefinindo para 0).
    """
    # Recupera o ID do usuário diretamente da sessão/token injetado
    logged_user_id = user.get("id")

    async with aiosqlite.connect(DB_PATH) as db:
        # Atualiza a coluna do grupo para 0 apenas para o ID de quem disparou a requisição
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users 
                SET fk_cd_event_group = 0 
                WHERE id = ?
                """,
                (logged_user_id,)
            )
            
            # Se rowcount for 0, o ID da sessão não foi localizado (falha crítica ou sessão inválida)
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Não foi possível processar a desinscrição."
                )
                
        await db.commit()

    return UserUnassignReturn()


@router.post("/admin/group/user/assign", status_code=status.HTTP_200_OK, response_model=AdminActionReturn)
async def admin_assign_user_to_group(data: AdminUserAssignRequest, user=Depends(check_access)):
    """
    Rota para o Administrador inscrever qualquer aluno em um grupo de evento à força.
    """
    # Trava estrita de hierarquia: Apenas Administradores podem acessar
    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas administradores podem gerenciar inscrições de terceiros."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        # Valida se o grupo de evento realmente existe na base de dados
        async with db.execute("SELECT id FROM events_groups WHERE id = ?", (data.group_id,)) as cursor:
            group = await cursor.fetchone()
            if not group:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Grupo de evento não encontrado."
                )

        # Executa a alteração do campo no ID do usuário enviado no corpo da requisição (data.user_id)
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users
                SET fk_cd_event_group = ?
                WHERE id = ?
                """,
                (data.group_id, data.user_id)
            )
            
            # Se nenhuma linha foi afetada, significa que o ID do aluno enviado não existe na tabela users
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuário com ID {data.user_id} não foi encontrado na base de dados."
                )
                
        await db.commit()

    return AdminActionReturn(message=f"Usuário {data.user_id} vinculado ao grupo {data.group_id} com sucesso.")


@router.delete("/admin/group/user/unassign", status_code=status.HTTP_200_OK, response_model=AdminActionReturn)
async def admin_unassign_user_from_group(data: AdminUserUnassignRequest, user=Depends(check_access)):
    """
    Rota para o Administrador desinscrever qualquer aluno de seu grupo atual (redefinindo para 0).
    """
    # Trava estrita de hierarquia: Apenas Administradores podem acessar
    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas administradores podem remover usuários de grupos."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        # Executa o reset do campo fk_cd_event_group para 0 no usuário especificado
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users 
                SET fk_cd_event_group = 0 
                WHERE id = ?
                """,
                (data.user_id,)
            )
            
            # Valida se o aluno informado de fato existia para evitar um falso sucesso
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Usuário com ID {data.user_id} não foi encontrado na base de dados."
                )
                
        await db.commit()

    return AdminActionReturn(message=f"Usuário {data.user_id} removido do grupo de evento com sucesso.")