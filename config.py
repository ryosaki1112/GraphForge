MODEL = "qwen3:8b"  # Consider "phi3" for faster inference (20s vs 30-60s per call)
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_GROUP_SIZE = 3
FILE_KEYS = [
    "main.py",
    "schemas.py",
    "routes/task.py",
    "tests/test_main.py",
    "openapi.json",
    ".github/workflows/test.yml",
    "frontend/src/App.jsx",
    "frontend/src/pages/Home.jsx",
    "frontend/src/components/TaskCard.jsx",
    "frontend/package.json",
    "frontend/vite.config.js",
    "frontend/index.html",
]

DOCKER_COMPOSE_TEMPLATE = """
version: '3.8'
services:
  db:
    image: {db_image}
    environment:
      POSTGRES_USER: {db_user}
      POSTGRES_PASSWORD: {db_password}
      POSTGRES_DB: {db_name}
    ports:
      - "{db_port}:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  db_data:
"""

MODELS_PROMPT_TEMPLATE = """
Generate a Python file `models.py` using SQLAlchemy 1.4 declarative base for the following schema:
{schema}
Requirements:
- Import `sqlalchemy`, `sqlalchemy.ext.declarative.declarative_base`, `sqlalchemy.orm`.
- Define a `Base` class with `declarative_base()`.
- Use CamelCase for class names, snake_case for column names.
- Include `__tablename__` matching table name for each class.
- Use appropriate SQLAlchemy types (e.g., Integer, String, ForeignKey).
- Define relationships with `back_populates` for foreign keys.
- Return only the Python code, no explanations, markdown, or backticks.
Example:
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    tasks = relationship("Task", back_populates="user")
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")
"""

DATABASE_PROMPT_TEMPLATE = """
Generate a Python file `database.py` for {db_type}:
Requirements:
- Import `os`, `sqlalchemy`, `sqlalchemy.orm`.
- Create an engine with `create_engine` using `DATABASE_URL` from environment.
- Configure `SessionLocal` with `sessionmaker` (autocommit=False, autoflush=False).
- Return only the Python code, no explanations, markdown, or backticks.
Example:
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///appdb.sqlite")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""