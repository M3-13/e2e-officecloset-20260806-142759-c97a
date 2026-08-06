import io
import os

import pytest
from fastapi.testclient import TestClient

from database import get_db
from models import ClothingItem, User


@pytest.fixture(scope="module", autouse=True)
def _setup_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from database import Base
    from main import app

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session_class = sessionmaker(bind=engine)

    def _override_get_db():
        db = test_session_class()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield test_session_class
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def db_session(_setup_db):
    db = _setup_db()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def test_user(db_session):
    user = User(email="wardrobe-test@example.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.query(ClothingItem).filter(ClothingItem.user_id == user.id).delete()
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()


@pytest.fixture
def other_user(db_session):
    user = User(email="other@example.com", hashed_password="hashed")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    yield user
    db_session.query(ClothingItem).filter(ClothingItem.user_id == user.id).delete()
    db_session.query(User).filter(User.id == user.id).delete()
    db_session.commit()


@pytest.fixture(autouse=True)
def _override_auth(test_user):
    from auth import get_current_user
    from main import app

    def _get_test_user():
        return test_user

    app.dependency_overrides[get_current_user] = _get_test_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


def _fake_image(fmt="JPEG"):
    from PIL import Image

    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return io.BytesIO(buf.getvalue())


def test_create_item_with_image(auth_headers):
    from main import app

    with TestClient(app) as c:
        response = c.post(
            "/api/wardrobe",
            data={"name": "Rotes Kleid", "category": "Kleid"},
            files={"image": ("test.jpg", _fake_image(), "image/jpeg")},
            headers=auth_headers,
        )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Rotes Kleid"
    assert data["category"] == "Kleid"
    assert data["image_url"].startswith("/api/uploads/")
    assert data["id"] > 0
    assert data["created_at"]

    filename = data["image_url"].split("/")[-1]
    filepath = os.path.join("uploads", filename)
    if os.path.isfile(filepath):
        os.remove(filepath)


def test_list_items_returns_user_items(auth_headers, db_session, test_user):
    from main import app

    item = ClothingItem(
        user_id=test_user.id,
        name="Blaue Jeans",
        category="Hose",
        image_filename="jeans.jpg",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    with TestClient(app) as c:
        response = c.get("/api/wardrobe", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(i["name"] == "Blaue Jeans" for i in data)


def test_list_items_filter_by_category(auth_headers, db_session, test_user):
    from main import app

    item = ClothingItem(
        user_id=test_user.id,
        name="Schwarze Schuhe",
        category="Schuhe",
        image_filename="shoes.jpg",
    )
    db_session.add(item)
    db_session.commit()

    with TestClient(app) as c:
        response = c.get("/api/wardrobe?category=Schuhe", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    for i in data:
        assert i["category"] == "Schuhe"
    assert any(i["name"] == "Schwarze Schuhe" for i in data)


def test_list_items_filter_category_no_match(auth_headers, db_session, test_user):
    from main import app

    with TestClient(app) as c:
        response = c.get("/api/wardrobe?category=Accessoire", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_single_item_returns_200(auth_headers, db_session, test_user):
    from main import app

    item = ClothingItem(
        user_id=test_user.id,
        name="Weißes Hemd",
        category="Oberteil",
        image_filename="hemd.jpg",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    with TestClient(app) as c:
        response = c.get(f"/api/wardrobe/{item.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Weißes Hemd"
    assert data["id"] == item.id


def test_get_item_not_found_returns_404(auth_headers):
    from main import app

    with TestClient(app) as c:
        response = c.get("/api/wardrobe/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_foreign_item_returns_403(auth_headers, other_user, db_session):
    from main import app

    item = ClothingItem(
        user_id=other_user.id,
        name="Fremdes Item",
        category="Hose",
        image_filename="fremd.jpg",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    with TestClient(app) as c:
        response = c.get(f"/api/wardrobe/{item.id}", headers=auth_headers)
    assert response.status_code == 403


def test_delete_item_returns_204(auth_headers, db_session, test_user):
    from main import app

    item = ClothingItem(
        user_id=test_user.id,
        name="Zu löschendes Item",
        category="Accessoire",
        image_filename="delete.jpg",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    with TestClient(app) as c:
        response = c.delete(f"/api/wardrobe/{item.id}", headers=auth_headers)
    assert response.status_code == 204

    with TestClient(app) as c:
        response = c.get(f"/api/wardrobe/{item.id}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_foreign_item_returns_403(auth_headers, other_user, db_session):
    from main import app

    item = ClothingItem(
        user_id=other_user.id,
        name="Fremdes zu löschen",
        category="Hose",
        image_filename="fremd_del.jpg",
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    with TestClient(app) as c:
        response = c.delete(f"/api/wardrobe/{item.id}", headers=auth_headers)
    assert response.status_code == 403


def test_create_item_invalid_category_returns_422(auth_headers):
    from main import app

    with TestClient(app) as c:
        response = c.post(
            "/api/wardrobe",
            data={"name": "Test", "category": "Mantel"},
            files={"image": ("test.jpg", _fake_image(), "image/jpeg")},
            headers=auth_headers,
        )
    assert response.status_code == 422


def test_create_item_saves_image_file_on_disk(auth_headers, db_session, test_user):
    from main import app

    with TestClient(app) as c:
        response = c.post(
            "/api/wardrobe",
            data={"name": "Grüner Pullover", "category": "Oberteil"},
            files={"image": ("pullover.png", _fake_image(), "image/png")},
            headers=auth_headers,
        )
    assert response.status_code == 201
    data = response.json()
    filename = data["image_url"].split("/")[-1]
    filepath = os.path.join("uploads", filename)
    assert os.path.isfile(filepath)

    os.remove(filepath)


def test_create_item_missing_image_returns_422(auth_headers):
    from main import app

    with TestClient(app) as c:
        response = c.post(
            "/api/wardrobe",
            data={"name": "Test", "category": "Hose"},
            headers=auth_headers,
        )
    assert response.status_code == 422
