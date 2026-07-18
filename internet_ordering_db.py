Exit code: 0
Wall time: 3.1 seconds
Output:
import os
from decimal import Decimal
from typing import Any

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://voice_agent_user:voice_agent_pass@localhost:5432/voice_agent",
)


def _conn():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def _money(value: Any) -> float:
    if isinstance(value, Decimal):
        return float(value)
    return float(value or 0)


def create_voice_session(room_name: str) -> dict[str, Any]:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO voice_sessions (livekit_room_name)
                VALUES (%s)
                RETURNING id, livekit_room_name, status
                """,
                (room_name,),
            )
            session = dict(cur.fetchone())
            cur.execute(
                """
                INSERT INTO carts (session_id)
                VALUES (%s)
                RETURNING id, status
                """,
                (session["id"],),
            )
            cart = dict(cur.fetchone())
            session["cart_id"] = cart["id"]
            conn.commit()
            return session


def search_menu(query: str = "", ingredient: str = "", category: str = "") -> list[dict[str, Any]]:
    query_text = f"{query or ''} {ingredient or ''}".strip()
    params: list[Any] = []
    filters = ["available = TRUE"]

    if query_text:
        filters.append(
            """
            (
                product_name ILIKE %s
                OR description ILIKE %s
                OR ingredients ILIKE %s
                OR category ILIKE %s
            )
            """
        )
        like = f"%{query_text}%"
        params.extend([like, like, like, like])

    if category:
        filters.append("category ILIKE %s")
        params.append(f"%{category}%")

    sql = f"""
        SELECT product_id, category, product_name, description, ingredients,
               vegetarian, spice_level, sizes, base_price_inr,
               customization_options, allergens, recommended_upsell
        FROM menu_items
        WHERE {' AND '.join(filters)}
        ORDER BY base_price_inr, product_name
        LIMIT 8
    """

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]
            for row in rows:
                row["base_price_inr"] = _money(row["base_price_inr"])
            return rows


def add_to_cart(
    cart_id: str,
    product_id: str,
    quantity: int = 1,
    selected_size: str = "",
    customizations: str = "",
) -> dict[str, Any]:
    quantity = max(1, int(quantity or 1))
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT product_id, product_name, base_price_inr, sizes
                FROM menu_items
                WHERE product_id = %s AND available = TRUE
                """,
                (product_id,),
            )
            item = cur.fetchone()
            if not item:
                raise ValueError(f"Product {product_id} is not available.")

            price = _money(item["base_price_inr"])
            cur.execute(
                """
                INSERT INTO cart_items
                    (cart_id, product_id, quantity, selected_size, customizations, item_price_inr)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (cart_id, product_id, quantity, selected_size or None, customizations or None, price),
            )
            cart_item_id = cur.fetchone()["id"]
            cur.execute("UPDATE carts SET updated_at = NOW() WHERE id = %s", (cart_id,))
            conn.commit()
            return {
                "cart_item_id": str(cart_item_id),
                "product_id": product_id,
                "product_name": item["product_name"],
                "quantity": quantity,
                "selected_size": selected_size,
                "customizations": customizations,
                "line_total_inr": round(price * quantity, 2),
            }


def get_cart(cart_id: str) -> dict[str, Any]:
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT ci.id, ci.product_id, mi.product_name, ci.quantity,
                       ci.selected_size, ci.customizations, ci.item_price_inr
                FROM cart_items ci
                JOIN menu_items mi ON mi.product_id = ci.product_id
                WHERE ci.cart_id = %s
                ORDER BY ci.created_at
                """,
                (cart_id,),
            )
            items = []
            subtotal = 0.0
            for row in cur.fetchall():
                row = dict(row)
                price = _money(row["item_price_inr"])
                line_total = round(price * row["quantity"], 2)
                subtotal += line_total
                items.append(
                    {
                        "cart_item_id": str(row["id"]),
                        "product_id": row["product_id"],
                        "product_name": row["product_name"],
                        "quantity": row["quantity"],
                        "selected_size": row["selected_size"],
                        "customizations": row["customizations"],
                        "item_price_inr": price,
                        "line_total_inr": line_total,
                    }
                )
            return {"items": items, "subtotal_inr": round(subtotal, 2)}


def confirm_order(
    session_id: str,
    cart_id: str,
    customer_name: str = "",
    customer_phone: str = "",
    notes: str = "",
) -> dict[str, Any]:
    cart = get_cart(cart_id)
    if not cart["items"]:
        raise ValueError("Cart is empty.")

    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders
                    (session_id, cart_id, customer_name, customer_phone, subtotal_inr, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, order_status, subtotal_inr, created_at
                """,
                (
                    session_id,
                    cart_id,
                    customer_name or None,
                    customer_phone or None,
                    cart["subtotal_inr"],
                    notes or None,
                ),
            )
            order = dict(cur.fetchone())
            cur.execute("UPDATE carts SET status = 'ordered', updated_at = NOW() WHERE id = %s", (cart_id,))
            cur.execute("UPDATE voice_sessions SET status = 'ordered' WHERE id = %s", (session_id,))
            conn.commit()
            return {
                "order_id": str(order["id"]),
                "order_status": order["order_status"],
                "subtotal_inr": _money(order["subtotal_inr"]),
                "items": cart["items"],
            }


def log_transcript(session_id: str, speaker: str, text: str) -> None:
    if not text:
        return
    with _conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO voice_transcripts (session_id, speaker, text)
                VALUES (%s, %s, %s)
                """,
                (session_id, speaker, text[:4000]),
            )
            conn.commit()


