import os

import aiosqlite
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel

# Importando do main para facilitar
from main import check_access

# Identificar rota de grupo e fora de main
router = APIRouter(
        prefix="/recycling",
        tags=["Reciclagem"]
    )

# Usando os para navegar entre os arquivos de forma segura entre sistemas operacionais diferentes
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")


class MaterialsScheme(BaseModel):
    id: int
    material_name: str
    points_per_kilogram: int

@router.get("/materials-info", response_model=list[MaterialsScheme], response_description="Retorna a lista de materiais e suas propriedades.")
async def materials_info():
    """Obtém a lista sobre os materiais recicláveis e suas propriedades."""

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        query = """
            SELECT * FROM materials
        """
        
        async with db.execute(query) as cur:
            result = await cur.fetchall()
            result_list = [{"id": row["id"], "material_name": row["nm_material"], "points_per_kilogram": row["nr_points_per_kilogram"]} for row in result]

        return result_list


class PostMaterialRequest(BaseModel):
    material_name: str
    points_per_kilogram: int

class PostMaterialReturn(BaseModel):
    status: int
    detail: str

@router.post("/material", response_model=PostMaterialReturn, response_description="Informa o status de inserção do material")
async def post_material(data: PostMaterialRequest, user: dict = Depends(check_access)):
    """Insere um material permitido na reciclagem, na tabela"""

    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não tem permissão para adicionar um material."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        query = """
            INSERT INTO materials (nm_material, nr_points_per_kilogram)
            VALUES (?, ?)
        """
        
        query_data = (
            data.material_name,
            data.points_per_kilogram
        )

        await db.execute(query, query_data)
        await db.commit()

    return {"status": 200, "detail": "Tudo certo!"}



class DeleteMaterialReturn(BaseModel):
    status: int
    detail: str

@router.delete("/material/{material_id}", response_model=DeleteMaterialReturn, response_description="Informa o status de exclusão do material")
async def delete_material(material_id: int, user: dict = Depends(check_access)):
    """Remove um material da tabela de reciclagem usando o seu ID."""

    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não tem permissão para deletar um material."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        query = "DELETE FROM materials WHERE id = ?"
        
        async with db.execute(query, (material_id,)) as cur:
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Material com o ID {material_id} não foi encontrado."
                )
        
        await db.commit()

    return {"status": 200, "detail": f"Material {material_id} deletado com sucesso!"}



class PostRecyclingRequest(BaseModel):
    fk_cd_material: int
    nr_weight_kilograms: float

# Resposta padrão para as operações
class RecyclingResponse(BaseModel):
    status: int
    detail: str
    points_earned: float
    total_points: float

@router.post("/recycle", response_model=RecyclingResponse, response_description="Registra uma nova atividade de reciclagem")
async def post_recycle(data: PostRecyclingRequest, user: dict = Depends(check_access)):
    """Registra uma entrega de material feita por um usuário."""

    data_user_id: int = user.get("id")

    # Trava  de peso negativo
    if data.nr_weight_kilograms <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O peso deve ser maior que ZERO")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Ativa suporte a chaves estrangeiras no SQLite para validar os IDs
        await db.execute("PRAGMA foreign_keys = ON;")

        # Faz uma busca dos materiais pelo id selecionado (para usar os pontos como base de calculo)
        query_select_material_points = """ 
        SELECT nr_points_per_kilogram
        FROM materials
        WHERE id = ?
        """
        select_material_points_args = (data.fk_cd_material,)
        cursor = await db.execute(query_select_material_points, select_material_points_args)
        points_per_kg = await cursor.fetchone()

        if not points_per_kg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")


        # Cálculo de pontos por kilo, indexado da tupla
        points_earned = points_per_kg[0] * data.nr_weight_kilograms
        # Arredonda os pontos para 2 casas decimais
        points_earned_rounded = round(points_earned, 2)

        query_adding_points = """
        UPDATE users
        SET nr_points = nr_points + ?
        WHERE id = ?
        """
        query_adding_points_args = (points_earned_rounded, data_user_id)
        cursor = await db.execute(query_adding_points, query_adding_points_args)


        query_recycle_adding_history = """
        INSERT INTO recycling (fk_cd_material, nr_weight_kilograms, fk_cd_user)
        VALUES (?, ?, ?)
        """
        
        query_recycle_adding_history_args = (
            data.fk_cd_material,
            data.nr_weight_kilograms,
            data_user_id
        )

        await db.execute(query_recycle_adding_history, query_recycle_adding_history_args)
        await db.commit()

        user_cursor = await db.execute("SELECT nr_points FROM users WHERE id = ?", (data_user_id,))
        total_points_row = await user_cursor.fetchone()
        total_points = round(total_points_row[0], 2) if total_points_row else 0.0

        return {
            "status": 200,
            "detail": "Reciclagem registrada com sucesso!",
            "points_earned": points_earned_rounded,
            "total_points": total_points
        }


@router.delete("/recycle/{recycle_id}", response_model=RecyclingResponse, response_description="Informa o status de exclusão do registro")
async def delete_recycling(recycle_id: int, user: dict = Depends(check_access)):
    """Remove um registro de reciclagem do histórico através do ID."""

    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Você não tem permissão para deletar uma reciclagem"
        )

    async with aiosqlite.connect(DB_PATH) as db:
        query = "DELETE FROM recycling WHERE id = ?"
        
        async with db.execute(query, (recycle_id,)) as cur:
            # Se nenhuma linha foi afetada, o ID enviado não existe
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Registro de reciclagem com ID {recycle_id} não foi encontrado."
                )
        
        await db.commit()

    return {"status": 200, "detail": f"Registro de reciclagem {recycle_id} deletado com sucesso!"}