import asyncio
import os
import time
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory
from livekit import api

import internet_ordering_db as db

load_dotenv()

app = Flask(__name__, static_folder="web")


def _livekit_http_url() -> str:
    url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    return url.replace("ws://", "http://").replace("wss://", "https://")


async def _dispatch_agent(room_name: str) -> None:
    lk = api.LiveKitAPI(
        url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
        api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
        api_secret=os.getenv("LIVEKIT_API_SECRET", "secret"),
    )
    try:
        await lk.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="internet-ordering-agent",
                room=room_name,
                metadata="{}",
            )
        )
    finally:
        await lk.aclose()


@app.get("/")
def index():
    return send_from_directory("web", "internet_ordering.html")


@app.get("/api/livekit-token")
def livekit_token():
    room_name = f"web-order-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    identity = f"customer-{uuid.uuid4().hex[:8]}"
    token = (
        api.AccessToken(
            os.getenv("LIVEKIT_API_KEY", "devkey"),
            os.getenv("LIVEKIT_API_SECRET", "secret"),
        )
        .with_identity(identity)
        .with_name("Website Customer")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )
    asyncio.run(_dispatch_agent(room_name))
    return jsonify(
        {
            "url": os.getenv("LIVEKIT_PUBLIC_URL") or os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            "http_url": _livekit_http_url(),
            "token": token,
            "room": room_name,
            "identity": identity,
        }
    )


@app.get("/api/menu")
def menu():
    return jsonify(db.search_menu())


@app.get("/api/orders/recent")
def recent_orders():
    with db._conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, customer_name, customer_phone, order_status, subtotal_inr, created_at
                FROM orders
                ORDER BY created_at DESC
                LIMIT 20
                """
            )
            orders = []
            for row in cur.fetchall():
                order = dict(row)
                order["id"] = str(order["id"])
                order["subtotal_inr"] = float(order["subtotal_inr"])
                order["created_at"] = order["created_at"].isoformat()
                orders.append(order)
            return jsonify(orders)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # Render supplies PORT and requires a public web service to bind to 0.0.0.0.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8091")), debug=False)

