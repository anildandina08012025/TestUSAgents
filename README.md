Exit code: 0
Wall time: 3.1 seconds
Output:
# Internet Voice Ordering Agent

This is the local browser-based voice ordering demo.

## Stack

- Self-hosted LiveKit on Docker
- Redis on Docker
- Postgres on Docker
- Deepgram STT/TTS
- Groq LLM through the OpenAI-compatible LiveKit plugin
- Flask test web app

## Required `.env`

```env
LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
DEEPGRAM_API_KEY=your_deepgram_key
GROQ_API_KEY=your_groq_key
DATABASE_URL=postgresql://voice_agent_user:voice_agent_pass@localhost:55432/voice_agent
```

## Start Local Services

```powershell
docker compose up -d postgres redis livekit-server
```

## Apply Schema And Load Menu

```powershell
docker cp migrations/001_init_voice_ordering.sql internet-voice-agent-postgres:/tmp/001_init_voice_ordering.sql
docker cp dummy_menu.csv internet-voice-agent-postgres:/tmp/dummy_menu.csv
docker exec internet-voice-agent-postgres psql -U voice_agent_user -d voice_agent -f /tmp/001_init_voice_ordering.sql
docker exec internet-voice-agent-postgres psql -U voice_agent_user -d voice_agent -c "TRUNCATE menu_items CASCADE; COPY menu_items(product_id, category, product_name, description, ingredients, vegetarian, spice_level, available, sizes, base_price_inr, customization_options, allergens, recommended_upsell) FROM '/tmp/dummy_menu.csv' WITH (FORMAT csv, HEADER true);"
```

## Start Agent

```powershell
.\start_internet_ordering_agent.ps1
```

## Start Web App

Open another terminal:

```powershell
.\start_internet_ordering_web.ps1
```

Then open:

```text
http://127.0.0.1:8091
```

Try saying:

- "What mushroom items do you have?"
- "Add one Mushroom Swiss Burger with extra cheese."
- "What is in my cart?"
- "Confirm the order. My name is Anil and my phone is 9999999999."

