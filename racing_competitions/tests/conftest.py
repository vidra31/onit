import os
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app

@pytest.fixture
def client():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(conn, record):
        conn.execute("PRAGMA foreign_keys=ON")
    # SQLite in-memory test schema is isolated and never used for production.
    # Production PostgreSQL schema is created exclusively via Alembic migrations.
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    def override_db():
        with Session() as db:
            yield db
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()
