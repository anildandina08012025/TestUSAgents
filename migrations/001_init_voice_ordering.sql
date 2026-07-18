Exit code: 0
Wall time: 3.1 seconds
Output:
CREATE TABLE IF NOT EXISTS menu_items (
    product_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    product_name TEXT NOT NULL,
    description TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    vegetarian BOOLEAN NOT NULL DEFAULT TRUE,
    spice_level TEXT NOT NULL DEFAULT 'none',
    available BOOLEAN NOT NULL DEFAULT TRUE,
    sizes TEXT NOT NULL,
    base_price_inr NUMERIC(10, 2) NOT NULL,
    customization_options TEXT,
    allergens TEXT,
    recommended_upsell TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_menu_items_category ON menu_items (category);
CREATE INDEX IF NOT EXISTS idx_menu_items_available ON menu_items (available);
CREATE INDEX IF NOT EXISTS idx_menu_items_ingredients_search ON menu_items USING GIN (to_tsvector('english', ingredients));
CREATE INDEX IF NOT EXISTS idx_menu_items_name_description_search ON menu_items USING GIN (
    to_tsvector('english', product_name || ' ' || description)
);

CREATE TABLE IF NOT EXISTS voice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    livekit_room_name TEXT,
    customer_name TEXT,
    customer_phone TEXT,
    customer_email TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS carts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES voice_sessions(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cart_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cart_id UUID NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL REFERENCES menu_items(product_id),
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    selected_size TEXT,
    customizations TEXT,
    item_price_inr NUMERIC(10, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES voice_sessions(id),
    cart_id UUID NOT NULL REFERENCES carts(id),
    customer_name TEXT,
    customer_phone TEXT,
    order_status TEXT NOT NULL DEFAULT 'pending',
    subtotal_inr NUMERIC(10, 2) NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS voice_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES voice_sessions(id) ON DELETE CASCADE,
    speaker TEXT NOT NULL CHECK (speaker IN ('user', 'assistant', 'system')),
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

