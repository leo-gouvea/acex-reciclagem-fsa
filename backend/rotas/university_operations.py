import os

import aiosqlite
from fastapi import APIRouter, HTTPException, status, Path, Depends
from pydantic import BaseModel, Field

# Importando do main para facilitar
from main import check_access

router = APIRouter(
    prefix="/fsa",
    tags=["Faculdade"],
    )

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")


class CoursesSchema(BaseModel):
    id: int
    course: str

@router.get("/get/courses", response_model=list[CoursesSchema], response_description="Retorna todos os cursos cadastrados.")
async def get_courses():
    """Retorna todos os cursos e suas IDs cadastrados no sistema."""

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
        SELECT *
        FROM courses
        """
        async with db.execute(query) as cur:
            response = await cur.fetchall()
            # O FastAPI ja identifica como lista de dicts para a documentação, ent~eo é feita apenas uma trona de nomes para facilitação de front.
            response = [{"id": row["id"], "course": row["nm_course"]} for row in response]
            return response 


# Esse sistema é passível de mudança
class ClassesScheme(BaseModel):
    id: int
    class_code: str

@router.get("/get/classes", response_model=list[ClassesScheme], response_description="Retorna as salas cadastradas.")
async def get_classes():
    """Retorna todas as turmas e suas IDs cadastradas no sistema."""

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = """
        SELECT *
        FROM classes
        """

        async with db.execute(query) as cur:
            response = await cur.fetchall()
            # O FastAPI ja identifica como lista de dicts para a documentação, mas naturalmente são apenas objetos, então ainda é feita a conversão.
            response = [{"id": row["id"], "class_code": row["ds_class_code"]} for row in response]
            return response



# ADICIONAR VERIFICAÇÃO DE HIERARQUIA POR COOKIE
# Adiciona e remove um Curso ao DB
class PostCourseRequest(BaseModel):
    course_name: str = Field(..., min_length=5, examples=["Análise e Desenvolvimento de Sistemas"])

class PostCourseReturn(BaseModel):
    status: int
    detail: str

@router.post("/course", response_model=PostCourseReturn, response_description="Retorna se a inserção foi um sucesso")
async def post_course(data: PostCourseRequest, user: dict = Depends(check_access)):
    """
    Adiciona um curso ao banco de Dados
    Informe o nome do Curso a ser inserido
    """

    # ADICIONAR VERIFICAÇÃO DE HIERARQUIA POR COOKIE
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem adicionar cursos.")

    async with aiosqlite.connect(DB_PATH) as db:
        query = """
        INSERT INTO courses (nm_course)
        VALUES (?)
        """
        try:
            await db.execute(query, (data.course_name,))
            await db.commit()
            return {"status": 200, "detail": "Curso inserido com sucesso."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao inserir curso: {str(e)}")
        
    
@router.delete("/course/{id}")
async def delete_course(id: int, user: dict = Depends(check_access)):
    """
    Deleta um curso existente com base no ID
    """

    # ADICIONAR VERIFICAÇÃO DE HIERARQUIA POR COOKIE
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem deletar cursos.")

    async with aiosqlite.connect(DB_PATH) as db:
        query = """
        DELETE FROM courses
        WHERE id = ?
        """
        try:
            await db.execute(query, (id,))
            await db.commit()
            return {"status": 200, "detail": "Curso deletado com sucesso."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar curso: {str(e)}")
        

# Adiciona e remove uma Turma ao DB
class PostClassRequest(BaseModel):
    class_code: str = Field(..., min_length=4, max_length=4, examples=["1A/M"])

class PostClassReturn(BaseModel):
    status: int
    detail: str

@router.post("/class", response_model=PostClassReturn, response_description="Retorna se a inserção foi um sucesso")
async def post_class(data: PostClassRequest, user: dict = Depends(check_access)):
    """
    Adiciona uma turma ao banco de Dados
    Informe a turma a ser inserida
    """

    # ADICIONAR VERIFICAÇÃO DE HIERARQUIA POR COOKIE
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem adicionar turmas.")

    async with aiosqlite.connect(DB_PATH) as db:
        query = """
        INSERT INTO classes (ds_class_code)
        VALUES (?)
        """
        try:
            await db.execute(query, (data.class_code,))
            await db.commit()
            return {"status": 200, "detail": "Turma inserida com sucesso."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao inserir turma: {str(e)}")
    
    
@router.delete("/class/{id}", response_description="Retorna se a deleção foi um sucesso")
async def delete_class(id: int, user: dict = Depends(check_access)):
    """
    Deleta uma turma existente com base no ID
    """

    # ADICIONAR VERIFICAÇÃO DE HIERARQUIA POR COOKIE
    if user.get("role") != "Administrador":
        raise HTTPException(status_code=403, detail="Acesso negado. Apenas administradores podem deletar turmas.")

    async with aiosqlite.connect(DB_PATH) as db:
        query = """
        DELETE FROM classes
        WHERE id = ?
        """
        try:
            await db.execute(query, (id,))
            await db.commit()
            return {"status": 200, "detail": "Turma deletada com sucesso."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao deletar turma: {str(e)}")