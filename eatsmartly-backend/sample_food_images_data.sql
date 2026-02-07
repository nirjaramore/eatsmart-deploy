-- Sample SQL to populate food_images table with test data
-- Run this in your Supabase SQL Editor

-- Example 1: Using storage_path (will be auto-constructed into full URL)
INSERT INTO food_images (barcode, storage_path, image_type, alt_text)
VALUES 
  ('8901030895784', 'products/maggi-noodles.jpg', 'product', 'Maggi 2-Minute Noodles'),
  ('8901063011588', 'products/parle-g.jpg', 'product', 'Parle-G Biscuits'),
  ('8901058842630', 'products/bournvita.jpg', 'product', 'Cadbury Bournvita');

-- Example 2: Using full image_url (if images are already uploaded)
INSERT INTO food_images (barcode, image_url, storage_path, image_type, alt_text)
VALUES 
  ('8901030895784', 
   'https://your-project.supabase.co/storage/v1/object/public/food-images/products/maggi.jpg',
   'products/maggi.jpg',
   'product', 
   'Maggi Noodles');

-- Example 3: Link to existing foods table
-- First, ensure you have matching entries in the foods table:
INSERT INTO foods (barcode, name, brand, region, is_verified)
VALUES 
  ('8901030895784', 'Maggi 2-Minute Noodles', 'Nestlé', 'India', true),
  ('8901063011588', 'Parle-G Gold Biscuits', 'Parle', 'India', true),
  ('8901058842630', 'Cadbury Bournvita', 'Cadbury', 'India', true);

-- Then add their images
INSERT INTO food_images (barcode, storage_path, image_type, alt_text)
VALUES 
  ('8901030895784', 'products/maggi-2min-noodles.jpg', 'product', 'Maggi Noodles Pack'),
  ('8901063011588', 'products/parle-g-biscuits.jpg', 'product', 'Parle-G Packet'),
  ('8901058842630', 'products/bournvita-jar.jpg', 'product', 'Bournvita Jar');

-- Check your data
SELECT 
    fi.id,
    fi.barcode,
    fi.storage_path,
    fi.image_type,
    f.name as product_name,
    f.brand
FROM food_images fi
LEFT JOIN foods f ON fi.barcode = f.barcode
ORDER BY fi.uploaded_at DESC
LIMIT 10;
