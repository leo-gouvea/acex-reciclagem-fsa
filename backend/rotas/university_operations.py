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
            print(response)
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
async def post_course(data: PostCourseRequest):
    """
    Adiciona um curso ao banco de Dados
    Informe o nome do Curso a ser inserido
    """
    
@router.delete("/course/{id}")
async def delete_course(id: int):
    """
    Deleta um curso existente com base no ID
    """

# Adiciona e remove uma Turma ao DB
class PostClassRequest(BaseModel):
    class_code: str = Field(..., min_length=4, max_length=4, examples=["1A/M"])

class PostClassReturn(BaseModel):
    status: int
    detail: str

@router.post("/course", response_model=PostClassReturn, response_description="Retorna se a inserção foi um sucesso")
async def post_class():
    """
    Adiciona uma turma ao banco de Dados
    Informe a turma a ser inserida
    """
    
@router.delete("/class/{id}", response_description="Retorna se a deleção foi um sucesso")
async def delete_class(id: int):
    """
    Deleta um curso existente com base no ID
    """
