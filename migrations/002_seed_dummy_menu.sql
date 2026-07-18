Exit code: 0
Wall time: 3.3 seconds
Output:
TRUNCATE menu_items CASCADE;

INSERT INTO menu_items (
    product_id,
    category,
    product_name,
    description,
    ingredients,
    vegetarian,
    spice_level,
    available,
    sizes,
    base_price_inr,
    customization_options,
    allergens,
    recommended_upsell
) VALUES
('P001', 'Burger', 'Classic Veg Burger', 'Crispy veg patty with lettuce, tomato, onion, and house mayo', 'veg patty; lettuce; tomato; onion; house mayo; burger bun', true, 'mild', true, 'regular:99; large:129', 99, 'extra cheese:+25; extra patty:+45; no onion:0; no mayo:0', 'gluten; dairy', 'French Fries'),
('P002', 'Burger', 'Mushroom Swiss Burger', 'Grilled mushroom burger with Swiss cheese and creamy garlic sauce', 'mushroom; Swiss cheese; lettuce; onion; garlic sauce; burger bun', true, 'mild', true, 'regular:149; large:179', 149, 'extra mushroom:+35; extra cheese:+30; no onion:0; no garlic sauce:0', 'gluten; dairy', 'Cold Coffee'),
('P003', 'Pizza', 'Mushroom Corn Pizza', 'Cheesy pizza topped with mushrooms, sweet corn, capsicum, and oregano', 'pizza base; mozzarella; mushroom; sweet corn; capsicum; oregano; tomato sauce', true, 'mild', true, 'small:199; medium:299; large:399', 199, 'extra mushroom:+40; extra cheese:+50; thin crust:+30; no capsicum:0', 'gluten; dairy', 'Garlic Bread'),
('P004', 'Pizza', 'Paneer Tikka Pizza', 'Indian-style paneer pizza with tikka sauce, onion, and capsicum', 'pizza base; mozzarella; paneer; tikka sauce; onion; capsicum', true, 'medium', true, 'small:229; medium:329; large:429', 229, 'extra paneer:+60; extra cheese:+50; thin crust:+30; less spicy:0', 'gluten; dairy', 'Masala Fries'),
('P005', 'Sandwich', 'Grilled Mushroom Sandwich', 'Toasted sandwich filled with mushrooms, cheese, onion, and pepper', 'bread; mushroom; cheese; onion; black pepper; butter', true, 'mild', true, 'regular:119; combo:179', 119, 'extra mushroom:+35; extra cheese:+25; no onion:0; brown bread:+15', 'gluten; dairy', 'Lemon Iced Tea'),
('P006', 'Wrap', 'Spicy Paneer Wrap', 'Soft wrap with paneer cubes, lettuce, onion, and spicy mayo', 'wrap; paneer; lettuce; onion; spicy mayo; capsicum', true, 'hot', true, 'regular:139; combo:199', 139, 'extra paneer:+50; no onion:0; less spicy:0; add cheese:+25', 'gluten; dairy', 'French Fries'),
('P007', 'Pasta', 'Creamy Mushroom Pasta', 'White sauce pasta with mushrooms, garlic, herbs, and parmesan', 'pasta; mushroom; white sauce; garlic; herbs; parmesan', true, 'mild', true, 'regular:189; large:249', 189, 'extra mushroom:+40; extra parmesan:+35; extra sauce:+25; no garlic:0', 'gluten; dairy', 'Garlic Bread'),
('P008', 'Fries', 'Loaded Cheese Fries', 'Crispy fries topped with cheese sauce, jalapenos, and seasoning', 'potato fries; cheese sauce; jalapeno; peri peri seasoning', true, 'medium', true, 'regular:129; large:169', 129, 'extra cheese sauce:+30; no jalapeno:0; extra seasoning:+10', 'dairy', 'Classic Veg Burger'),
('P009', 'Beverage', 'Cold Coffee', 'Chilled coffee blended with milk, sugar, and ice cream', 'coffee; milk; sugar; vanilla ice cream', true, 'none', true, 'regular:99; large:129', 99, 'less sugar:0; no ice cream:0; extra ice cream:+30', 'dairy', 'Mushroom Swiss Burger'),
('P010', 'Side', 'Garlic Bread', 'Toasted bread with garlic butter, herbs, and optional cheese', 'bread; garlic butter; herbs; cheese', true, 'mild', true, 'regular:89; cheese:119', 89, 'add cheese:+30; extra garlic butter:+20', 'gluten; dairy', 'Mushroom Corn Pizza');


