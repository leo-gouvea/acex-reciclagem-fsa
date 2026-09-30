import os

import aiosqlite
from fastapi import APIRouter, HTTPException, status
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
async def post_material(data: PostMaterialRequest):
    """Insere um material permitido na reciclagem, na tabela"""

    try:
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Erros encontrados internamente."
        )

class DeleteMaterialReturn(BaseModel):
    status: int
    detail: str

@router.delete("/material/{material_id}", response_model=DeleteMaterialReturn, response_description="Informa o status de exclusão do material")
async def delete_material(material_id: int):
    """Remove um material da tabela de reciclagem usando o seu ID."""

    try:
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
    
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Erros encontrados internamente ao tentar deletar."
        )


class PostRecyclingRequest(BaseModel):
    fk_cd_material: int
    nr_weight_kilograms: float
    fk_cd_user: int

# Resposta padrão para as operações
class RecyclingResponse(BaseModel):
    status: int
    detail: str

@router.post("/recycle", response_model=RecyclingResponse, response_description="Registra uma nova atividade de reciclagem")
async def post_recycle(data: PostRecyclingRequest):
    """Registra uma entrega de material feita por um usuário."""
    try:
        # Trava  de peso negativo
        if data.nr_weight_kilograms <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O peso deve ser maior que ZERO")
        
        async with aiosqlite.connect(DB_PATH) as db:
            # Ativa suporte a chaves estrangeiras no SQLite para validar os IDs
            await db.execute("PRAGMA foreign_keys = ON;")
            
            query = """
                INSERT INTO recycling (fk_cd_material, nr_weight_kilograms, fk_cd_user)
                VALUES (?, ?, ?)
            """
            
            query_data = (
                data.fk_cd_material,
                data.nr_weight_kilograms,
                data.fk_cd_user
            )

            await db.execute(query, query_data)
            await db.commit()

        return {"status": 201, "detail": "Reciclagem registrada com sucesso!"}
    
    except HTTPException:
        raise
    except aiosqlite.IntegrityError as e:
        # Captura se o usuário passar um ID de material ou usuário que não existe
        print(f"Erro de integridade: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro de integridade. Verifique se o material e o usuário informados existem."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erros encontrados internamente ao registrar."
        )


@router.delete("/recycle/{recycle_id}", response_model=RecyclingResponse, response_description="Informa o status de exclusão do registro")
async def delete_recycling(recycle_id: int):
    """Remove um registro de reciclagem do histórico através do ID."""
    try:
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

    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao deletar: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erros encontrados internamente ao tentar deletar o registro."
        )
