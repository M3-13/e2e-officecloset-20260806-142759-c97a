import pytest

from database import SessionLocal
from models import ClothingItem, Outfit, OutfitItem, User


class _TestUser:
    def __init__(self, id: int, email: str = "test@local"):
        self.id = id
        self.email = email


def _make_mock_auth(user_id: int):
    def mock_auth(request, db):
        return _TestUser(user_id)

    return mock_auth


@pytest.fixture
def own_user(client, monkeypatch):
    db = SessionLocal()
    user = User(email="outfits_own@test.local", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    monkeypatch.setattr("outfits._auth_get_current_user", _make_mock_auth(user.id))

    yield user

    db = SessionLocal()
    db.query(OutfitItem).delete()
    db.query(Outfit).delete()
    db.query(ClothingItem).filter(ClothingItem.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()
    db.close()


@pytest.fixture
def foreign_user(client):
    db = SessionLocal()
    user = User(email="outfits_foreign@test.local", hashed_password="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    yield user

    db = SessionLocal()
    db.query(OutfitItem).delete()
    db.query(Outfit).delete()
    db.query(ClothingItem).filter(ClothingItem.user_id == user.id).delete()
    db.query(User).filter(User.id == user.id).delete()
    db.commit()
    db.close()


def _create_item(user_id: int, name: str, category: str, filename: str) -> ClothingItem:
    db = SessionLocal()
    item = ClothingItem(user_id=user_id, name=name, category=category, image_filename=filename)
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()
    return item


class TestCreateOutfit:
    def test_create_outfit_success(self, client, own_user):
        item1 = _create_item(own_user.id, "Shirt", "Tops", "shirt.jpg")
        item2 = _create_item(own_user.id, "Jeans", "Bottoms", "jeans.jpg")

        response = client.post(
            "/api/outfits",
            json={"name": "Casual", "item_ids": [item1.id, item2.id]},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Casual"
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "Shirt"
        assert data["items"][1]["name"] == "Jeans"
        assert "created_at" in data

    def test_create_outfit_empty_items(self, client, own_user):
        response = client.post(
            "/api/outfits",
            json={"name": "Empty", "item_ids": []},
        )
        assert response.status_code == 400

    def test_create_outfit_nonexistent_item(self, client, own_user):
        response = client.post(
            "/api/outfits",
            json={"name": "Ghost", "item_ids": [99999]},
        )
        assert response.status_code == 404

    def test_create_outfit_foreign_item_returns_403(self, client, own_user, foreign_user):
        own_item = _create_item(own_user.id, "My Shirt", "Tops", "mine.jpg")
        foreign_item = _create_item(foreign_user.id, "Their Shirt", "Tops", "theirs.jpg")

        response = client.post(
            "/api/outfits",
            json={"name": "Stolen", "item_ids": [own_item.id, foreign_item.id]},
        )
        assert response.status_code == 403


class TestListOutfits:
    def test_list_outfits_empty(self, client, own_user):
        response = client.get("/api/outfits")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_outfits_with_data(self, client, own_user):
        item = _create_item(own_user.id, "Hat", "Accessories", "hat.jpg")
        client.post(
            "/api/outfits",
            json={"name": "Summer", "item_ids": [item.id]},
        )

        response = client.get("/api/outfits")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Summer"
        assert len(data[0]["items"]) == 1
        assert data[0]["items"][0]["name"] == "Hat"
        assert data[0]["items"][0]["image_url"] == "/api/uploads/hat.jpg"

    def test_list_outfits_only_own(self, client, own_user, foreign_user):
        own_item = _create_item(own_user.id, "My Hat", "Accessories", "my_hat.jpg")
        client.post(
            "/api/outfits",
            json={"name": "My Outfit", "item_ids": [own_item.id]},
        )

        foreign_item = _create_item(foreign_user.id, "Their Hat", "Accessories", "their_hat.jpg")
        fb = SessionLocal()
        foreign_outfit = Outfit(user_id=foreign_user.id, name="Their Outfit")
        fb.add(foreign_outfit)
        fb.flush()
        fb.add(OutfitItem(outfit_id=foreign_outfit.id, clothing_item_id=foreign_item.id))
        fb.commit()
        foreign_outfit_id = foreign_outfit.id
        fb.close()

        response = client.get("/api/outfits")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "My Outfit"

        fb = SessionLocal()
        fb.query(OutfitItem).filter(OutfitItem.outfit_id == foreign_outfit_id).delete()
        fb.query(Outfit).filter(Outfit.id == foreign_outfit_id).delete()
        fb.commit()
        fb.close()


class TestDeleteOutfit:
    def test_delete_outfit_success(self, client, own_user):
        item = _create_item(own_user.id, "Shoes", "Footwear", "shoes.jpg")
        create_resp = client.post(
            "/api/outfits",
            json={"name": "DeleteMe", "item_ids": [item.id]},
        )
        outfit_id = create_resp.json()["id"]

        response = client.delete(f"/api/outfits/{outfit_id}")
        assert response.status_code == 204

        list_resp = client.get("/api/outfits")
        assert list_resp.json() == []

    def test_delete_outfit_not_found(self, client, own_user):
        response = client.delete("/api/outfits/99999")
        assert response.status_code == 404

    def test_delete_outfit_not_own(self, client, own_user, foreign_user):
        foreign_item = _create_item(foreign_user.id, "Their Shoes", "Footwear", "ts.jpg")
        db = SessionLocal()
        foreign_outfit = Outfit(user_id=foreign_user.id, name="Theirs")
        db.add(foreign_outfit)
        db.flush()
        db.add(OutfitItem(outfit_id=foreign_outfit.id, clothing_item_id=foreign_item.id))
        db.commit()
        outfit_id = foreign_outfit.id
        db.close()

        response = client.delete(f"/api/outfits/{outfit_id}")
        assert response.status_code == 403

        db = SessionLocal()
        db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit_id).delete()
        db.query(Outfit).filter(Outfit.id == outfit_id).delete()
        db.commit()
        db.close()

    def test_delete_outfit_cascades_items(self, client, own_user):
        item = _create_item(own_user.id, "Watch", "Accessories", "watch.jpg")
        create_resp = client.post(
            "/api/outfits",
            json={"name": "CasualDelete", "item_ids": [item.id]},
        )
        outfit_id = create_resp.json()["id"]

        client.delete(f"/api/outfits/{outfit_id}")

        db = SessionLocal()
        remaining_items = db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit_id).count()
        db.close()
        assert remaining_items == 0
