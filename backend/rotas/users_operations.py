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

# Identifica padrão de Request para registro
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=60, title="Nome de usuário", description='Seu nome de Identificação.')
    ra: str = Field(..., min_length=6, max_length=6, title="RA do Aluno (Não editável)", description="Seu Registro de Aluno na Universidade. Esse número não poderá ser editado depois por meios convencionais.")
    # Adicionada validação de email com Pydantic já
    email: EmailStr = Field(..., max_lenght=150, title="Email institucional da universidade.", description="Adicione seu email para contato.")
    password: str = Field(..., examples=["Senha0_Forte"], min_length=6, pattern=PATTERN_PASSWORD, title="Senha de usuário", description="Adicione a senha do usuário. Deve incluir pelo menos 6 caracteres, uma letra maiúscula, uma letra minúscula e um símbolo especial.")
    course: int = Field(..., ge=1, le=23, title="Código do curso do estudante.", description="Adicione o código do curso do estudante.")
    user_class: int = Field(..., ge=1, le=10, title="Código da turma do aluno.", description="Digite o código da turma do aluno a ser cadastrado.")
    user_type: int = Field(1, ge=1, le=3, title="Tipo de usuário a ser cadastrado.", description="Adicione o código de tipo de usuário a ser cadastrado.")

# Identifica padrão de Return para registro
class UserRegisterReturn(BaseModel):
    status: int
    detail: str

