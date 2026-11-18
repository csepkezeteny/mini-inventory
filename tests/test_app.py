
import pytest

from app import create_app
from app.database import get_db


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test_inventory.sqlite"

    app = create_app({
        "TESTING": True,
        "DATABASE": str(db_path),
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def add_test_product(client, sku="TEST-001", quantity=10):
    """Segédfüggvény teszttermék létrehozásához."""
    return client.post(
        "/products",
        data={
            "sku": sku,
            "name": "Teszt termék",
            "price": "1500",
            "quantity": str(quantity),
        },
        follow_redirects=True,
    )


def get_product_id(app, sku):
    """Termék adatbázis-azonosítójának lekérdezése."""
    with app.app_context():
        product = get_db().execute(
            "SELECT id FROM products WHERE sku = ?",
            (sku,),
        ).fetchone()

        return product["id"]


def test_homepage(client):
    response = client.get("/")

    assert response.status_code == 200


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_add_product(client):
    response = add_test_product(client)

    assert response.status_code == 200
    assert b"TEST-001" in response.data


def test_duplicate_sku(client, app):
    add_test_product(client, sku="TEST-002")

    response = client.post(
        "/products",
        data={
            "sku": "TEST-002",
            "name": "Masik termek",
            "price": "2000",
            "quantity": "5",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "Ez a cikkszám már létezik.".encode("utf-8") in response.data

    with app.app_context():
        products = get_db().execute(
            "SELECT * FROM products WHERE sku = ?",
            ("TEST-002",),
        ).fetchall()

    assert len(products) == 1


def test_product_list(client):
    add_test_product(client, sku="TEST-003")

    response = client.get("/")

    assert response.status_code == 200
    assert "Teszt termék".encode("utf-8") in response.data
    assert b"TEST-003" in response.data


def test_increase_stock(client, app):
    add_test_product(client, sku="TEST-004", quantity=10)
    product_id = get_product_id(app, "TEST-004")

    response = client.post(
        f"/products/{product_id}/stock",
        data={"change": "5"},
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        product = get_db().execute(
            "SELECT quantity FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()

    assert product["quantity"] == 15


def test_decrease_stock(client, app):
    add_test_product(client, sku="TEST-005", quantity=10)
    product_id = get_product_id(app, "TEST-005")

    response = client.post(
        f"/products/{product_id}/stock",
        data={"change": "-3"},
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        product = get_db().execute(
            "SELECT quantity FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()

    assert product["quantity"] == 7


def test_negative_stock_is_rejected(client, app):
    add_test_product(client, sku="TEST-006", quantity=2)
    product_id = get_product_id(app, "TEST-006")

    response = client.post(
        f"/products/{product_id}/stock",
        data={"change": "-5"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "A művelet nem hajtható végre: a készlet nem lehet negatív.".encode("utf-8") in response.data

    with app.app_context():
        product = get_db().execute(
            "SELECT quantity FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()

    assert product["quantity"] == 2


def test_low_stock_warning(client):
    add_test_product(client, sku="TEST-007", quantity=3)

    response = client.get("/")

    assert response.status_code == 200
    assert "1 alacsony készletű".encode("utf-8") in response.data


def test_delete_product(client, app):
    add_test_product(client, sku="TEST-008")
    product_id = get_product_id(app, "TEST-008")

    response = client.post(
        f"/products/{product_id}/delete",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        product = get_db().execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,),
        ).fetchone()

    assert product is None
