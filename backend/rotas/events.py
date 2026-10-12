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
# from main import check_access
from utils.jwt_validation import check_access
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
    

class EventRankingUsersScheme(BaseModel):
    """
    Modelo de retorno do ranking
    """
    user_id: int
    user_name: str
    group_id: int
    group_name: str
    recycles: int
    total_weight: float
    recycle_points: int

class EventRanking(BaseModel):
    """
    Modelo de retorno do ranking das pessoas que mais reciclaram em um evento
    """
    event_id: int
    event_name: str
    ranking: list[EventRankingUsersScheme]


class EventGroupResponse(BaseModel):
    """Schema para padronizar a resposta enviada ao cliente"""
    id: int
    group_name: str
    fk_cd_event: int


class EventGroupDeletion(BaseModel):
    """Modelo de retorno da deleção de grupos"""
    message: str
    
    
class EventGroupNested(BaseModel):
    """Modelo para representar o grupo dentro da listagem de eventos"""
    id: int
    group_name: str


class EventWithGroupsReturn(EventsReturn):
    """Modelo que herda os dados de evento e adiciona a lista de grupos"""
    groups: list[EventGroupNested]


class EventStatsWithRankingReturn(BaseModel):
    """Modelo para retornar os totais matemáticos e o Top 10 juntos"""
    total_recycles: int
    total_weight: float
    total_points: int
    ranking: list[EventRankingUsersScheme]

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


class EventGroupCreate(BaseModel):
    """
    Schema para receber os dados de criação de um grupo
    """
    group_name: str = Field(..., min_length=3, max_length=100, example="Eco Warriors")
    fk_cd_event: int = Field(..., description="ID do evento ao qual o grupo pertence", example=1)


# ==========================================
# ROTAS / ENDPOINTS
# ==========================================


