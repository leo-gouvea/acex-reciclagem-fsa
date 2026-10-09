import os

import aiosqlite
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field

# Importando do main para facilitar
from main import check_access

router = APIRouter(
    prefix="/fsa",
    tags=["Faculdade"],
)

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "ecohora.db")


# ==========================================
# SCHEMAS DE RETORNO (RESPONSES)
# ==========================================

class CoursesSchema(BaseModel):
    id: int
    course: str


class ClassesScheme(BaseModel):
    id: int
    class_code: str


class PostCourseReturn(BaseModel):
    status: int = 201
    detail: str = "Curso inserido com sucesso."
    course_id: int


class DeleteCourseReturn(BaseModel):
    status: int = 200
    detail: str = "Curso deletado com sucesso."


class PostClassReturn(BaseModel):
    status: int = 201
    detail: str = "Turma inserida com sucesso."
    class_id: int


class DeleteClassReturn(BaseModel):
    status: int = 200
    detail: str = "Turma deletada com sucesso."


# ==========================================
# SCHEMAS DE ENTRADA (REQUESTS)
# ==========================================

class PostCourseRequest(BaseModel):
    course_name: str = Field(
        ...,
        min_length=5, 
        examples=["Análise e Desenvolvimento de Sistemas"]
    )


class PostClassRequest(BaseModel):
    class_code: str = Field(
        ...,
        min_length=4,
        max_length=4,
        examples=["1A/M"]
    )


# ==========================================
# ROTAS / ENDPOINTS
# ==========================================

@router.get("/get/courses", response_model=list[CoursesSchema], response_description="Retorna todos os cursos cadastrados.")
async def get_courses():
    """Retorna todos os cursos e suas IDs cadastrados no sistema."""

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM courses"
        
        async with db.execute(query) as cur:
            response = await cur.fetchall()
            
        return [
            CoursesSchema(id=row["id"], course=row["nm_course"]) 
            for row in response
        ]


@router.get("/get/classes", response_model=list[ClassesScheme], response_description="Retorna as salas cadastradas.")
async def get_classes():
    """Retorna todas as turmas e suas IDs cadastradas no sistema."""

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM classes"

        async with db.execute(query) as cur:
            response = await cur.fetchall()
            
        return [
            ClassesScheme(id=row["id"], class_code=row["ds_class_code"]) 
            for row in response
        ]


@router.post("/course", response_model=PostCourseReturn, status_code=status.HTTP_201_CREATED, response_description="Retorna se a inserção foi um sucesso")
async def post_course(data: PostCourseRequest, user: dict = Depends(check_access)):
    """
    Adiciona um curso ao banco de Dados
    Informe o nome do Curso a ser inserido
    """

    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas administradores podem adicionar cursos."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        query = "INSERT INTO courses (nm_course) VALUES (?)"
        
        async with db.execute(query, (data.course_name,)) as cur:
            course_id = cur.lastrowid
            
        await db.commit()
        return PostCourseReturn(course_id=course_id)


@router.delete("/course/{id}", response_model=DeleteCourseReturn, status_code=status.HTTP_200_OK, response_description="Retorna se a deleção foi um sucesso")
async def delete_course(id: int, user: dict = Depends(check_access)):
    """
    Deleta um curso existente com base no ID
    """

    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas administradores podem deletar cursos."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        query = "DELETE FROM courses WHERE id = ?"
        
        async with db.execute(query, (id,)) as cur:
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Curso com ID {id} não foi encontrado."
                )
                
        await db.commit()
        return DeleteCourseReturn()


@router.post("/class", response_model=PostClassReturn, status_code=status.HTTP_201_CREATED, response_description="Retorna se a inserção foi um sucesso")
async def post_class(data: PostClassRequest, user: dict = Depends(check_access)):
    """
    Adiciona uma turma ao banco de Dados
    Informe a turma a ser inserida
    """

    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas administradores podem adicionar turmas."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        query = "INSERT INTO classes (ds_class_code) VALUES (?)"
        
        async with db.execute(query, (data.class_code,)) as cur:
            class_id = cur.lastrowid
            
        await db.commit()
        return PostClassReturn(class_id=class_id)


@router.delete("/class/{id}", response_model=DeleteClassReturn, status_code=status.HTTP_200_OK, response_description="Retorna se a deleção foi um sucesso")
async def delete_class(id: int, user: dict = Depends(check_access)):
    """
    Deleta uma turma existente com base no ID
    """

    if user.get("role") != "Administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado. Apenas administradores podem deletar turmas."
        )

    async with aiosqlite.connect(DB_PATH) as db:
        query = "DELETE FROM classes WHERE id = ?"
        
        async with db.execute(query, (id,)) as cur:
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail=f"Turma com ID {id} não foi encontrado."
                )
                
        await db.commit()
        return DeleteClassReturn()
