import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from db.database import get_db, Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with test database"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI response for story generation"""
    return {
        "title": "Test Adventure",
        "rootNode": {
            "content": "You find yourself in a mysterious forest.",
            "isEnding": False,
            "isWinningEnding": False,
            "options": [
                {
                    "text": "Go left",
                    "nextNode": {
                        "content": "You found treasure!",
                        "isEnding": True,
                        "isWinningEnding": True,
                        "options": []
                    }
                },
                {
                    "text": "Go right", 
                    "nextNode": {
                        "content": "You fell into a trap.",
                        "isEnding": True,
                        "isWinningEnding": False,
                        "options": []
                    }
                }
            ]
        }
    }