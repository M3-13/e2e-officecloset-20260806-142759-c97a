import io
import os
import tempfile

import pytest
from fastapi import HTTPException
from PIL import Image

from main import app


def create_test_image(fmt: str = "JPEG", with_exif: bool = False) -> bytes:
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    if not (with_exif and fmt in ("JPEG", "JPG")):
        return buf.getvalue()
    buf.seek(0)
    img2 = Image.open(buf)
    exif = img2.getexif()
    exif[0x010F] = "TestCamera"
    buf2 = io.BytesIO()
    img2.save(buf2, format="JPEG", exif=exif.tobytes())
    return buf2.getvalue()


def _mock_user():
    class MockUser:
        id = 1
        email = "test@example.com"

    return MockUser()


def _auth_ok(request, db):
    return _mock_user()


def _auth_unauthorized(request, db):
    raise HTTPException(status_code=401, detail="Not authenticated")


@pytest.fixture
def upload_dir(monkeypatch):
    tmpdir = tempfile.mkdtemp()
    monkeypatch.setattr("uploads.UPLOAD_DIR", tmpdir)
    yield tmpdir
    for f in os.listdir(tmpdir):
        os.remove(os.path.join(tmpdir, f))
    os.rmdir(tmpdir)


@pytest.fixture
def auth_client(upload_dir, monkeypatch):
    monkeypatch.setattr("uploads.get_current_user", _auth_ok)
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c


def test_upload_valid_jpeg(auth_client, upload_dir):
    jpeg_data = create_test_image("JPEG")
    response = auth_client.post(
        "/api/uploads",
        files={"file": ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")},
    )
    assert response.status_code == 201
    body = response.json()
    assert "filename" in body
    assert "url" in body
    assert body["filename"].endswith(".jpg")
    assert body["url"].startswith("/api/uploads/")
    assert os.path.isfile(os.path.join(upload_dir, body["filename"]))


def test_upload_valid_png(auth_client):
    png_data = create_test_image("PNG")
    response = auth_client.post(
        "/api/uploads",
        files={"file": ("test.png", io.BytesIO(png_data), "image/png")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"].endswith(".png")


def test_upload_valid_gif(auth_client):
    gif_data = create_test_image("GIF")
    response = auth_client.post(
        "/api/uploads",
        files={"file": ("test.gif", io.BytesIO(gif_data), "image/gif")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"].endswith(".gif")


def test_gif_pixels_preserved_after_upload(auth_client):
    gif_data = create_test_image("GIF")
    upload_resp = auth_client.post(
        "/api/uploads",
        files={"file": ("test.gif", io.BytesIO(gif_data), "image/gif")},
    )
    filename = upload_resp.json()["filename"]
    get_resp = auth_client.get(f"/api/uploads/{filename}")
    assert get_resp.status_code == 200

    img = Image.open(io.BytesIO(get_resp.content))
    pixels = list(img.getdata())
    assert any(p != (0, 0, 0) for p in pixels), "GIF must contain non-black pixels"


def test_upload_valid_webp(auth_client):
    webp_data = create_test_image("WEBP")
    response = auth_client.post(
        "/api/uploads",
        files={"file": ("test.webp", io.BytesIO(webp_data), "image/webp")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"].endswith(".webp")


def test_upload_invalid_file(auth_client):
    invalid_data = b"This is not an image"
    response = auth_client.post(
        "/api/uploads",
        files={"file": ("fake.jpg", io.BytesIO(invalid_data), "image/jpeg")},
    )
    assert response.status_code == 400


def test_upload_without_authentication(client, monkeypatch):
    monkeypatch.setattr("uploads.get_current_user", _auth_unauthorized)
    jpeg_data = create_test_image("JPEG")
    response = client.post(
        "/api/uploads",
        files={"file": ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")},
    )
    assert response.status_code == 401


def test_serve_uploaded_file(auth_client):
    jpeg_data = create_test_image("JPEG")
    upload_resp = auth_client.post(
        "/api/uploads",
        files={"file": ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")},
    )
    filename = upload_resp.json()["filename"]

    response = auth_client.get(f"/api/uploads/{filename}")
    assert response.status_code == 200
    assert response.headers.get("x-content-type-options") == "nosniff"


def test_serve_uploaded_file_content_type_png(auth_client):
    png_data = create_test_image("PNG")
    upload_resp = auth_client.post(
        "/api/uploads",
        files={"file": ("test.png", io.BytesIO(png_data), "image/png")},
    )
    filename = upload_resp.json()["filename"]

    response = auth_client.get(f"/api/uploads/{filename}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.headers.get("x-content-type-options") == "nosniff"


def test_serve_uploaded_file_content_type_jpeg(auth_client):
    jpeg_data = create_test_image("JPEG")
    upload_resp = auth_client.post(
        "/api/uploads",
        files={"file": ("test.jpg", io.BytesIO(jpeg_data), "image/jpeg")},
    )
    filename = upload_resp.json()["filename"]

    response = auth_client.get(f"/api/uploads/{filename}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"


def test_serve_nonexistent_file(auth_client):
    response = auth_client.get("/api/uploads/nonexistent_12345.jpg")
    assert response.status_code == 404


def test_magic_byte_check_manipulated_extension(auth_client):
    png_data = create_test_image("PNG")
    response = auth_client.post(
        "/api/uploads",
        files={"file": ("fake.jpg", io.BytesIO(png_data), "image/png")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"].endswith(".jpg")

    get_resp = auth_client.get(f"/api/uploads/{body['filename']}")
    assert get_resp.status_code == 200
    assert get_resp.headers["content-type"] == "image/png"


def test_exif_stripped_from_upload(auth_client):
    jpeg_with_exif = create_test_image("JPEG", with_exif=True)
    upload_resp = auth_client.post(
        "/api/uploads",
        files={"file": ("test.jpg", io.BytesIO(jpeg_with_exif), "image/jpeg")},
    )
    filename = upload_resp.json()["filename"]

    get_resp = auth_client.get(f"/api/uploads/{filename}")
    assert get_resp.status_code == 200

    saved_img = Image.open(io.BytesIO(get_resp.content))
    exif = saved_img.getexif()
    assert exif.get(0x010F) is None, "EXIF Make tag should be stripped"


def test_strip_exif_removes_metadata(upload_dir):
    from uploads import strip_exif

    jpeg_with_exif = create_test_image("JPEG", with_exif=True)
    original = Image.open(io.BytesIO(jpeg_with_exif))
    assert original.getexif().get(0x010F) is not None, "test image must contain EXIF"

    cleaned = io.BytesIO(strip_exif(jpeg_with_exif))
    result = Image.open(cleaned)
    result_exif = result.getexif()
    assert result_exif.get(0x010F) is None, "EXIF should be removed by strip_exif"


def test_path_traversal_rejected(auth_client):
    response = auth_client.get("/api/uploads/..%2F..%2Fetc%2Fpasswd")
    assert response.status_code == 404


def test_save_upload_utility(monkeypatch, upload_dir):
    monkeypatch.setattr("uploads.get_current_user", _auth_ok)

    async def _run():
        from uploads import save_upload

        class FakeFile:
            filename = "photo.jpg"

            async def read(self):
                return create_test_image("JPEG")

        stored = await save_upload(FakeFile(), "photo.jpg")
        return stored

    import asyncio

    stored = asyncio.run(_run())
    assert stored.endswith(".jpg")
    assert os.path.isfile(os.path.join(upload_dir, stored))
