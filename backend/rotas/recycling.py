import os
import base64
import hashlib
import io
import secrets
from datetime import datetime, timedelta, timezone

import qrcode

import aiosqlite
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

# Importando para facilitar
from utils.jwt_validation import check_access

# Identificar rota de grupo e fora de main
router = APIRouter(
    prefix="/recycling",
    tags=["Reciclagem"]
)

# Usando os para navegar entre os arquivos de forma segura entre sistemas operacionais diferentes
DB_PATH = os.getenv("ECOHORA_DB_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db"))


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


# ==========================================
# SCHEMAS DE ENTRADA (REQUESTS)
# ==========================================

class PostMaterialRequest(BaseModel):
    material_name: str
    points_per_kilogram: int


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


@router.post(
    "/recycle",
    status_code=status.HTTP_410_GONE,
    response_description="O registro direto foi desativado; utilize a confirmação por QR Code."
)
async def post_recycle(user: dict = Depends(check_access)):
    """Bloqueia o registro direto para exigir validação por QR Code."""

    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="O registro direto foi desativado. As entregas devem ser confirmadas por QR Code."
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


# ==========================================
# FLUXO DE ENTREGA COM QR CODE
# ==========================================

QR_EXPIRATION_MINUTES = 10


class CreateRecyclingQRRequest(BaseModel):
    fk_cd_material: int
    nr_weight_kilograms: float = Field(..., ge=1, le=10)


