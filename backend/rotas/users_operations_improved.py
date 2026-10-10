# Imports das bibliotecas
# Nativos
import os
import re

# Instalados (check requirements)
import aiosqlite
import bcrypt
from fastapi import APIRouter, HTTPException, status, Path, Depends, Response
from pydantic import BaseModel, Field, EmailStr
import jwt

# Importando do main para facilitar
from main import check_access

# Identificar rota de grupo e fora de main
router = APIRouter(
    prefix="/user",
    tags=["Usuários"]
)

# Usando os para navegar entre os arquivos de forma segura entre sistemas operacionais diferentes
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")

# Padrão de senha para PydanticV2
PATTERN_PASSWORD = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_.])[A-Za-z\d@$!%*?&_.]+$")

# ==========================================
# SCHEMAS DE RETORNO (RESPONSES)
# ==========================================

class UserRegisterReturn(BaseModel):
    """
    Modelo padrão de retorno para cadastro realizado com sucesso.
    """
    status: int = 201
    detail: str = "Cadastro realizado com sucesso."


class UserLoginReturn(BaseModel):
    """
    Modelo padrão de retorno para login autenticado com sucesso.
    """
    status: int = 200
    detail: str = "Login aprovado com sucesso! Bem-vindo."


class RecyclingHistoryScheme(BaseModel):
    id: int
    material: str
    weight_kilograms: float
    gave_at: str


class GetUserInfosReturn(BaseModel):
    id: int
    name: str
    ra: str
    email: str
    created_at: str
    user_class: str
    course: str
    user_type: str
    recycling: list[RecyclingHistoryScheme]


class UserUpdateReturn(BaseModel):
    id: int
    ra: str
    name: str
    email: str
    course: str
    user_class: str
    user_type: str


class SessionReturn(BaseModel):
    authenticated: bool
    user: dict


class LogoutReturn(BaseModel):
    status: int = 200
    detail: str = "Logout realizado com sucesso."


class UserRankingReturn(BaseModel):
    id: int
    name: str
    ra: str
    points: float


# ==========================================
# SCHEMAS DE ENTRADA (REQUESTS)
# ==========================================

class UserRegisterRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=3,
        max_length=60,
        title="Nome de usuário",
        description='Seu nome de Identificação.'
    )
    ra: str = Field(
        ...,
        min_length=6,
        max_length=6,
        title="RA do Aluno (Não editável)",
        description="Seu Registro de Aluno na Universidade."
    )
    email: EmailStr = Field(
        ...,
        max_length=150,
        title="Email institucional da universidade.",
        description="Adicione seu email para contato."
    )
    password: str = Field(
        ...,
        examples=["Senha0_Forte"],
        min_length=6,
        pattern=PATTERN_PASSWORD,
        title="Senha de usuário",
        description="Deve incluir pelo menos 6 caracteres, uma letra maiúscula, uma letra minúscula e um símbolo especial."
    )
    course: int | None= Field(
        default=None,
        ge=1,
        le=23,
        title="Código do curso do estudante.",
        description="Adicione o código do curso do estudante."
    )
    user_class: int | None = Field(
        default=None,
        ge=1,
        le=10,
        title="Código da turma do aluno.",
        description="Digite o código da turma do aluno a ser cadastrado."
    )
    user_type: int = Field(
        1,
        ge=1,
        le=3,
        title="Tipo de usuário a ser cadastrado.",
        description="Adicione o código de tipo de usuário a ser cadastrado."
    )


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=150, title="Email institucional", description="Digite o e-mail cadastrado.")
    password: str = Field(..., examples=["Senha0_Forte"], pattern=PATTERN_PASSWORD, title="Senha de usuário", description="Digite a senha para entrar.")


class UserUpdateRequest(BaseModel):
    ra: str = Field(
        ...,
        title="O RA do Usuário.",
        description="Adicione o RA do usuário que será editado.",
        max_length=6,
        min_length=6
    )
    name: str | None = Field(
        default=None,
        title="Nome (Opcional)",
        description="Caso o usuário altere o nome.",
        max_length=150,
        min_length=6
    )
    email: EmailStr | None = Field(
        default=None,
        title="Email (Opcional)",
        description="Caso o usuário altere o e-mail."
    )
    course: int | None = Field(
        default=None,
        title="Código de curso (Opcional)",
        description="Caso o usuário altere o curso.",
        ge=1,
        le=23
    )
    user_class: int | None = Field(
        default=None,
        title="Código de turma (Opcional)",
        description="Caso o usuário altere a turma.",
        ge=1,
        le=10
    )
    user_type: int | None = Field(
        default=None,
        title="Código de tipo de usuário (Opcional)",
        description="Caso o usuário venha a ter seu cargo alterado.",
        ge=1,
        le=3
    )