# Rota nova que substitui as listagens antigas
@router.get("/list-with-groups", response_model=list[EventWithGroupsReturn])
async def list_events_with_groups():
    """
    Rota para listar todos os eventos e os grupos associados a eles.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Busca todos os eventos
        async with db.execute("SELECT * FROM events") as cursor:
            events_rows = await cursor.fetchall()

        # Busca todos os grupos na tabela correta
        async with db.execute("SELECT * FROM events_groups") as cursor:
            groups_rows = await cursor.fetchall()

        events_list = []
        for event in events_rows:
            
            # Filtra os grupos que pertencem a este evento
            event_groups = [
                EventGroupNested(id=g["id"], group_name=g["nm_group_name"]) 
                for g in groups_rows if g["fk_cd_event"] == event["id"]
            ]
            
            events_list.append(
                EventWithGroupsReturn(
                    id=event["id"], 
                    event_name=event["nm_event"], 
                    event_description=event["ds_event_description"], 
                    event_start_date=event["dt_event_start"], 
                    event_end_date=event["dt_event_end"],
                    groups=event_groups
                )
            )
            
    return events_list


@router.get("/list", response_model=list[EventsReturn], deprecated=True)
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


@router.get("/groups/list", response_model=list[EventsGroupsReturn], deprecated=True)
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
                group_name=row["nm_group_name"], 
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


# ESTATISTICAS DE UM EVENTO
@router.get("/event/{event_id}/stats", response_model=EventStatsWithRankingReturn)
async def get_event_total_stats(event_id: int):
    """
    Retorna os pontos totais, quilos totais e o Top 10 do evento inteiro.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        #  Verifica se o evento existe (se não existir, retorna erro 404)
        async with db.execute("SELECT id FROM events WHERE id = ?", (event_id,)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Evento não encontrado.")

        #  Busca os totais matemáticos do evento
        query_totals = """
            SELECT 
                COUNT(r.id) AS total_recycles,
                IFNULL(SUM(r.nr_weight_kilograms), 0) AS total_weight,
                CAST(IFNULL(SUM(r.nr_weight_kilograms * m.nr_points_per_kilogram), 0) AS INTEGER) AS total_points
            FROM events e
            INNER JOIN events_groups eg ON eg.fk_cd_event = e.id
            INNER JOIN users u ON u.fk_cd_event_GROUP = eg.id
            INNER JOIN recycling r ON r.fk_cd_user = u.id
            INNER JOIN materials m ON m.id = r.fk_cd_material
            WHERE e.id = ? 
            AND r.dt_gave BETWEEN e.dt_event_start AND e.dt_event_end
        """
        async with db.execute(query_totals, (event_id,)) as cursor:
            stats = await cursor.fetchone()
            
        #  Busca o ranking (Top 10) do evento
        query_ranking = """
            SELECT 
                u.id AS user_id,
                u.nm_user AS user_name,
                eg.id AS group_id,
                eg.nm_group_name AS group_name,
                COUNT(r.id) AS recycles,
                IFNULL(SUM(r.nr_weight_kilograms),0) AS total_weight,
                CAST(IFNULL(SUM(r.nr_weight_kilograms * m.nr_points_per_kilogram), 0) AS INTEGER) AS recycle_points 
            FROM events e
            INNER JOIN events_groups eg ON eg.fk_cd_event = e.id
            INNER JOIN users u ON u.fk_cd_event_GROUP = eg.id
            INNER JOIN recycling r ON r.fk_cd_user = u.id
            INNER JOIN materials m ON m.id = r.fk_cd_material
            WHERE e.id = ? 
            AND r.dt_gave BETWEEN e.dt_event_start AND e.dt_event_end
            GROUP BY u.id, u.nm_user, eg.id, eg.nm_group_name
            ORDER BY recycle_points DESC, total_weight DESC
            LIMIT 10;
        """
        async with db.execute(query_ranking, (event_id,)) as cursor:
            rows = await cursor.fetchall()

        #  Converte as linhas do banco de dados para a lista do schema
        users_ranking = [EventRankingUsersScheme(**dict(row)) for row in rows]

        #  Retorna tudo empacotado no mesmo JSON
        return EventStatsWithRankingReturn(
            total_recycles=stats["total_recycles"],
            total_weight=stats["total_weight"],
            total_points=stats["total_points"],
            ranking=users_ranking
        )


# ESTATISTICAS DE DE UM GRUPO
@router.get("/event/{event_id}/group/{group_id}/stats", response_model=EventStatsWithRankingReturn)
async def get_group_stats(event_id: int, group_id: int):
    """
    Retorna os pontos totais, quilos totais e o Top 10 de um grupo específico.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        #  Verifica se o grupo pertence a esse evento
        async with db.execute("SELECT id FROM events_groups WHERE id = ? AND fk_cd_event = ?", (group_id, event_id)) as cursor:
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="Grupo ou evento não encontrado.")

        #  Busca os totais matemáticos apenas desse grupo
        query_totals = """
            SELECT 
                COUNT(r.id) AS total_recycles,
                IFNULL(SUM(r.nr_weight_kilograms), 0) AS total_weight,
                CAST(IFNULL(SUM(r.nr_weight_kilograms * m.nr_points_per_kilogram), 0) AS INTEGER) AS total_points
            FROM events_groups eg
            INNER JOIN users u ON u.fk_cd_event_GROUP = eg.id
            INNER JOIN recycling r ON r.fk_cd_user = u.id
            INNER JOIN materials m ON m.id = r.fk_cd_material
            INNER JOIN events e ON e.id = eg.fk_cd_event
            WHERE eg.id = ? AND eg.fk_cd_event = ?
            AND r.dt_gave BETWEEN e.dt_event_start AND e.dt_event_end
        """
        async with db.execute(query_totals, (group_id, event_id)) as cursor:
            stats = await cursor.fetchone()
            
        #  Busca o ranking (Top 10) restrito aos alunos deste grupo
        query_ranking = """
            SELECT 
                u.id AS user_id,
                u.nm_user AS user_name,
                eg.id AS group_id,
                eg.nm_group_name AS group_name,
                COUNT(r.id) AS recycles,
                IFNULL(SUM(r.nr_weight_kilograms),0) AS total_weight,
                CAST(IFNULL(SUM(r.nr_weight_kilograms * m.nr_points_per_kilogram), 0) AS INTEGER) AS recycle_points 
            FROM events_groups eg
            INNER JOIN users u ON u.fk_cd_event_GROUP = eg.id
            INNER JOIN recycling r ON r.fk_cd_user = u.id
            INNER JOIN materials m ON m.id = r.fk_cd_material
            INNER JOIN events e ON e.id = eg.fk_cd_event
            WHERE eg.id = ? AND eg.fk_cd_event = ?
            AND r.dt_gave BETWEEN e.dt_event_start AND e.dt_event_end
            GROUP BY u.id, u.nm_user, eg.id, eg.nm_group_name
            ORDER BY recycle_points DESC, total_weight DESC
            LIMIT 10;
        """
        async with db.execute(query_ranking, (group_id, event_id)) as cursor:
            rows = await cursor.fetchall()

        #  Converte as linhas para o formato de retorno
        users_ranking = [EventRankingUsersScheme(**dict(row)) for row in rows]

        #  Retorna os dados combinados
        return EventStatsWithRankingReturn(
            total_recycles=stats["total_recycles"],
            total_weight=stats["total_weight"],
            total_points=stats["total_points"],
            ranking=users_ranking
        )


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
    Rota para o próprio usuário autenticado se desinscrever do seu grupo atual (redefinindo para Null).
    """
    # Recupera o ID do usuário diretamente da sessão/token injetado
    logged_user_id = user.get("id")

    async with aiosqlite.connect(DB_PATH) as db:
        # Atualiza a coluna do grupo para 0 apenas para o ID de quem disparou a requisição
        async with db.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE users 
                SET fk_cd_event_group = NULL 
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
    Rota para o Administrador desinscrever qualquer aluno de seu grupo atual (redefinindo para Null).
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
                SET fk_cd_event_group = NULL 
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
        

@router.post("/event/group", response_model=EventGroupResponse, status_code=status.HTTP_201_CREATED)
async def create_event_group(group_data: EventGroupCreate):
    """
    Cria um grupo para um evento existente
    """
    
    async with aiosqlite.connect(DB_PATH) as DB:
        DB.row_factory = aiosqlite.Row
        
        # Verificar se o evento realmente existe antes de criar o grupo
        async with DB.execute("SELECT id FROM events WHERE id = ?", (group_data.fk_cd_event,)) as cursor:
            event_exists = await cursor.fetchone()
            
        if not event_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Não foi possível criar o grupo. O evento com ID {group_data.fk_cd_event} não existe."
            )
            
        # Inserir o novo grupo no banco de dados com os nomes de tabela e coluna corrigidos
        query_insert = """
            INSERT INTO events_groups (nm_group_name, fk_cd_event) 
            VALUES (?, ?)
            RETURNING id, nm_group_name AS group_name, fk_cd_event;
        """
        try:
            async with DB.execute(query_insert, (group_data.group_name, group_data.fk_cd_event)) as cursor:
                new_group = await cursor.fetchone()
                await DB.commit()
        except Exception as e:
            await DB.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao salvar o grupo no banco de dados."
            )
            
        return EventGroupResponse(**dict(new_group))


@router.delete("/event/group/{group_id}", status_code=status.HTTP_200_OK)
async def delete_event_group(group_id: int):
    """
    Deleta um grupo de um evento.
    """
    
    async with aiosqlite.connect(DB_PATH) as DB:
        # Verificar se o grupo existe antes de tentar deletar na tabela correta
        async with DB.execute("SELECT id FROM events_groups WHERE id = ?", (group_id,)) as cursor:
            group_exists = await cursor.fetchone()
            
        if not group_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grupo com ID {group_id} não encontrado."
            )
            
        # Executar a deleção na tabela correta
        try:
            await DB.execute("DELETE FROM events_groups WHERE id = ?", (group_id,))
            await DB.commit()
        except Exception:
            await DB.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao deletar o grupo."
            )
            
        return EventGroupDeletion(message="Grupo de evento excluído com sucesso.")