def _qr_token_hash(token: str) -> str:
    """Gera o hash SHA-256 do token recebido."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _require_qr_role(user: dict, expected_role: str):
    if user.get("role") != expected_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para realizar esta operação."
        )


@router.post(
    "/qr",
    status_code=status.HTTP_201_CREATED,
    response_description="Gera um QR Code para uma entrega pendente."
)
async def create_recycling_qr(
    data: CreateRecyclingQRRequest,
    user: dict = Depends(check_access)
):
    """Somente administradores podem criar entregas para confirmação."""

    _require_qr_role(user, "Administrador")

    admin_id = user.get("id")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão administrativa inválida."
        )

    token = secrets.token_urlsafe(32)
    token_hash = _qr_token_hash(token)

    now = _utc_now()
    expires_at = now + timedelta(minutes=QR_EXPIRATION_MINUTES)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT id, nm_material, nr_points_per_kilogram
            FROM materials
            WHERE id = ?
            """,
            (data.fk_cd_material,)
        ) as cursor:
            material = await cursor.fetchone()

        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material não encontrado."
            )

        points_estimated = round(
            material["nr_points_per_kilogram"] * data.nr_weight_kilograms,
            2
        )

        await db.execute(
            """
            INSERT INTO recycling_qr_pending (
                token_hash,
                fk_cd_material,
                nr_weight_kilograms,
                fk_cd_admin,
                dt_expires_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                token_hash,
                data.fk_cd_material,
                data.nr_weight_kilograms,
                admin_id,
                expires_at.isoformat(timespec="seconds")
            )
        )

        await db.commit()

    frontend_url = os.getenv(
        "FRONTEND_BASE_URL",
        "http://localhost:5500"
    ).rstrip("/")

    confirmation_url = (
        f"{frontend_url}/confirmar-reciclagem.html?token={token}"
    )

    qr_image = qrcode.make(confirmation_url)
    image_buffer = io.BytesIO()
    qr_image.save(image_buffer, format="PNG")

    qr_base64 = base64.b64encode(
        image_buffer.getvalue()
    ).decode("utf-8")

    return {
        "detail": "QR Code gerado com sucesso.",
        "material": material["nm_material"],
        "weight": data.nr_weight_kilograms,
        "estimated_points": points_estimated,
        "expires_at": expires_at.isoformat(timespec="seconds"),
        "confirmation_url": confirmation_url,
        "qr_code_base64": f"data:image/png;base64,{qr_base64}"
    }


@router.get(
    "/qr/{token}",
    response_description="Consulta os dados de uma entrega pendente."
)
async def get_recycling_qr(
    token: str,
    user: dict = Depends(check_access)
):
    """Somente alunos autenticados podem consultar a entrega."""

    _require_qr_role(user, "Aluno")

    token_hash = _qr_token_hash(token)

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute(
            """
            SELECT
                p.id,
                p.nr_weight_kilograms,
                p.dt_expires_at,
                p.dt_redeemed_at,
                m.nm_material,
                m.nr_points_per_kilogram
            FROM recycling_qr_pending p
            INNER JOIN materials m ON m.id = p.fk_cd_material
            WHERE p.token_hash = ?
            """,
            (token_hash,)
        ) as cursor:
            delivery = await cursor.fetchone()

    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR Code inválido ou não encontrado."
        )

    if delivery["dt_redeemed_at"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta entrega já foi confirmada."
        )

    expires_at = datetime.fromisoformat(delivery["dt_expires_at"])

    if _utc_now() >= expires_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este QR Code expirou."
        )

    points = round(
        delivery["nr_points_per_kilogram"]
        * delivery["nr_weight_kilograms"],
        2
    )

    return {
        "detail": "Entrega disponível para confirmação.",
        "material": delivery["nm_material"],
        "weight": delivery["nr_weight_kilograms"],
        "points": points,
        "expires_at": delivery["dt_expires_at"]
    }


@router.post(
    "/qr/{token}/confirm",
    response_model=RecyclingResponse,
    status_code=status.HTTP_201_CREATED,
    response_description="Confirma a entrega e credita os pontos ao aluno."
)
async def confirm_recycling_qr(
    token: str,
    user: dict = Depends(check_access)
):
    """Confirma uma entrega uma única vez e credita os pontos ao aluno."""

    _require_qr_role(user, "Aluno")

    student_id = user.get("id")

    if not student_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão do aluno inválida."
        )

    token_hash = _qr_token_hash(token)
    now = _utc_now()
    now_iso = now.isoformat(timespec="seconds")

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON")
        db.row_factory = aiosqlite.Row

        # Serializa as confirmações concorrentes no SQLite.
        await db.execute("BEGIN IMMEDIATE")

        async with db.execute(
            """
            SELECT
                p.id,
                p.fk_cd_material,
                p.nr_weight_kilograms,
                p.dt_expires_at,
                p.dt_redeemed_at,
                m.nr_points_per_kilogram
            FROM recycling_qr_pending p
            INNER JOIN materials m ON m.id = p.fk_cd_material
            WHERE p.token_hash = ?
            """,
            (token_hash,)
        ) as cursor:
            delivery = await cursor.fetchone()

        if not delivery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR Code inválido ou não encontrado."
            )

        if delivery["dt_redeemed_at"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta entrega já foi confirmada."
            )

        expires_at = datetime.fromisoformat(delivery["dt_expires_at"])

        if now >= expires_at:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Este QR Code expirou."
            )

        points_earned = round(
            delivery["nr_points_per_kilogram"]
            * delivery["nr_weight_kilograms"],
            2
        )

        # A atualização condicional impede a reutilização do token.
        async with db.execute(
            """
            UPDATE recycling_qr_pending
            SET
                dt_redeemed_at = ?,
                fk_cd_user_redeemed = ?
            WHERE id = ?
              AND dt_redeemed_at IS NULL
              AND dt_expires_at > ?
            """,
            (
                now_iso,
                student_id,
                delivery["id"],
                now_iso
            )
        ) as cursor:
            if cursor.rowcount != 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Esta entrega não está mais disponível."
                )

        async with db.execute(
            """
            UPDATE users
            SET nr_points = nr_points + ?
            WHERE id = ?
            """,
            (points_earned, student_id)
        ) as cursor:
            if cursor.rowcount != 1:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Aluno não encontrado."
                )

        await db.execute(
            """
            INSERT INTO recycling (
                fk_cd_material,
                nr_weight_kilograms,
                fk_cd_user
            )
            VALUES (?, ?, ?)
            """,
            (
                delivery["fk_cd_material"],
                delivery["nr_weight_kilograms"],
                student_id
            )
        )

        async with db.execute(
            "SELECT nr_points FROM users WHERE id = ?",
            (student_id,)
        ) as cursor:
            total_points_row = await cursor.fetchone()

        total_points = round(total_points_row["nr_points"], 2)

        await db.commit()

    return RecyclingResponse(
        status=201,
        detail="Entrega confirmada e pontos creditados com sucesso!",
        points_earned=points_earned,
        total_points=total_points
    )
