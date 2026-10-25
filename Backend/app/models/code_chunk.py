from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text
from ..core.db import Base

class CodeChunk(Base):
    __tablename__ = "code_chunks"

    id = Column(Integer, primary_key=True, index=True)
    repo = Column(String, nullable=False, index=True)
    path = Column(String, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)
