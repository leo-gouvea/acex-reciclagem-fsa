from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field, BeforeValidator, PlainSerializer

# Cria um tipo reutilizável para o projeto inteiro
def parse_sqlite_datetime(v: any) -> datetime:
    if isinstance(v, str):
        try:
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("A data deve estar no formato exato 'AAAA-MM-DD HH:MM:SS'")
    if isinstance(v, datetime):
        return v
    raise ValueError("Tipo de dado inválido para data")

# Este tipo garante: valida a string limpa na entrada e converte para string limpa na saída
SQLiteDateTime = Annotated[
    datetime,
    BeforeValidator(parse_sqlite_datetime),
    PlainSerializer(lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S"), return_type=str)
]