# ==========================================
# ROTAS / ENDPOINTS
# ==========================================

@router.post("/register", response_model=UserRegisterReturn, status_code=status.HTTP_201_CREATED, response_description="Identifica se a operação foi um sucesso.")
async def user_register(user: UserRegisterRequest):
    """
    Cria um usuário na base de dados SQLite (ecohora.db).
    """
    async with aiosqlite.connect(DB_PATH) as db:
        query_check = "SELECT nr_ra, ds_email FROM users WHERE nr_ra = ? OR ds_email = ?"
        
        async with db.execute(query_check, (user.ra, user.email)) as cur:
            results = await cur.fetchone()
            if results:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O registro de RA ou e-mail já existe.")

        # Criptografia segura com bcrypt
        user_password_bytes = user.password.encode("utf-8")
        user_password_bytes_salt = bcrypt.gensalt()
        user_password_hash = bcrypt.hashpw(user_password_bytes, user_password_bytes_salt)
        user_password_hash_text = user_password_hash.decode("utf-8")
        
        query_insert = """
        INSERT INTO users (nm_user, nr_ra, fk_cd_course, fk_cd_class, ds_email, ds_password, fk_cd_user_type) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        await db.execute(
            query_insert, 
            (user.name, user.ra, user.course, user.user_class, user.email, user_password_hash_text, user.user_type)
        )
        await db.commit()

    return UserRegisterReturn()


@router.post("/login", response_model=UserLoginReturn, status_code=status.HTTP_200_OK, response_description="Verifica se o usuário tem permissão para entrar.")
async def user_login(credentials: UserLoginRequest, response: Response):
    """
    Rota para autenticar (fazer login) o usuário no sistema.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        query_search = """
        SELECT users.id, users.nm_user, users.nr_ra, users.ds_password, user_types.nm_type
        FROM users
        INNER JOIN user_types ON user_types.id = users.fk_cd_user_type
        WHERE users.ds_email = ?
        """
        
        async with db.execute(query_search, (credentials.email,)) as cur:
            result = await cur.fetchone()
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="E-mail ou senha incorretos."
                )
            
            saved_password_bytes = result["ds_password"].encode("utf-8")
            tried_password_bytes = credentials.password.encode("utf-8")
            
            if not bcrypt.checkpw(tried_password_bytes, saved_password_bytes):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="E-mail ou senha incorretos."
                )
                
            user_data = {
                "origin": "site",
                "id": result["id"],
                "name": result["nm_user"],
                "ra": result["nr_ra"],
                "role": result["nm_type"]
            }
            
            master_key = os.getenv("ECO_HORA_API_KEY")
            token_jwt = jwt.encode(user_data, master_key, algorithm="HS256")
            
            response.set_cookie(
                key="access_token", 
                value=token_jwt,
                httponly=True,
                secure=True, 
                samesite="none"
            )

            return UserLoginReturn()


@router.get("/get/{user_ra}", response_model=GetUserInfosReturn, status_code=status.HTTP_200_OK, response_description="Retorna todas as informações relacionadas a um usuário, removendo o campo de senha.")
async def user_get(user_ra: str = Path(description="Número de RA do aluno.", examples=["123456"], title="RA do Aluno."), user: dict = Depends(check_access)):
    """Obtém informações relacionadas a um usuário usando um RA.
    * Usuários Alunos só podem puxar o próprio perfil."""

    if user.get("role") == "Aluno" and user.get("ra") != user_ra:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso Negado! Você só pode visualizar o seu próprio perfil."
        )
        
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        query1 = """
        SELECT users.id, users.nm_user, users.nr_ra, users.ds_email, users.dt_created_at,
               classes.ds_class_code, courses.nm_course, user_types.nm_type
        FROM users 
        INNER JOIN classes ON users.fk_cd_class = classes.id
        INNER JOIN courses ON users.fk_cd_course = courses.id
        INNER JOIN user_types ON users.fk_cd_user_type = user_types.id
        WHERE users.nr_ra = ?
        """

        async with db.execute(query1, (user_ra,)) as cur:
            response1 = await cur.fetchone()
            if not response1:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
            
            query2 = """
            SELECT recycling.id, materials.nm_material, recycling.nr_weight_kilograms, recycling.dt_gave
            FROM recycling
            INNER JOIN users ON users.id = recycling.fk_cd_user
            INNER JOIN materials ON recycling.fk_cd_material = materials.id
            WHERE users.nr_ra = ?
            """
            
            async with db.execute(query2, (user_ra,)) as history_cur:
                response2 = await history_cur.fetchall()
                all_recycles = [
                    RecyclingHistoryScheme(
                        id=row["id"],
                        material=row["nm_material"],
                        weight_kilograms=row["nr_weight_kilograms"],
                        gave_at=row["dt_gave"]
                    )
                    for row in response2
                ]
                
        return GetUserInfosReturn(
            id=response1["id"],
            name=response1["nm_user"],
            ra=response1["nr_ra"],
            email=response1["ds_email"],
            created_at=response1["dt_created_at"],
            user_class=response1["ds_class_code"],
            course=response1["nm_course"],
            user_type=response1["nm_type"],
            recycling=all_recycles
        )
            