@router.post("/register", response_model=UserRegisterReturn, response_description="Identifica se a operação foi um sucesso.")
async def user_register(user: UserRegisterRequest):
    """
    Cria um usuário na base de dados SQLite (ecohora.db) com os seguintes dados:
    * Nome
    * RA
    * Email
    * Senha
    * Código de curso
    * Código de turma
    * Tipo de usuário
    """

    # Conexão com o banco de dados de forma assíncrona
    async with aiosqlite.connect(DB_PATH) as db:
        
        # Query para verificar se o usuário já existe
        query_check = """
        SELECT nr_ra, ds_email FROM users WHERE nr_ra = ? OR ds_email = ?
        """
        async with db.execute(query_check, (user.ra, user.email)) as cur:
            results = await cur.fetchone()

            # Validação se já existe registro com os UNIQUES
            if results:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="O registro de RA ou e-mail já existe.")

        # Caso não haja, ele continua aqui 

        # Codifica a senha de texto para bytes 
        user_password_bytes = user.password.encode("utf-8")

        # Gera um salt para a senha do usuário
        user_password_bytes_salt = bcrypt.gensalt()

        # Cria um hash de senha do usuário, incluindo o salt diretamente
        user_password_hash = bcrypt.hashpw(user_password_bytes, user_password_bytes_salt)

        # Volta de bytes para texto para salvar no DB (processo inverso para comparação em check login)
        user_password_hash_text = user_password_hash.decode("utf-8")
        
        # Query para inserir o novo usuário
        query_insert = """
        INSERT INTO users (nm_user, nr_ra, fk_cd_course, fk_cd_class, ds_email, ds_password, fk_cd_user_type) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # Executa a inserção direto na conexão do banco (db)
        await db.execute(query_insert, (user.name, user.ra, user.course, user.user_class, user.email, user_password_hash_text, user.user_type))
        await db.commit()

    return {
        "status": 200,
        "detail": "Cadastro realizado com sucesso."
    }



# Identifica o padrão de Request (entrada) para o login
class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=150, title="Email institucional", description="Digite o e-mail cadastrado.")
    password: str = Field(..., examples=["Senha_Fraca1"], pattern=PATTERN_PASSWORD, title="Senha de usuário", description="Digite a senha para entrar.")

# Identifica o padrão de Return (saída) para o login
class UserLoginReturn(BaseModel):
    status: int
    detail: str

@router.post("/login", response_model=UserLoginReturn, response_description="Verifica se o usuário tem permissão para entrar.")
async def user_login(credentials: UserLoginRequest, response: Response):
    """
    Rota para autenticar (fazer login) o usuário no sistema.
    """
    
    # Abre a conexão com o banco de dados
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Prepara a pergunta para o banco
        query_search = """
        SELECT users.id, users.nm_user, users.nr_ra, users.ds_password, user_types.nm_type
        FROM users
        INNER JOIN user_types ON user_types.id = users.fk_cd_user_type
        WHERE users.ds_email = ?
        """
        
        # Executa a busca
        async with db.execute(query_search, (credentials.email,)) as cur:
            result = await cur.fetchone()
            
            # Se não encontrou o e-mail no banco, o resultado será vazio (None)
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="E-mail ou senha incorretos."
                )
            
            # Se chegou aqui, o e-mail existe, então pega a senha que veio do banco (em texto)
            saved_password_hash = result["ds_password"]
            
            # Transforma o texto do banco de volta para bytes
            saved_password_bytes = saved_password_hash.encode("utf-8")
            
            # Transforma a senha que o usuário digitou para bytes para comparar
            tried_password_bytes = credentials.password.encode("utf-8")
            
            # A hora da verdade onde o bcrypt compara as duas senhas
            if bcrypt.checkpw(tried_password_bytes, saved_password_bytes):
                # Se as senhas baterem, devolve sucesso

                # Prepara os dados apra irem ao Cookie
                user_data = {
                    "origin": "site",
                    "id": result["id"],
                    "name": result["nm_user"],
                    "ra": result["nr_ra"],
                    "role": result["nm_type"]
                }
                
                # Criamos o Token usando assinatura da KEY que ja temos, por isso busca com os na env
                master_key = os.getenv("ECO_HORA_API_KEY")
                token_jwt = jwt.encode(user_data, master_key, algorithm="HS256")
                
                # Colocamos o Token no Cookie e mandamos para o navegador
                response.set_cookie(
                    key="access_token", 
                    value=token_jwt,
                    httponly=True,
                    secure=True, 
                    samesite="none"
                )

                return {
                    "status": 200,
                    "detail": "Login aprovado com sucesso! Bem-vindo."
                }
            else:
                # Se a senha estiver errada, bloqueia o acesso.
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="E-mail ou senha incorretos."
                )


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

# Rota de recuperação de informação
@router.get("/get/{user_ra}", response_model=GetUserInfosReturn, response_description="Retorna todas as informações relacionadas a um usuário, removendo o campo de senha.")
async def user_get(user_ra: str = Path(description="Número de RA do aluno.", examples=["123456"], title="RA do Aluno."), user: dict = Depends(check_access)):
    """Obtém informações relacionadas a um usuário usando um RA.
    * Usuários **NÃO** Operadores podem puxar apenas as próprias informações."""


    # VALIDAÇÃO EXTRA
    # Verifica se quem está acessando tem o cargo de Aluno
    if user["role"] == "Aluno":
        # Transforma ambos em texto (str) para garantir que a comparação não dê erro
        if user["ra"] != user_ra:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Acesso Negado! Você só pode visualizar o seu próprio perfil."
            )

        
    async with aiosqlite.connect(DB_PATH) as db:
        # Para poder manipular como dicionário, ao invés de retornar uma tupla comum ele retorna um objeto aiosqlite.Row
        db.row_factory = aiosqlite.Row

        query1 = """
        SELECT users.*, 
        classes.ds_class_code,
        courses.nm_course,
        user_types.nm_type
        FROM users 
        INNER JOIN classes ON users.fk_cd_class = classes.id
        INNER JOIN courses ON users.fk_cd_course = courses.id
        INNER JOIN user_types ON users.fk_cd_user_type = user_types.id
        WHERE users.nr_ra = ?
        """

        async with db.execute(query1, (user_ra,)) as cur:
            response1 = await cur.fetchone() # Vem como Objeto Row ou None

            if not response1:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
            response1 = dict(response1) # Converte em dicionário e atualiza a var

            print(response1)
            # Remove os itens em números de Curso e Classe, senha e tipo de usuário
            response1.pop("fk_cd_course")
            response1.pop("fk_cd_class")
            response1.pop("ds_password")
            response1.pop("fk_cd_user_type")

            # Segunda busca
            query2 = """
            SELECT recycling.id,
            materials.nm_material,
            recycling.nr_weight_kilograms,
            dh_gave
            FROM recycling
            INNER JOIN users ON users.id = recycling.fk_cd_user
            INNER JOIN materials ON recycling.fk_cd_material = materials.id
            WHERE users.nr_ra = ?"""

            await cur.execute(query2, (response1["nr_ra"],))

            response2 = await cur.fetchall()

            #Normalização das chaves do dicionário
            all_recycles = [{
                "id": row["id"],
                "material": row["nm_material"],
                "weight_kilograms": row["nr_weight_kilograms"],
                "gave_at": row["dh_gave"]
            } for row in response2]

            # Junção da resposta e normalização das chaves
            response = {
                "id": response1["id"],
                "name": response1["nm_user"],
                "ra": response1["nr_ra"],
                "email": response1["ds_email"],
                "created_at": response1["dh_created_at"],
                "user_class": response1["ds_class_code"],
                "course": response1["nm_course"],
                "user_type": response1["nm_type"],
                "recycling": all_recycles
            }

            return response


class UserUpdateRequest(BaseModel):
    ra: str = Field(..., title="O RA do Usuário.", description="Adicione o RA do usuáro que será editado.", max_length=6, min_length=6)
    name: str | None = Field(title="Nome (Opcional)", description="Caso o usuário altere o nome.", max_length=150, min_length=6)
    email: EmailStr | None = Field(title="Email (Opcional)", description="Caso o usuário altere o e-mail.")
    course: int | None = Field(title="Código de curso (Opcional)", description="Caso o usuário altere o curso.", ge=1, le=23)
    user_class: int | None = Field(title="Código de turma (Opcional)", description="Caso o usuário altere a turma.", ge=1, le=10)
    user_type: int | None = Field(title="Código de tipo de usuário (Opcional)", description="Caso o usuário venha a ter seu cargo alterado.", ge=1, le=3)
    # password: str | None = Field(title="Nova senha (Opcional)", description="Caso o usuário altere a senha.", examples=["S3nh4*B04"], pattern=PATTERN_PASSWORD)

class UserUpdateReturn(BaseModel):
    id: int
    ra: str
    name: str
    email: str
    course: str
    user_class: str
    user_type: str

@router.patch("/update", response_model=UserUpdateReturn, response_description="Retorna os dados atualizados do usuário.")
async def user_update(data: UserUpdateRequest, user: dict = Depends(check_access)):
    """
    Atualiza o perfil de um usuário, **exceto o RA**.
    * Alunos **só** podem atualizar seus próprios perfis. 
    """
    # Verifica permissão do Aluno
    if user["role"] == "Aluno":
        if data.ra != user["ra"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Acesso negado, você não pode alterar outros perfis."
            )

    # Listas para guardar os pedaços do SQL e os valores
    update_fields = []
    data_list = []

    # Cria as adições e insere na lista de campos e de valores se existirem
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

    # Se a lista de campos estiver vazia, significa que nada foi enviado para atualizar
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhum dado foi enviado para atualização."
        )

    # Junta todos os campos com uma vírgula e espaço de forma segura
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE nr_ra = ?"
    data_list.append(data.ra)
    
    # Transforma a lista em uma tupla, que é o formato exigido pelo aiosqlite
    data_tuple = tuple(data_list)

    # Conecta no banco de dados e executa
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Executa a atualização
        await db.execute(query, data_tuple)
        await db.commit()

        # Busca os dados atualizados
        query_updated = """
        SELECT users.*, courses.nm_course, classes.ds_class_code, user_types.nm_type
        FROM users
        INNER JOIN courses ON courses.id = users.fk_cd_course
        INNER JOIN classes ON classes.id = users.fk_cd_class
        INNER JOIN user_types ON user_types.id = users.fk_cd_user_type
        WHERE users.nr_ra = ?
        """
        
        # Executa a busca
        async with db.execute(query_updated, (data.ra,)) as cur:
            response = await cur.fetchone()

        # Se não encontrar o usuário no banco (RA inválido)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        # Formata a resposta
        formated_response = {
            "id": response["id"],
            "ra": response["nr_ra"],
            "name": response["nm_user"],
            "email": response["ds_email"],
            "course": response["nm_course"],
            "user_class": response["ds_class_code"],
            "user_type": response["nm_type"]
        }

        return formated_response


# AUTENTICAÇÃO DE SESSÃO
# ----------------------
@router.get("/user/session")
async def check_session(
    response: Response,
    user: dict = Depends(check_access)
):
    """
    Verifica se existe uma sessão autenticada.

    O endpoint utiliza o mesmo mecanismo de autenticação
    das demais rotas protegidas, através do cookie
    'access_token' ou da chave X-API-Key.

    Retorna os dados do usuário caso a autenticação seja válida.
    Caso contrário, check_access() retorna HTTP 401.
    """

    # Impede que navegador ou proxy reutilize uma resposta antiga.
    response.headers["Cache-Control"] = "no-store"

    return {
        "authenticated": True,
        "user": user
    }


@router.post("/user/logout")
async def logout(response: Response):
    """
    Encerra a sessão removendo o cookie 'access_token'.

    A rota não exige autenticação para permitir que o logout
    funcione mesmo quando o token estiver inválido ou expirado.
    """

    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="none"
    )

    # Impede o armazenamento da resposta em cache.
    response.headers["Cache-Control"] = "no-store"

    return {
        "status": 200,
        "detail": "Logout realizado com sucesso."
    }