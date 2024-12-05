from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.config import environ

from models.base import Model

host = environ.get("POSTGRES_DB", "127.0.0.1")
port = int(environ.get("POSTGRES_PORT", 5432))
user = environ.get("POSTGRES_USER", "postgres")
password = environ.get("POSTGRES_PASSWORD", "postgres")
db = environ.get("POSTGRES_DB", "postgres")

# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"


engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

#Model.metadata.create_all(engine)