@router.patch("/update", response_model=UserUpdateReturn, status_code=status.HTTP_200_OK, response_description="Retorna os dados atualizados do usuário.")
async def user_update(data: UserUpdateRequest, user: dict = Depends(check_access)):
    """
    Atualiza o perfil de um usuário, exceto o RA.
    """
    if user.get("role") == "Aluno" and data.ra != user.get("ra"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado, você não pode alterar outros perfis."
        )
        
    # Proteção adicional estrutural de privilégio de cargo
    if data.user_type and user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem alterar o tipo/cargo de um usuário."
        )
    
    update_fields = []
    data_list = []
    
    if data.name:
        update_fields.append("nm_user = ?")
        data_list.append(data.name)
        
    if data.email:
        update_fields.append("ds_email = ?")
        data_list.append(data.email)

    if data.course:
        update_fields.append("fk_cd_course = ?")
        data_list.append(data.course)
    
    if data.user_class:
        update_fields.append("fk_cd_class = ?")
        data_list.append(data.user_class)
    
    if data.user_type:
        update_fields.append("fk_cd_user_type = ?")
        data_list.append(data.user_type)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado foi enviado para atualização."
        )

    query = f"UPDATE users SET {', '.join(update_fields)} WHERE nr_ra = ?"
    data_list.append(data.ra)
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
    
        async with db.execute(query, tuple(data_list)) as update_cur:
            if update_cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado para atualização."
                )
                    
        await db.commit()
    
        query_updated = """
        SELECT users.id, users.nr_ra, users.nm_user, users.ds_email,
        courses.nm_course, classes.ds_class_code, user_types.nm_type
        FROM users
        INNER JOIN courses ON courses.id = users.fk_cd_course
        INNER JOIN classes ON classes.id = users.fk_cd_class
        INNER JOIN user_types ON user_types.id = users.fk_cd_user_type
        WHERE users.nr_ra = ?
        """
        
        async with db.execute(query_updated, (data.ra,)) as cur:
            response = await cur.fetchone()
            if not response:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuário não encontrado após atualização."
                )
        
        return UserUpdateReturn(
            id=response["id"],
            ra=response["nr_ra"],
            name=response["nm_user"],
            email=response["ds_email"],
            course=response["nm_course"],
            user_class=response["ds_class_code"],
            user_type=response["nm_type"]
        )
    
    
@router.get("/session", response_model=SessionReturn, status_code=status.HTTP_200_OK)
async def check_session(response: Response, user: dict = Depends(check_access)):
    """
    Verifica se existe uma sessão autenticada.
    """
    
    response.headers["Cache-Control"] = "no-store"
    
    return SessionReturn(authenticated=True, user=user)
    
    
@router.post("/logout", response_model=LogoutReturn, status_code=status.HTTP_200_OK)
async def logout(response: Response):
    """
    Encerra a sessão removendo o cookie 'access_token'.
    """
    
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="none"
    )
    response.headers["Cache-Control"] = "no-store"
    return LogoutReturn()


@router.get("/ranking", response_model=list[UserRankingReturn], status_code=status.HTTP_200_OK, response_description="Retorna o ranking de usuários baseado na soma de pontos.")
async def get_ranking(user: dict = Depends(check_access)):
    """
    Retorna o ranking de usuários baseado na soma de pontos.
    """
    
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
        SELECT users.id, users.nm_user, users.nr_ra, users.nr_points
        FROM users
        ORDER BY users.nr_points DESC
        LIMIT 10
        """
        
        async with db.execute(query) as cur:
        
            results = await cur.fetchall()
            
            return [
                UserRankingReturn(
                    id=row["id"],
                    name=row["nm_user"],
                    ra=row["nr_ra"],
                    points=row["nr_points"]
                )
                for row in results
            ]