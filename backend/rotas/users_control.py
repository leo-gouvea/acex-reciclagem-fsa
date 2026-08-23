# Imports das bibliotecas
# Nativos
import os
import re

# Instalados (check requirements)
import aiosqlite
import bcrypt
from fastapi import APIRouter, HTTPException, status, Path
from pydantic import BaseModel, Field, EmailStr

# Identificar rota de grupo e fora de main
router = APIRouter(prefix="/user", tags=["Registro"])

# Usando os para navegar entre os arquivos de forma segura entre sistemas operacionais diferentes
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")

# Padrão de senha para PydanticV2
PATTERN_PASSWORD = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_.])[A-Za-z\d@$!%*?&_.]+$")

# Identifica padrão de Request para registro
class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=60, title="Nome de usuário", description='Seu nome de Identificação.')
    ra: str = Field(..., min_length=6, max_length=6, title="RA do Aluno", description="Seu Registro de Aluno na Universidade.")
    # Adicionada validação de email com Pydantic já
    email: EmailStr = Field(..., max_lenght=150, title="Email institucional da universidade.", description="Adicione seu email para contato.")
    password: str = Field(..., examples=["Senha0_Forte"], min_length=6, pattern=PATTERN_PASSWORD, title="Senha de usuário", description="Adicione a senha do usuário. Deve incluir pelo menos 6 caracteres, uma letra maiúscula, uma letra minúscula e um símbolo especial.")
    cd_course: int = Field(..., ge=1, le=23, title="Código do curso do estudante.", description="Adicione o código do curso do estudante.")
    cd_class: int = Field(..., ge=1, le=10, title="Código da turma do aluno.", description="Digite o código da turma do aluno a ser cadastrado.")
    user_type: int = Field(..., ge=1, le=3, title="Tipo de usuário a ser cadastrado.", description="Adicione o código de tipo de usuário a ser cadastrado.")

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
        INSERT INTO users (nm_student, nr_ra, fk_cd_course, fk_cd_class, ds_email, ds_password, fk_cd_user_type) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        # Executa a inserção direto na conexão do banco (db)
        await db.execute(query_insert, (user.name, user.ra, user.cd_course, user.cd_class, user.email, user_password_hash_text, user.user_type))
        await db.commit()

    return {
        "status": 200,
        "detail": "Cadastro realizado com sucesso."
    }



# Identifica o padrão de Request (entrada) para o login
class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=150, title="Email institucional", description="Digite o e-mail cadastrado.")
    password: str = Field(..., pattern=PATTERN_PASSWORD, title="Senha de usuário", description="Digite a senha para entrar.")

# Identifica o padrão de Return (saída) para o login
class UserLoginReturn(BaseModel):
    status: int
    detail: str

@router.post("/login", response_model=UserLoginReturn, response_description="Verifica se o usuário tem permissão para entrar.")
async def user_login(credentials: UserLoginRequest):
    """
    Rota para autenticar (fazer login) o usuário no sistema.
    """
    
    # Abre a conexão com o banco de dados
    async with aiosqlite.connect(DB_PATH) as db:
        
        # Prepara a pergunta para o banco
        query_busca = "SELECT ds_password FROM users WHERE ds_email = ?"
        
        # Executa a busca
        async with db.execute(query_busca, (credentials.email,)) as cur:
            resultado = await cur.fetchone()
            
            # Se não encontrou o e-mail no banco, o resultado será vazio (None)
            if not resultado:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="E-mail ou senha incorretos."
                )
            
            # Se chegou aqui, o e-mail existe, então pega a senha que veio do banco (em texto)
            hash_salvo_texto = resultado[0]
            
            # Transforma o texto do banco de volta para bytes
            hash_salvo_bytes = hash_salvo_texto.encode("utf-8")
            
            # Transforma a senha que o usuário digitou para bytes para comparar
            senha_tentativa_bytes = credentials.password.encode("utf-8")
            
            # A hora da verdade onde o bcrypt compara as duas senhas
            if bcrypt.checkpw(senha_tentativa_bytes, hash_salvo_bytes):
                # Se as senhas baterem, devolve sucesso
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
    nm_material: str
    nr_weight_kilograms: float
    dh_gave: str

class GetUserInfosReturn(BaseModel):
    id: int
    nm_student: str
    nr_ra: str
    ds_email: str
    dh_created_at: str
    ds_class: str
    nm_course: str
    nm_type: str
    recycling: list[RecyclingHistoryScheme]

# Rota de recuperação de informação
@router.get("/get/{user_ra}", response_model=GetUserInfosReturn, response_description="Retorna todas as informações relacionadas a um usuário, removendo o campo de senha.")
async def user_get(user_ra: int = Path(description="Número de RA do aluno.", examples=["123456"], title="RA do Aluno.")):
    """Obtém informações relacionadas a um usuário usando um RA"""

    async with aiosqlite.connect(DB_PATH) as db:
        # Para poder manipular como dicionário, ao invés de retornar uma tupla comum ele retorna um objeto aiosqlite.Row
        db.row_factory = aiosqlite.Row

        query1 = """
        SELECT users.*, 
        classes.ds_class,
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
            INNER JOIN users ON users.id = recycling.fk_cd_student
            INNER JOIN materials ON recycling.fk_cd_material = materials.id
            WHERE users.nr_ra = ?"""

            await cur.execute(query2, (response1["nr_ra"],))

            response2 = await cur.fetchall()

            # Conversão dos objetos para uma lista de dicionarios
            all_recycles = [dict(row) for row in response2]
            # Junção da resposta
            response1["recycling"] = all_recycles
            return response1