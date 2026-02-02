-- EatSmartly Database Setup Script
-- Run this to create the PostgreSQL database and tables

-- Create database (run this as postgres superuser first)
-- CREATE DATABASE eatsmartly;
-- CREATE USER eatsmartly WITH PASSWORD 'password';
-- GRANT ALL PRIVILEGES ON DATABASE eatsmartly TO eatsmartly;

-- Connect to eatsmartly database and run the rest:

-- Food Products Table (from APIs and manual entries)
CREATE TABLE IF NOT EXISTS food_products (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(20) UNIQUE,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(100),
    source VARCHAR(50), -- 'open_food_facts', 'usda', 'ifct2017', 'manual'
    
    -- Nutrition per 100g
    calories FLOAT,
    protein_g FLOAT,
    carbs_g FLOAT,
    fat_g FLOAT,
    saturated_fat_g FLOAT,
    trans_fat_g FLOAT,
    fiber_g FLOAT,
    sugar_g FLOAT,
    sodium_mg FLOAT,
    cholesterol_mg FLOAT,
    
    -- Additional nutrients
    calcium_mg FLOAT,
    iron_mg FLOAT,
    vitamin_a_mcg FLOAT,
    vitamin_c_mg FLOAT,
    vitamin_d_mcg FLOAT,
    
    -- Food composition
    moisture_g FLOAT,
    ash_g FLOAT,
    
    -- Ingredients and allergens
    ingredients TEXT,
    allergens TEXT,
    
    -- Metadata
    serving_size FLOAT,
    serving_unit VARCHAR(20),
    is_indian_product BOOLEAN DEFAULT FALSE,
    
    -- Web scraping data
    official_website VARCHAR(500),
    product_page_url VARCHAR(500),
    last_scraped_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IFCT 2017 Indian Food Composition Table
CREATE TABLE IF NOT EXISTS ifct_foods (
    id SERIAL PRIMARY KEY,
    food_code VARCHAR(20) UNIQUE,
    food_name VARCHAR(255) NOT NULL,
    food_name_hindi VARCHAR(255),
    
    -- Food classification
    food_group VARCHAR(100),
    food_subgroup VARCHAR(100),
    scientific_name VARCHAR(255),
    
    -- Nutrition per 100g (edible portion)
    moisture_g FLOAT,
    protein_g FLOAT,
    fat_g FLOAT,
    ash_g FLOAT,
    crude_fiber_g FLOAT,
    carbohydrate_g FLOAT,
    energy_kcal FLOAT,
    
    -- Minerals
    calcium_mg FLOAT,
    phosphorus_mg FLOAT,
    iron_mg FLOAT,
    sodium_mg FLOAT,
    potassium_mg FLOAT,
    magnesium_mg FLOAT,
    zinc_mg FLOAT,
    copper_mg FLOAT,
    
    -- Vitamins
    carotene_mcg FLOAT,
    vitamin_a_mcg FLOAT,
    thiamin_mg FLOAT,
    riboflavin_mg FLOAT,
    niacin_mg FLOAT,
    vitamin_c_mg FLOAT,
    folic_acid_mcg FLOAT,
    
    -- Fatty acids
    saturated_fatty_acids_g FLOAT,
    monounsaturated_fatty_acids_g FLOAT,
    polyunsaturated_fatty_acids_g FLOAT,
    
    -- Amino acids (essential)
    tryptophan_mg FLOAT,
    threonine_mg FLOAT,
    isoleucine_mg FLOAT,
    leucine_mg FLOAT,
    lysine_mg FLOAT,
    methionine_mg FLOAT,
    phenylalanine_mg FLOAT,
    valine_mg FLOAT,
    
    -- Other data
    edible_portion_percent FLOAT,
    refuse_percent FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Alternatives Table (better options)
CREATE TABLE IF NOT EXISTS product_alternatives (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES food_products(id),
    alternative_product_id INTEGER REFERENCES food_products(id),
    
    reason VARCHAR(50), -- 'lower_sugar', 'higher_protein', 'less_fat', 'more_fiber'
    score_improvement FLOAT, -- How much better (percentage)
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Demographics
    age INTEGER,
    gender VARCHAR(10),
    height_cm FLOAT,
    weight_kg FLOAT,
    
    -- Activity and goals
    activity_level VARCHAR(20), -- sedentary, light, moderate, active, very_active
    health_goal VARCHAR(50), -- weight_loss, weight_gain, maintain, muscle_gain
    
    -- Health conditions
    allergies TEXT,
    health_conditions TEXT, -- diabetes, hypertension, heart_disease, etc.
    dietary_restrictions TEXT, -- vegetarian, vegan, gluten_free, etc.
    
    -- Daily targets
    daily_calorie_target FLOAT,
    daily_protein_target_g FLOAT,
    daily_carbs_target_g FLOAT,
    daily_fat_target_g FLOAT,
    daily_fiber_target_g FLOAT,
    daily_sodium_target_mg FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scan History Table
CREATE TABLE IF NOT EXISTS scan_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    product_id INTEGER REFERENCES food_products(id),
    barcode VARCHAR(20),
    
    verdict VARCHAR(20), -- safe, caution, avoid
    health_score FLOAT,
    
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Search Cache Table (for faster searches)
CREATE TABLE IF NOT EXISTS product_search_cache (
    id SERIAL PRIMARY KEY,
    search_query VARCHAR(255) NOT NULL,
    product_ids TEXT,
    result_count INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_search_query UNIQUE (search_query)
);

-- Create indexes for faster queries
CREATE INDEX idx_food_products_barcode ON food_products(barcode);
CREATE INDEX idx_food_products_name ON food_products(name);
CREATE INDEX idx_food_products_brand ON food_products(brand);
CREATE INDEX idx_food_products_category ON food_products(category);
CREATE INDEX idx_ifct_foods_name ON ifct_foods(food_name);
CREATE INDEX idx_ifct_foods_group ON ifct_foods(food_group);
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_scan_history_user_id ON scan_history(user_id);
CREATE INDEX idx_scan_history_product_id ON scan_history(product_id);

-- Trigger to update updated_at timestamp for food_products
CREATE OR REPLACE TRIGGER update_food_products_updated_at
BEFORE UPDATE ON food_products
FOR EACH ROW
BEGIN
    :NEW.updated_at := CURRENT_TIMESTAMP;
END;
/

-- Trigger to update updated_at timestamp for user_profiles
CREATE OR REPLACE TRIGGER update_user_profiles_updated_at
BEFORE UPDATE ON user_profiles
FOR EACH ROW
BEGIN
    :NEW.updated_at := CURRENT_TIMESTAMP;
END;
/

-- Sample IFCT data insert (you'll populate this from the PDF)
-- INSERT INTO ifct_foods (food_code, food_name, food_group, protein_g, carbohydrate_g, fat_g, energy_kcal)
-- VALUES 
-- ('A001', 'Rice, raw, milled', 'Cereals and Millets', 6.8, 78.2, 0.5, 345),
-- ('A002', 'Wheat, whole', 'Cereals and Millets', 11.8, 71.2, 1.5, 346);

COMMENT ON TABLE food_products IS 'Main product database from all sources';
COMMENT ON TABLE ifct_foods IS 'Indian Food Composition Tables 2017 data';
COMMENT ON TABLE product_alternatives IS 'Better alternative products';
COMMENT ON TABLE user_profiles IS 'User health profiles and preferences';
COMMENT ON TABLE scan_history IS 'History of user scans';
