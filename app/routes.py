import sqlite3
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from .database import get_db

bp = Blueprint("inventory", __name__)


def _parse_product_form():
    sku = request.form.get("sku", "").strip().upper()
    name = request.form.get("name", "").strip()

    try:
        price = float(request.form.get("price", ""))
        quantity = int(request.form.get("quantity", ""))
    except (TypeError, ValueError):
        raise ValueError("Az árnak számnak, a mennyiségnek egész számnak kell lennie.")

    if not sku or not name:
        raise ValueError("A cikkszám és a terméknév megadása kötelező.")
    if price < 0:
        raise ValueError("Az ár nem lehet negatív.")
    if quantity < 0:
        raise ValueError("A készlet nem lehet negatív.")

    return sku, name, price, quantity


@bp.get("/")
def index():
    products = get_db().execute(
        "SELECT * FROM products ORDER BY name COLLATE NOCASE"
    ).fetchall()
    low_stock_count = sum(1 for product in products if product["quantity"] < 5)
    return render_template(
        "index.html",
        products=products,
        low_stock_count=low_stock_count,
    )


@bp.post("/products")
def add_product():
    try:
        sku, name, price, quantity = _parse_product_form()
        db = get_db()
        db.execute(
            "INSERT INTO products (sku, name, price, quantity) VALUES (?, ?, ?, ?)",
            (sku, name, price, quantity),
        )
        db.commit()
        flash(f"'{name}' termék sikeresen hozzáadva.", "success")
    except ValueError as error:
        flash(str(error), "error")
    except sqlite3.IntegrityError:
        flash("Ez a cikkszám már létezik.", "error")

    return redirect(url_for("inventory.index"))


@bp.post("/products/<int:product_id>/stock")
def update_stock(product_id):
    try:
        change = int(request.form.get("change", ""))
    except ValueError:
        flash("A készletváltozásnak egész számnak kell lennie.", "error")
        return redirect(url_for("inventory.index"))

    db = get_db()
    product = db.execute(
        "SELECT * FROM products WHERE id = ?", (product_id,)
    ).fetchone()

    if product is None:
        flash("A keresett termék nem található.", "error")
        return redirect(url_for("inventory.index"))

    new_quantity = product["quantity"] + change
    if new_quantity < 0:
        flash("A művelet nem hajtható végre: a készlet nem lehet negatív.", "error")
    else:
        db.execute(
            "UPDATE products SET quantity = ? WHERE id = ?",
            (new_quantity, product_id),
        )
        db.commit()
        flash("A készlet sikeresen módosítva.", "success")

    return redirect(url_for("inventory.index"))


@bp.post("/products/<int:product_id>/delete")
def delete_product(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    flash("A termék törlése megtörtént.", "success")
    return redirect(url_for("inventory.index"))


@bp.get("/health")
def health():
    # Used later by the CI/CD deployment health check.
    get_db().execute("SELECT 1").fetchone()
    return {"status": "ok"}, 200
