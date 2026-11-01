import os
import json
import io
import base64

import aiosqlite
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import qrcode

# Importando para facilitar
from utils.jwt_validation import check_access

# Identificar rota de grupo e fora de main
router = APIRouter(
    prefix="/recycling",
    tags=["Reciclagem"]
)

# Usando os para navegar entre os arquivos de forma segura entre sistemas operacionais diferentes
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")


# ==========================================
# SCHEMAS DE RETORNO (RESPONSES)
# ==========================================

class MaterialsScheme(BaseModel):
    id: int
    material_name: str
    points_per_kilogram: int


class PostMaterialReturn(BaseModel):
    status: int = 201
    detail: str = "Material inserido com sucesso!"
    material_id: int


class DeleteMaterialReturn(BaseModel):
    status: int = 200
    detail: str


class RecyclingResponse(BaseModel):
    status: int = 200
    detail: str
    points_earned: float
    total_points: float


class QrCodeResponse(BaseModel):
    material_name: str
    weight: float
    qr_code_base64: str

# ==========================================
# SCHEMAS DE ENTRADA (REQUESTS)
# ==========================================

class PostMaterialRequest(BaseModel):
    material_name: str
    points_per_kilogram: int


class PostRecyclingRequest(BaseModel):
    fk_cd_material: int
    nr_weight_kilograms: float = Field(
        ..., 
        ge=1, 
        le=10
    )


# ==========================================
# ROTAS / ENDPOINTS
# ==========================================

@router.get("/materials-info", response_model=list[MaterialsScheme], response_description="Retorna a lista de materiais e suas propriedades.")
async def materials_info():
    """Obtém a lista sobre os materiais recicláveis e suas propriedades."""

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        query = "SELECT * FROM materials"
        
        async with db.execute(query) as cur:
            result = await cur.fetchall()
            
        result_list = [
            MaterialsScheme(
                id=row["id"], 
                material_name=row["nm_material"], 
                points_per_kilogram=row["nr_points_per_kilogram"]
            ) 
            for row in result
        ]

        return result_list


@router.post("/material", response_model=PostMaterialReturn, status_code=status.HTTP_201_CREATED, response_description="Informa o status de inserção do material")
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

        async with db.execute(query, query_data) as cur:
            material_id = cur.lastrowid
            
        await db.commit()

    return PostMaterialReturn(material_id=material_id)


@router.delete("/material/{material_id}", response_model=DeleteMaterialReturn, status_code=status.HTTP_200_OK, response_description="Informa o status de exclusão do material")
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

    return DeleteMaterialReturn(detail=f"Material {material_id} deletado com sucesso!")


@router.post("/recycle", response_model=RecyclingResponse, status_code=status.HTTP_201_CREATED, response_description="Registra uma nova atividade de reciclagem")
async def post_recycle(data: PostRecyclingRequest, user: dict = Depends(check_access)):
    """Registra uma entrega de material feita por um usuário."""

    data_user_id: int = user.get("id")

    # Verificação de peso
    if not 1 <= data.nr_weight_kilograms <= 10:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="O peso deve estar entre 1 e 10.")
    
    async with aiosqlite.connect(DB_PATH) as db:
        # Ativa suporte a chaves estrangeiras no SQLite para validar os IDs
        await db.execute("PRAGMA foreign_keys = ON;")

        # Faz uma busca dos materiais pelo id selecionado (para usar os pontos como base de calculo)
        query_select_material_points = """ 
        SELECT nr_points_per_kilogram
        FROM materials
        WHERE id = ?
        """
        async with db.execute(query_select_material_points, (data.fk_cd_material,)) as cur:
            points_per_kg = await cur.fetchone()

        if not points_per_kg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")

        # Cálculo de pontos por kilo, indexado da tupla
        points_earned = points_per_kg[0] * data.nr_weight_kilograms
        points_earned_rounded = round(points_earned, 2)

        query_adding_points = """
        UPDATE users
        SET nr_points = nr_points + ?
        WHERE id = ?
        """
        await db.execute(query_adding_points, (points_earned_rounded, data_user_id))

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

        # Obtém o total acumulado do usuário de forma isolada e limpa
        async with db.execute("SELECT nr_points FROM users WHERE id = ?", (data_user_id,)) as user_cur:
            total_points_row = await user_cur.fetchone()
            total_points = round(total_points_row[0], 2) if total_points_row else 0.0

        return RecyclingResponse(
            status=201,
            detail="Reciclagem registrada com sucesso!",
            points_earned=points_earned_rounded,
            total_points=total_points
        )


@router.delete("/recycle/{recycle_id}", response_model=RecyclingResponse, status_code=status.HTTP_200_OK, response_description="Informa o status de exclusão do registro")
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
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Registro de reciclagem com ID {recycle_id} não foi encontrado."
                )
        
        await db.commit()

    return RecyclingResponse(
        status=200,
        detail=f"Registro de reciclagem {recycle_id} deletado com sucesso!",
        points_earned=0.0,
        total_points=0.0
    )


# Essa rota gera um QR CODE com as informações de reciclagem que serão lidas por um usuário para que a reciclagem seja oficialmente cadastrada.
# Fluxo esperado: Usuário traz a reciclagem, Operador preenche o form, que bate nessa rota e a rota gera um qrcode. O usuário abre o leitor e as infofs lidas são enviadas para a rota POST /recycling/recycle
def qrcode_gen(data: str):
    """Gera a imagem do qrcode e retorna o objeto da imagem (sem salvar no disco)"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Retorna a imagem gerada
    return qr.make_image(fill_color="darkgreen", back_color="white")


async def retrieve_material_info(material_id: int) -> dict:
    """Recupera informações do material pelo ID, retornando um dicionário com os dados."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM materials WHERE id = ?"
        async with db.execute(query, (material_id,)) as cur:
            row = await cur.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "material_name": row["nm_material"],
                    "points_per_kilogram": row["nr_points_per_kilogram"]
                }
            else:
                raise HTTPException(status_code=404, detail=f"Material com ID {material_id} não encontrado.")


@router.get("/qrcode/{material_id}/{weight}", response_model=QrCodeResponse, response_description="Gera um QR Code em formato JSON e o exibe diretamente na tela do navegador.")
async def qr_code_validation(material_id: int, weight: float):
    """
    Gera um QR Code em formato JSON e o exibe diretamente na tela do navegador.
    """
    try:
        
        material_data_for_qrcode: dict = await retrieve_material_info(material_id)
        material_name = material_data_for_qrcode.get("material_name")  # Obtém o nome do material para incluir na resposta
        
        # Monta os dados no formato que o POST /recycle exige
        dados_para_qr = {
            "fk_cd_material": material_id,
            "nr_weight_kilograms": weight
        }
        
        # Converte o dicionário Python para um texto JSON
        texto_json = json.dumps(dados_para_qr)
        
        # Efetivamente Gera a imagem do QRCode
        imagem = qrcode_gen(data=texto_json)
        
        # Asism vai tratar a imagem na memória para enviar pelo navegador sem salvar em disco
        img_byte_arr = io.BytesIO()
        imagem.save(img_byte_arr, format='PNG')
        
        # Pega o valor da imagem em bytes (img_byte_arr.getvalue()) e converte para base64 (opcional, caso queira enviar como string)
        img_encoded_text = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        return QrCodeResponse(
            material_name=material_name,
            weight=weight,
            qr_code_base64=f"data:image/png;base64,{img_encoded_text}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar QR Code: {e}")
