Exit code: 0
Wall time: 3.1 seconds
Output:
import json
import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions, function_tool
from livekit.plugins import deepgram, openai, silero

import internet_ordering_db as db

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("internet-ordering-agent")


SYSTEM_PROMPT = """
You are a fast, friendly voice ordering assistant for an online restaurant.

Your job is to help the customer choose food, customize it, build a cart, and confirm the order.

Rules:
- Keep voice replies short: usually 1-2 sentences.
- Use tools for menu search, cart changes, cart summary, and order confirmation.
- If the user asks for an ingredient, search the menu by that ingredient.
- If multiple matching products exist, mention up to 4 clear options with prices.
- Before adding to cart, confirm ambiguous choices like size, quantity, or which product.
- Do not invent menu items, prices, ingredients, offers, or availability.
- Before confirming an order, summarize cart items and total.
- Ask for name and phone only when the user is ready to place the order.
- If the customer asks for allergens, answer only from menu data.
"""


class OrderingTools:
    def __init__(self, session_id: str, cart_id: str):
        self.session_id = session_id
        self.cart_id = cart_id

    @function_tool
    async def search_menu(
        self,
        query: Annotated[str, "Food, category, product name, or general search text"] = "",
        ingredient: Annotated[str, "Specific ingredient the customer asked for, such as mushroom"] = "",
        category: Annotated[str, "Optional category such as Burger, Pizza, Pasta, Beverage"] = "",
    ) -> str:
        """Search available menu items."""
        items = db.search_menu(query=query, ingredient=ingredient, category=category)
        if not items:
            return "No matching menu items found."
        return json.dumps(items, ensure_ascii=False)

    @function_tool
    async def add_to_cart(
        self,
        product_id: Annotated[str, "Exact product_id from search_menu, such as P002"],
        quantity: Annotated[int, "Quantity to add"] = 1,
        selected_size: Annotated[str, "Selected size, such as regular, medium, large, or combo"] = "",
        customizations: Annotated[str, "Customer customizations, such as extra cheese or no onion"] = "",
    ) -> str:
        """Add a selected menu item to the current cart."""
        item = db.add_to_cart(
            self.cart_id,
            product_id=product_id,
            quantity=quantity,
            selected_size=selected_size,
            customizations=customizations,
        )
        return json.dumps(item, ensure_ascii=False)

    @function_tool
    async def get_cart(self) -> str:
        """Get the current cart items and subtotal."""
        return json.dumps(db.get_cart(self.cart_id), ensure_ascii=False)

    @function_tool
    async def confirm_order(
        self,
        customer_name: Annotated[str, "Customer name"],
        customer_phone: Annotated[str, "Customer phone number"],
        notes: Annotated[str, "Any final customer notes"] = "",
    ) -> str:
        """Confirm and create the final order."""
        order = db.confirm_order(
            self.session_id,
            self.cart_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            notes=notes,
        )
        return json.dumps(order, ensure_ascii=False)


class InternetOrderingAgent(Agent):
    def __init__(self, tools: OrderingTools):
        super().__init__(
            instructions=SYSTEM_PROMPT,
            tools=[tools.search_menu, tools.add_to_cart, tools.get_cart, tools.confirm_order],
        )


async def entrypoint(ctx: agents.JobContext):
    room_name = ctx.room.name
    session_record = db.create_voice_session(room_name)
    logger.info("Started voice ordering session %s in room %s", session_record["id"], room_name)

    tools = OrderingTools(
        session_id=str(session_record["id"]),
        cart_id=str(session_record["cart_id"]),
    )

    session = AgentSession(
        stt=deepgram.STT(
            model=os.getenv("DEEPGRAM_STT_MODEL", "nova-3"),
            language=os.getenv("DEEPGRAM_STT_LANGUAGE", "en-US"),
            smart_format=True,
            api_key=os.getenv("DEEPGRAM_API_KEY"),
        ),
        llm=openai.LLM(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.2,
        ),
        tts=deepgram.TTS(
            model=os.getenv("DEEPGRAM_TTS_MODEL", "aura-2-andromeda-en"),
            api_key=os.getenv("DEEPGRAM_API_KEY"),
        ),
        vad=silero.VAD.load(min_silence_duration=0.35, min_speech_duration=0.1),
    )

    @session.on("user_input_transcribed")
    def on_user_input(event):
        if getattr(event, "is_final", False) and getattr(event, "transcript", ""):
            db.log_transcript(str(session_record["id"]), "user", event.transcript)

    @session.on("conversation_item_added")
    def on_conversation_item(event):
        item = getattr(event, "item", None)
        role = getattr(item, "role", "") if item else ""
        text_content = getattr(item, "text_content", "") if item else ""
        if role in {"assistant", "system"} and text_content:
            db.log_transcript(str(session_record["id"]), role, text_content)

    await session.start(
        room=ctx.room,
        agent=InternetOrderingAgent(tools),
        room_input_options=RoomInputOptions(close_on_disconnect=True),
    )

    await session.generate_reply(
        instructions=(
            "Greet the customer and say you can help them order from the menu. "
            "Mention they can ask by item or ingredient, for example mushroom."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="internet-ordering-agent",
            load_threshold=9.99,
            num_idle_processes=1,
            port=8083,
        )
    )


