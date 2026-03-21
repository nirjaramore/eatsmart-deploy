import React, { useState, useRef, useEffect } from 'react'

type Item = {
    id: string
    name: string
    url: string
    status: 'idle' | 'processing' | 'done' | 'error'
    progress: number
    text: string
    error?: string
    parsed?: Record<string, any>
    productName?: string
    size?: number
    file?: File
    uploadedAndSaved?: boolean
}

function parseNutrition(text: string) {
    // Clean up the text - remove extra whitespace, normalize
    const cleanText = text.replace(/\s+/g, ' ').toLowerCase().trim()

    // More comprehensive OCR correction for common misreads
    let correctedText = cleanText
        // Character-level corrections
        .replace(/\btol\b/g, 'total')
        .replace(/\bh\b/g, 'g')
        .replace(/\bs\b/g, 'g')
        .replace(/\ba\b/g, '4')
        .replace(/\bz\b/g, '2')
        .replace(/\bco\b/g, '0')
        .replace(/\bhi\b/g, '0')
        .replace(/\bti\b/g, '1')
        .replace(/\bii\b/g, '1')
        .replace(/\bll\b/g, '1')
        .replace(/\bjj\b/g, '1')
        .replace(/\bee\b/g, '6')
        .replace(/\bbb\b/g, '6')
        .replace(/\bgg\b/g, '9')
        .replace(/\bqq\b/g, '9')
        // Word-level corrections for nutrition terms
        .replace(/\bprot\b/g, 'protein')
        .replace(/\bcarb\b/g, 'carbohydrate')
        .replace(/\bsug\b/g, 'sugar')
        .replace(/\bfib\b/g, 'fiber')
        .replace(/\bna\b/g, 'sodium')
        .replace(/\bcal\b/g, 'calories')
        .replace(/\bkcal\b/g, 'calories')
        .replace(/\bener\b/g, 'energy')
        .replace(/\bsat\b/g, 'saturated')
        .replace(/\btot\b/g, 'total')
        .replace(/\bchol\b/g, 'cholesterol')
        .replace(/\bdiet\b/g, 'dietary')
        // Common OCR misreads for numbers and units
        .replace(/\b(\d)o\b/g, '$1g')  // 10o -> 10g
        .replace(/\b(\d)i\b/g, '$1g')  // 10i -> 10g
        .replace(/\b(\d)l\b/g, '$1g')  // 10l -> 10g
        // Fix common garbled sequences
        .replace(/\butruon\b/g, 'protein')
        .replace(/\bacd\b/g, 'acid')
        .replace(/\blennnn\b/g, 'energy')
        .replace(/\bmamn\b/g, 'mann')
        .replace(/\bdl\b/g, 'dl')
        .replace(/\bduur\b/g, 'sugar')
        .replace(/\bsnackboldly\b/g, 'snack boldly')
        // More pattern corrections
        .replace(/\bex(\d+)\b/g, 'energy $1')  // ex5 -> energy 5
        .replace(/\benergv\b/g, 'energy')
        .replace(/\bprotem\b/g, 'protein')
        .replace(/\bcarbohvdrate\b/g, 'carbohydrate')
        .replace(/\bsuqar\b/g, 'sugar')
        .replace(/\bfber\b/g, 'fiber')
        .replace(/\bsodum\b/g, 'sodium')
        .replace(/\bcalores\b/g, 'calories')
        .replace(/\btatal\b/g, 'total')
        .replace(/\bsaturted\b/g, 'saturated')
        .replace(/\bcholestrerol\b/g, 'cholesterol')

    // More flexible regex-based parser to extract common fields
    const findValue = (keys: string[], text: string) => {
        for (const k of keys) {
            // More flexible patterns: "protein 10g", "protein: 10g", "total protein 10g", etc.
            const patterns = [
                new RegExp(`\\b${k}\\b\\s*[:\\-]?\\s*(\\d{1,4}(?:[\\.,]\\d+)?)\\s*(g|mg|kcal|cal|kj|ml)?`, 'i'),
                new RegExp(`\\btotal\\s+${k}\\b\\s*[:\\-]?\\s*(\\d{1,4}(?:[\\.,]\\d+)?)\\s*(g|mg|kcal|cal|kj|ml)?`, 'i'),
                new RegExp(`\\b${k}\\s+per\\s+serving\\b\\s*[:\\-]?\\s*(\\d{1,4}(?:[\\.,]\\d+)?)\\s*(g|mg|kcal|cal|kj|ml)?`, 'i'),
                // Handle cases where number comes first: "10g protein"
                new RegExp(`(\\d{1,4}(?:[\\.,]\\d+)?)\\s*(g|mg|kcal|cal|kj|ml)?\\s*\\b${k}\\b`, 'i'),
                // Handle "protein (g)" format
                new RegExp(`\\b${k}\\b\\s*\\([^)]*\\)\\s*[:\\-]?\\s*(\\d{1,4}(?:[\\.,]\\d+)?)`, 'i'),
                // Fuzzy matching for garbled text - look for number near keyword
                new RegExp(`\\b${k}\\w*\\s*(\\d{1,4}(?:[\\.,]\\d+)?)\\s*(g|mg|kcal|cal|kj|ml)?`, 'i'),
                new RegExp(`(\\d{1,4}(?:[\\.,]\\d+)?)\\s*(g|mg|kcal|cal|kj|ml)?\\s*\\b${k}\\w*`, 'i'),
                // Table-ish spacing / no delimiter line styles
                new RegExp(`\\b${k}\\b\\s+(\\d{1,4}(?:[\\.,]\\d+)?)\\b`, 'i'),
            ]

            for (const re of patterns) {
                const m = text.match(re)
                if (m) return { value: parseFloat(String(m[1]).replace(',', '.')), unit: m[2] || '' }
            }
        }
        return null
    }

    // Expanded nutrient keywords
    const protein = findValue(['protein', 'proteins', 'prot'], correctedText)
    const fat = findValue(['fat', 'fats', 'total fat', 'saturated fat', 'sat fat', 'lipid', 'lipids'], correctedText)
    const carbs = findValue(['carbohydrate', 'carbohydrates', 'carbs', 'total carbohydrate', 'total carbs', 'carb'], correctedText)
    const sugar = findValue(['sugar', 'sugars', 'total sugar', 'added sugar', 'sug'], correctedText)
    const calories = findValue(['calories', 'calorie', 'energy', 'kcal', 'cal', 'cals'], correctedText)
    const fiber = findValue(['fiber', 'fibre', 'dietary fiber', 'fib'], correctedText)
    const sodium = findValue(['sodium', 'salt', 'na'], correctedText)

    // Parsed result accumulator (allow nested objects like `_debug`)
    const parsed: Record<string, any> = {}

    // Attempt to extract a product name/title from the OCR text
    const lines = text.split(/\r?\n/).map(l => l.trim()).filter(Boolean)
    const titleCandidates = lines.filter(l => l.length > 2 && l.length < 80)

    // Filter out lines that are likely nutritional values or common labels
    const nutritionKeywords = /^(nutrition|facts|ingredients|calories|protein|fat|carb|sugar|fiber|sodium|serving|contains|allergen|energy|total|per|value)/i
    const meaningfulLines = titleCandidates.filter(l =>
        !nutritionKeywords.test(l) &&
        !/^\d+\s*(g|mg|kcal|cal|%|ml|oz)/i.test(l) && // not just a number with unit
        l.split(' ').length <= 8 // reasonable product name length
    )

    const isLikelyTitle = (s: string) => {
        // Uppercase or Title Case heuristic
        const upper = s.replace(/[^A-Z0-9 ]/g, '')
        if (upper && upper === s.toUpperCase() && s.split(' ').length >= 2 && s.split(' ').length <= 6) return true
        // Title case: most words start with capital letter
        const words = s.split(' ')
        const capit = words.filter(w => /^[A-Z][a-z]/.test(w)).length
        if (capit >= Math.max(1, Math.floor(words.length / 2))) return true
        return false
    }

    let productName = ''
    // Prioritize lines from the first 3-5 lines (brand/product usually at top)
    const topLines = meaningfulLines.slice(0, 5)
    for (const l of topLines) {
        if (isLikelyTitle(l)) {
            productName = l
            break
        }
    }
    if (!productName && meaningfulLines.length) {
        // Use the longest meaningful line from top section (likely brand/product)
        productName = meaningfulLines[0]
    }
    if (productName) parsed.product_name = productName

    // Fallback: Look for numbers with units and try to infer nutrient type
    const fallbackParse = (text: string) => {
        const fallback: Record<string, number | string> = {}

        // Find all number-unit combinations
        const numberUnitPattern = /(\d+(?:\.\d+)?)\s*(g|mg|kcal|cal|kj)/gi
        const matches = [...text.matchAll(numberUnitPattern)]

        if (matches.length > 0) {
            // Common nutrition label order: calories, fat, carbs, protein, etc.
            const nutrientOrder = ['calories', 'fat', 'carbs', 'protein', 'sugar', 'fiber', 'sodium']
            let matchIndex = 0

            for (const nutrient of nutrientOrder) {
                if (matchIndex < matches.length) {
                    const match = matches[matchIndex]
                    const value = parseFloat(match[1])
                    const unit = match[2].toLowerCase()

                    // Only assign if we haven't found this nutrient already
                    if (!(nutrient in parsed)) {
                        if ((nutrient === 'calories' && (unit === 'kcal' || unit === 'cal')) ||
                            (nutrient !== 'calories' && (unit === 'g' || unit === 'mg'))) {
                            fallback[nutrient] = value
                            matchIndex++
                        }
                    }
                }
            }
        }

        return fallback
    }

    const fallbackResults = fallbackParse(correctedText)

    // Merge fallback results with main parsing (only add if not already found)
    Object.keys(fallbackResults).forEach(key => {
        if (!(key in parsed)) {
            parsed[key] = fallbackResults[key]
        }
    })

    // Add debug info
    parsed._debug = {
        extracted_text: text,
        clean_text: cleanText,
        corrected_text: correctedText,
        found_patterns: {
            protein: !!protein,
            fat: !!fat,
            carbs: !!carbs,
            sugar: !!sugar,
            calories: !!calories,
            fiber: !!fiber,
            sodium: !!sodium
        }
    }

    // simple categorization per 100g heuristics (approx)
    const categories: string[] = []
    const p = protein?.value || 0
    const f = fat?.value || 0
    const s = sugar?.value || 0
    if (p >= 10) categories.push('High protein')
    if (f >= 17.5) categories.push('High fat')
    if (s >= 22.5) categories.push('High sugar')
    if (categories.length) parsed.categories = categories.join(', ')

    return parsed
}

// Search OpenFoodFacts by brand/product name to avoid unnecessary Vision API calls
async function searchOpenFoodFactsByBrand(brandOrProduct: string): Promise<any | null> {
    try {
        // Clean up brand name for search
        const searchTerm = brandOrProduct.toLowerCase().trim()
        const searchUrl = `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${encodeURIComponent(searchTerm)}&search_simple=1&action=process&json=1&page_size=5`

        const res = await fetch(searchUrl)
        const data = await res.json()

        if (data && data.products && data.products.length > 0) {
            // Return the first matching product
            const product = data.products[0]
            console.log('✅ Found product in OpenFoodFacts:', product.product_name || product.brands)
            return {
                barcode: product.code,
                product_name: product.product_name,
                brand: product.brands,
                nutriments: product.nutriments,
                image_url: product.image_url,
                from_openfoodfacts: true
            }
        }
        return null
    } catch (e) {
        console.error('OpenFoodFacts search failed:', e)
        return null
    }
}

export default function ImageUploadExtract() {
    const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8006').replace(/\/$/, '')
    const [items, setItems] = useState<Item[]>([])
    const [showThankYou, setShowThankYou] = useState(false)
    const [thankYouMessage, setThankYouMessage] = useState('')
    const [thankYouImageUrl, setThankYouImageUrl] = useState<string | null>(null)
    const processingIdRef = useRef<string | null>(null)
    const thankYouTimeoutRef = useRef<number | null>(null)
    const browseInputRef = useRef<HTMLInputElement | null>(null)

    useEffect(() => {
        // No cleanup needed for backend Vision API
        return () => {
            if (thankYouTimeoutRef.current) {
                window.clearTimeout(thankYouTimeoutRef.current)
                thankYouTimeoutRef.current = null
            }
            if (thankYouImageUrl) {
                try { URL.revokeObjectURL(thankYouImageUrl) } catch (e) { }
            }
        }
    }, [])

    const onFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || [])
        if (!files.length) return

        const newItems: Item[] = files.map((file) => ({
            id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
            name: file.name,
            url: URL.createObjectURL(file),
            status: 'idle',
            progress: 0,
            text: '',
            size: file.size,
            file
        }))

        setItems((s) => [...newItems, ...s])
    }

    const handleNext = async () => {
        const pending = items.filter(it => it.status === 'idle' && it.file)
        if (!pending.length) return

        for (const it of pending) {
            if (it.file) {
                await processFile(it.file, it.id)
            }
        }
    }

    const processFile = async (file: File, id: string) => {
        // mark current processing id
        processingIdRef.current = id
        setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'processing', progress: 0 } : it)))

        // first attempt: detect barcode (fast, client-side)
        try {
            const barcode = await detectBarcodeFromFile(file)
            if (barcode) {
                // query OpenFoodFacts
                try {
                    const res = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`)
                    const j = await res.json()
                    if (j && j.status === 1) {
                        const prod = j.product
                        const parsed: Record<string, any> = {
                            protein: prod.nutriments?.proteins_100g || null,
                            fat: prod.nutriments?.fat_100g || null,
                            carbs: prod.nutriments?.carbohydrates_100g || null,
                            sugar: prod.nutriments?.sugars_100g || null,
                            calories: prod.nutriments?.energy_kcal_100g || prod.nutriments?.energy_100g || null,
                            categories: [] as string[]
                        }
                        if (parsed.protein && parsed.protein >= 10) parsed.categories.push('High protein')
                        if (parsed.fat && parsed.fat >= 17.5) parsed.categories.push('High fat')
                        if (parsed.sugar && parsed.sugar >= 22.5) parsed.categories.push('High sugar')

                        setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'done', progress: 100, text: JSON.stringify(prod, null, 2), parsed } : it)))
                        return
                    }
                } catch (e) {
                    // continue to OCR fallback
                }
            }
        } catch (e) {
            // ignore barcode detection failures, continue to OCR
        }

        try {
            // Extract text using Google Cloud Vision API (primary) with OCR.space fallback
            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, progress: 30 } : it)))

            const formData = new FormData()
            formData.append('file', file)

            let text = ''
            let apiUsed: string = 'unknown'
            try {
                const ocrResponse = await fetch(`${API_BASE_URL}/extract-text`, {
                    method: 'POST',
                    body: formData
                })

                if (ocrResponse.ok) {
                    const ocrResult = await ocrResponse.json()
                    text = ocrResult.extracted_text || ''
                    apiUsed = ocrResult.api_used || 'unknown'
                    const visionUsage = ocrResult.vision_usage || {}
                    console.log(`📊 Text extraction completed using ${apiUsed}. Google Cloud Vision API units used: ${visionUsage.units_used || 0}/${visionUsage.units_limit || 1000}`)
                } else {
                    // server responded with error (but fetch succeeded) - log and continue with fallback
                    let errMsg = `OCR failed: ${ocrResponse.status} ${ocrResponse.statusText}`
                    try {
                        const errBody = await ocrResponse.json()
                        if (errBody && (errBody.detail || errBody.error)) errMsg = String(errBody.detail || errBody.error)
                    } catch (e) { }
                    console.error('Google Cloud Vision API request failed (server):', errMsg)
                    // leave text as empty so parseNutrition + filename fallback will run
                }
            } catch (fetchErr) {
                // network-level failure (connection refused etc) - continue with local fallback
                console.error('Google Cloud Vision API fetch failed (network):', fetchErr)
                text = ''
            }

            // Also try to detect product labels and barcode using Google Cloud Vision API (uses 3 units)
            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, progress: 50 } : it)))
            let detectionResult: any = null
            try {
                const detectFormData = new FormData()
                detectFormData.append('file', file)
                const detectResponse = await fetch(`${API_BASE_URL}/detect-product`, {
                    method: 'POST',
                    body: detectFormData
                })
                if (detectResponse.ok) {
                    detectionResult = await detectResponse.json()
                    console.log('🔍 Product detection results:', detectionResult)
                    console.log('📊 Barcode in response:', detectionResult?.barcode || 'NOT FOUND')
                    console.log('🏷️ Brand in response:', detectionResult?.detected_brand || 'NOT FOUND')
                    console.log('🌐 Web entities count:', detectionResult?.web_entities?.length || 0)
                    console.log('📝 Detected text:', detectionResult?.detected_text_full?.substring(0, 300) || 'None')
                }
            } catch (e) {
                // Product detection is optional, continue without it
                console.log('Product detection skipped:', e)
            }

            // NEW APPROACH: Extract product name from OCR text first, then search Amazon/BigBasket
            // This is MORE RELIABLE than barcode detection which often fails
            console.log('📝 Extracting product name from OCR text...')

            // Extract product name from detected text
            let extractedProductName = ''
            if (detectionResult && detectionResult.detected_text_full) {
                const lines = detectionResult.detected_text_full.split('\n').map((l: string) => l.trim()).filter(Boolean)
                // Look for product names in first 5 lines (usually at top of package)
                const topLines = lines.slice(0, 5)
                for (const line of topLines) {
                    // Skip common non-product text
                    const lower = line.toLowerCase()
                    if (lower.includes('fssai') || lower.includes('authority') ||
                        lower.includes('license') || lower.includes('office') ||
                        lower.length < 3 || /^\d+$/.test(line)) {
                        continue
                    }
                    // Look for lines with product-like names (uppercase, 2-6 words, or mixed case with capitals)
                    if ((line === line.toUpperCase() || /[A-Z]/.test(line)) &&
                        line.split(' ').length >= 2 &&
                        line.split(' ').length <= 8 &&
                        line.length >= 5) {
                        extractedProductName = line
                        console.log('🎯 Extracted product name from OCR:', line)
                        break
                    }
                }
            }

            // Also try with detected brand if we found one
            if (!extractedProductName && detectionResult?.detected_brand) {
                extractedProductName = detectionResult.detected_brand
                console.log('🏷️ Using detected brand as product name:', extractedProductName)
            }

            // NEW: Search Amazon India and BigBasket for the product
            if (extractedProductName && extractedProductName.length >= 3) {
                console.log(`🔍 Searching Amazon India & BigBasket for: "${extractedProductName}"`)
                setItems((prev) => prev.map((it) => (it.id === id ? { ...it, progress: 70 } : it)))

                try {
                    const searchResponse = await fetch(`${API_BASE_URL}/search-product-by-name`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            product_name: extractedProductName,
                            max_results: 3
                        })
                    })

                    if (searchResponse.ok) {
                        const searchResult = await searchResponse.json()
                        console.log('🛒 Search results:', searchResult)

                        if (searchResult.found && searchResult.results && searchResult.results.length > 0) {
                            // Use top match (highest confidence)
                            const topMatch = searchResult.results[0]
                            console.log(`✅ TOP MATCH: ${topMatch.product_name} from ${topMatch.source} (₹${topMatch.price || 'N/A'})`)

                            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, progress: 85 } : it)))

                            // Get detailed product info including nutrition
                            if (topMatch.product_url) {
                                try {
                                    const detailsResponse = await fetch(`${API_BASE_URL}/get-product-details?product_url=${encodeURIComponent(topMatch.product_url)}`)

                                    if (detailsResponse.ok) {
                                        const detailsResult = await detailsResponse.json()
                                        const productData = detailsResult.product

                                        console.log('📦 Got complete product details:', productData.product_name)
                                        if (productData.nutrition) {
                                            console.log('✅ Nutrition data included:', Object.keys(productData.nutrition))
                                        }

                                        // Build parsed object with nutrition
                                        const parsed: Record<string, any> = {
                                            product_name: productData.product_name,
                                            brand: productData.brand,
                                            price: productData.price,
                                            rating: productData.rating,
                                            protein: productData.nutrition?.protein || null,
                                            fat: productData.nutrition?.totalFat || null,
                                            carbs: productData.nutrition?.carbs || null,
                                            sugar: productData.nutrition?.sugars || null,
                                            calories: productData.nutrition?.calories || null,
                                            fiber: productData.nutrition?.fiber || null,
                                            sodium: productData.nutrition?.sodium || null,
                                            image_url: productData.image_url || topMatch.image_url,
                                            product_url: topMatch.product_url,
                                            source: topMatch.source,
                                            description: productData.description,
                                            features: productData.features || [],
                                            from_web_scraping: true,
                                            categories: [] as string[]
                                        }

                                        // Add health categories
                                        if (parsed.protein && parsed.protein >= 10) parsed.categories.push('High protein')
                                        if (parsed.fat && parsed.fat >= 17.5) parsed.categories.push('High fat')
                                        if (parsed.sugar && parsed.sugar >= 22.5) parsed.categories.push('High sugar')

                                        setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'done', progress: 100, text: JSON.stringify(productData, null, 2), parsed } : it)))
                                        console.log(`💾 Product data ready from ${topMatch.source} (WEB SCRAPING)`)

                                        // Keep parsed result visible; user can review then click Save.
                                        return
                                    }
                                } catch (e) {
                                    console.error('Failed to get product details:', e)
                                }
                            }

                            // If couldn't get detailed info, use basic search result
                            const parsed: Record<string, any> = {
                                product_name: topMatch.product_name,
                                brand: topMatch.brand,
                                price: topMatch.price,
                                rating: topMatch.rating,
                                image_url: topMatch.image_url,
                                product_url: topMatch.product_url,
                                source: topMatch.source,
                                from_web_scraping: true,
                                categories: []
                            }

                            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'done', progress: 100, text: JSON.stringify(topMatch, null, 2), parsed } : it)))
                            console.log(`💾 Basic product data from ${topMatch.source}`)

                            return
                        } else {
                            console.log('⚠️ No products found in Amazon/BigBasket search, will use OCR fallback')
                        }
                    }
                } catch (e) {
                    console.error('Product search failed:', e)
                }
            } else {
                console.log('⚠️ Could not extract product name from image, will use OCR fallback')
            }

            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, progress: 80 } : it)))
            const parsed = parseNutrition(text)

            // Enhance parsed data with Google Cloud Vision API detection results
            if (detectionResult) {
                // Store barcode if detected
                if (detectionResult.barcode) {
                    parsed.barcode = detectionResult.barcode
                }

                // Priority 0: Extract product name from detected text (most accurate for product names on packaging)
                if (detectionResult.detected_text_full && !parsed.product_name) {
                    const lines = detectionResult.detected_text_full.split('\\n').map((l: string) => l.trim()).filter(Boolean)
                    // Look for product names in first 5 lines (usually at top of package)
                    const topLines = lines.slice(0, 5)
                    for (const line of topLines) {
                        // Skip common non-product text
                        const lower = line.toLowerCase()
                        if (lower.includes('fssai') || lower.includes('authority') ||
                            lower.includes('license') || lower.includes('office') ||
                            lower.length < 3 || /^\\d+$/.test(line)) {
                            continue
                        }
                        // Look for lines with product-like names (uppercase, 2-6 words)
                        if (line === line.toUpperCase() && line.split(' ').length >= 2 && line.split(' ').length <= 6) {
                            parsed.product_name = line
                            console.log('🎯 Extracted product name from OCR:', line)
                            break
                        }
                    }
                }

                // Priority 1: Use detected brand as product name base
                if (detectionResult.detected_brand) {
                    if (!parsed.product_name) {
                        parsed.product_name = detectionResult.detected_brand
                    } else if (parsed.product_name && parsed.product_name.length < 15) {
                        // If OCR gave short generic name, prepend brand
                        parsed.product_name = `${detectionResult.detected_brand} ${parsed.product_name}`
                    }
                }

                // Priority 2: Use web entities (known products from Google's database)
                if (detectionResult.web_entities && detectionResult.web_entities.length > 0) {
                    const productEntity = detectionResult.web_entities.find((e: any) =>
                        e.description &&
                        e.description.length > 3 &&
                        e.description.length < 60 &&
                        e.score > 0.5
                    )
                    if (productEntity && !parsed.product_name) {
                        parsed.product_name = productEntity.description
                    }
                }

                if (detectionResult.primary_category) {
                    parsed.detected_category = detectionResult.primary_category
                }

                if (detectionResult.labels && detectionResult.labels.length > 0) {
                    parsed.vision_labels = detectionResult.labels.slice(0, 5).map((l: any) => l.description)
                    // Priority 3: Use specific food labels if still no name
                    if (!parsed.product_name && detectionResult.labels.length > 0) {
                        const specificLabels = detectionResult.labels.filter((l: any) =>
                            l.description &&
                            l.description.length > 4 &&
                            !['Food', 'Ingredient', 'Recipe', 'Cuisine', 'Dish', 'Snack', 'Product'].includes(l.description)
                        )
                        if (specificLabels.length > 0) {
                            parsed.product_name = specificLabels[0].description
                        }
                    }
                }
                parsed.detection_api = apiUsed
            }

            // If still no product name, use filename as fallback
            if (!parsed.product_name) {
                parsed.product_name = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ')
            }

            console.log('✅ Extraction complete! Parsed nutrition data:', parsed)
            console.log('📦 Product Name Detected:', parsed.product_name || 'Not found')
            console.log('📊 Barcode:', detectionResult?.barcode || parsed.barcode || 'Not detected')
            console.log('🏷️ Brand:', detectionResult?.detected_brand || 'Not detected')
            console.log('🌐 Web Entities:', detectionResult?.web_entities?.slice(0, 3).map((e: any) => e.description).join(', ') || 'None')
            console.log('�🍎 Nutrition Values:', {
                calories: parsed.calories,
                protein: parsed.protein,
                carbs: parsed.carbs,
                fat: parsed.fat,
                sugar: parsed.sugar,
                fiber: parsed.fiber,
                sodium: parsed.sodium
            })
            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'done', progress: 100, text, parsed } : it)))

            // Keep parsed result visible; user can review then click Save.
        } catch (err: any) {
            const msg = err?.message || String(err) || 'Vision API processing failed'
            console.error('Google Cloud Vision API processing error', err)
            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'error', error: msg } : it)))
        } finally {
            processingIdRef.current = null
        }
    }

    async function detectBarcodeFromFile(file: File): Promise<string | null> {
        // Try BarcodeDetector API first
        try {
            if ((window as any).BarcodeDetector) {
                const img = await createImageBitmap(file)
                const detector = new (window as any).BarcodeDetector({ formats: ['ean_13', 'ean_8', 'upc_e', 'upc_a'] })
                const barcodes = await detector.detect(img)
                if (barcodes && barcodes.length) return barcodes[0].rawValue || null
            }
        } catch (e) {
            // ignore
        }

        // Fallback to zxing-js
        try {
            // dynamic import with a literal string so Next.js can bundle it properly
            const mod: any = await import('@zxing/library')
            const { BrowserMultiFormatReader, DecodeHintType } = mod
            const hints = new Map()
            hints.set(DecodeHintType.POSSIBLE_FORMATS, [])
            const reader = new (BrowserMultiFormatReader as any)(hints)
            // create image element
            const url = URL.createObjectURL(file)
            const img = document.createElement('img')
            img.src = url
            await new Promise((res, rej) => { img.onload = res; img.onerror = rej })
            try {
                // Use await in case decodeFromImageElement returns a Promise
                const result = await (reader.decodeFromImageElement as any)(img)
                if (result) {
                    // ZXing result API may expose text via getText() or text property
                    return (result.getText && result.getText()) || result.text || null
                }
            } catch (err) {
                // no barcode - swallow the error so UI doesn't crash
            } finally {
                URL.revokeObjectURL(url)
            }
        } catch (e) {
            // ignore
        }

        return null
    }

    const saveItem = (it: Item) => {
        (async () => {
            const productName = it.productName?.trim() || it.parsed?.product_name || it.name?.replace(/\.[^/.]+$/, '') || 'Unknown Product'
            if (!productName || productName === 'Unknown Product') {
                alert('Please enter a product name before saving.')
                return
            }

            // Send parsed product to backend to persist in DB
            try {
                let persistedImageUrl: string | undefined
                if (it.file) {
                    const uploadFd = new FormData()
                    uploadFd.append('file', it.file)
                    uploadFd.append('image_type', 'back')
                    uploadFd.append('alt_text', productName)
                    const uploadRes = await fetch(`${API_BASE_URL}/upload-front-image`, { method: 'POST', body: uploadFd })
                    if (uploadRes.ok) {
                        const uploadJson = await uploadRes.json()
                        persistedImageUrl = uploadJson?.url
                    }
                }

                const payload = {
                    name: productName,
                    brand: undefined,
                    calories: it.parsed?.calories || undefined,
                    protein_g: it.parsed?.protein || it.parsed?.protein_g || undefined,
                    carbs_g: it.parsed?.carbs || it.parsed?.carbs_g || undefined,
                    fat_g: it.parsed?.fat || it.parsed?.fat_g || undefined,
                    sugar_g: it.parsed?.sugar || it.parsed?.sugar_g || undefined,
                    fiber_g: it.parsed?.fiber || it.parsed?.fiber_g || undefined,
                    sodium_mg: it.parsed?.sodium || it.parsed?.sodium_mg || undefined,
                    ingredients: it.parsed?._debug?.corrected_text || undefined,
                    allergens: [],
                    image_url: persistedImageUrl || undefined
                }

                // Prefer saving to products table using save-product-complete
                const completePayload = {
                    barcode: null,
                    product_name: productName,
                    brand: payload.brand || null,
                    manufacturer: null,
                    region: null,
                    weight: null,
                    fssai_license: null,
                    image_url: payload.image_url || null,
                    is_verified: false,
                    verified_by: null,
                    nutrition: {
                        serving_size: payload.calories ? 100 : null,
                        servings_per_container: null,
                        calories: payload.calories || null,
                        total_fat: payload.fat_g || null,
                        saturated_fat: null,
                        trans_fat: null,
                        cholesterol: null,
                        sodium: payload.sodium_mg || null,
                        total_carbohydrates: payload.carbs_g || null,
                        dietary_fiber: payload.fiber_g || null,
                        total_sugars: payload.sugar_g || null,
                        added_sugars: null,
                        protein: payload.protein_g || null
                    },
                    user_id: null
                }

                console.log('💾 Saving to database...', completePayload)
                const res = await fetch(`${API_BASE_URL}/save-product-complete`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(completePayload)
                })

                if (!res.ok) {
                    const errBody = await res.text()
                    console.error('❌ Failed to save product to backend', res.status, errBody)
                    alert('Failed to save product to backend')
                    return
                }

                const j = await res.json()
                console.log('✅ Successfully saved to Supabase database!', j)
                console.log('📋 Product ID:', j.product_id)

                // also persist locally for offline convenience
                const stored = JSON.parse(localStorage.getItem('eatsmart_products') || '[]')
                stored.push({ id: it.id, name: it.name, text: it.text, parsed: it.parsed || {}, url: it.url, savedAt: new Date().toISOString(), backend: j })
                localStorage.setItem('eatsmart_products', JSON.stringify(stored))

                // Mark as uploaded and saved (no thank you screen since we already showed it after extraction)
                setItems(prev => prev.map(x => x.id === it.id ? { ...x, uploadedAndSaved: true } : x))
                console.log('✅ Item marked as saved in local state')
            } catch (e) {
                console.error('Save failed', e)
                alert('Error saving product')
            }
        })()
    }

    const clearAll = () => {
        setItems([])
    }

    const onDrop = async (e: React.DragEvent) => {
        e.preventDefault()
        const files = Array.from(e.dataTransfer.files || [])
        if (files.length) {
            const fake = { target: { files } } as unknown as React.ChangeEvent<HTMLInputElement>
            await onFiles(fake)
        }
    }

    const onDragOver = (e: React.DragEvent) => { e.preventDefault() }

    const asNumber = (v: any): number | null => {
        if (v === null || v === undefined || v === '') return null
        if (typeof v === 'number' && Number.isFinite(v)) return v
        if (typeof v === 'string') {
            const cleaned = v.replace(/[^\d.,-]/g, '').replace(',', '.')
            const n = parseFloat(cleaned)
            return Number.isFinite(n) ? n : null
        }
        return null
    }

    const getMetric = (parsed: Record<string, any> | undefined, keys: string[]): number | null => {
        if (!parsed) return null
        for (const k of keys) {
            const n = asNumber(parsed[k])
            if (n !== null) return n
        }
        return null
    }

    const humanSize = (bytes: number) => {
        if (!bytes) return '0 B'
        const units = ['B', 'KB', 'MB', 'GB']
        let i = 0
        let value = bytes
        while (value >= 1024 && i < units.length - 1) { value = value / 1024; i++ }
        return `${Math.round(value * 10) / 10} ${units[i]}`
    }

    return (
        <section aria-label="Upload nutrition labels" style={{ padding: '2.5rem', background: 'var(--brand-bg)', position: 'relative' }}>
            <style jsx>{`
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { 
                        opacity: 0;
                        transform: translateY(30px);
                    }
                    to { 
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
                <div className="upload-card" style={{ width: '100%', maxWidth: 720, borderRadius: 16, background: '#fff', boxShadow: '0 20px 40px rgba(0,0,0,0.08)', padding: 20, position: 'relative', minHeight: 500 }}>
                    {showThankYou ? (
                        <div style={{
                            position: 'absolute',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: '#fff',
                            borderRadius: 16,
                            zIndex: 1000,
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: '2rem',
                            animation: 'fadeIn 0.3s ease-in'
                        }}>
                            <div style={{ width: '100%', borderRadius: 12, overflow: 'hidden', marginBottom: 18 }}>
                                <img
                                    src={thankYouImageUrl || '/thankyou.jpeg'}
                                    alt="Uploaded preview"
                                    style={{
                                        width: '100%',
                                        height: 420,
                                        objectFit: 'cover',
                                        display: 'block'
                                    }}
                                />
                            </div>

                            <div style={{ textAlign: 'center', padding: '0 1rem' }}>
                                <div style={{ fontWeight: 700, fontSize: '1.25rem', marginBottom: 8, color: '#e27575' }}>Thank you for contributing to our community</div>
                                <div style={{ fontSize: 14, color: '#eca6a4' }}>We’ve received your contribution — it will appear after review.</div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ display: showThankYou ? 'none' : 'block' }}>
                            <h2 style={{ margin: 0, marginBottom: 12 }}>Upload Files</h2>
                            <p style={{ marginTop: 0, marginBottom: 18, color: '#eca6a4' }}>Upload your user-downloadable files.</p>

                            <div
                                onDrop={onDrop}
                                onDragOver={onDragOver}
                                style={{ borderRadius: 12, background: '#f6f6f6', padding: 28, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}
                            >
                                <div style={{ width: 64, height: 64, borderRadius: 12, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 6px 18px rgba(0,0,0,0.03)' }}>
                                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 16V8" stroke="#e27575" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /><path d="M8 12l4-4 4 4" stroke="#e27575" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /><path d="M21 15v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2" stroke="#e27575" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                                </div>
                                <div style={{ fontSize: 16, fontWeight: 600, color: '#e27575' }}>Drop your files here or browse</div>
                                <div style={{ fontSize: 12, color: '#eca6a4' }}>Max file size up to 1 GB</div>
                                <div style={{ marginTop: 8 }}>
                                    <input ref={browseInputRef} id="browse-files-input" type="file" accept="image/*,application/pdf" multiple onChange={onFiles} style={{ display: 'none' }} />
                                    <button onClick={() => browseInputRef.current?.click()} style={{ marginTop: 8, padding: '8px 14px', borderRadius: 10, background: '#fff', border: '1px solid #eee' }}>Browse files</button>
                                </div>
                            </div>

                            <div style={{ marginTop: 18 }}>
                                {items.length === 0 && (
                                    <div style={{ padding: 18, borderRadius: 12, background: '#fff', border: '1px solid #f0f0f0', textAlign: 'center', color: '#eca6a4' }}>No files uploaded yet.</div>
                                )}

                                {items.map((it) => (
                                    <div key={it.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', background: '#fff', borderRadius: 10, marginTop: 12, border: '1px solid #f0f0f0' }}>
                                        {it.uploadedAndSaved ? (
                                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', padding: '12px 0' }}>
                                                <img src="/thankyou.jpeg" alt="thankyou" style={{ width: 120, height: 120, objectFit: 'cover', borderRadius: 12, marginBottom: 12 }} />
                                                <div style={{ textAlign: 'center' }}>
                                                    <div style={{ fontWeight: 700, color: '#e27575' }}>Thank you for contributing to our community</div>
                                                    <div style={{ fontSize: 13, color: '#eca6a4', marginTop: 6 }}>We’ve received your contribution — it will appear after review.</div>
                                                </div>
                                            </div>
                                        ) : (
                                            <>
                                                <div style={{ width: 44, height: 44, borderRadius: 8, background: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, color: '#e27575' }}>{it.name.split('.').pop()?.toUpperCase() || 'IMG'}</div>
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                        <div style={{ fontWeight: 600, color: '#e27575' }}>{it.name}</div>
                                                        <div style={{ fontSize: 12, color: '#eca6a4' }}>{humanSize(it.size || 0)}</div>
                                                    </div>

                                                    <div style={{ marginTop: 8 }}>
                                                        <div style={{ height: 8, background: '#eee', borderRadius: 8, overflow: 'hidden' }}>
                                                            <div style={{ width: `${it.progress}%`, height: '100%', background: '#e27575', transition: 'width 300ms' }} />
                                                        </div>
                                                    </div>
                                                    {it.parsed && (
                                                        <>
                                                            <div style={{ marginTop: 8 }}>
                                                                <label style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#e27575', marginBottom: 4 }}>Product name</label>
                                                                <input
                                                                    type="text"
                                                                    placeholder="Enter product name (e.g. Maggi Noodles)"
                                                                    value={it.productName ?? (it.parsed?.product_name || it.name?.replace(/\.[^/.]+$/, '') || '')}
                                                                    onChange={(e) => setItems(prev => prev.map(x => x.id === it.id ? { ...x, productName: e.target.value } : x))}
                                                                    style={{ width: '100%', padding: '8px 10px', borderRadius: 8, border: '1px solid #eee', fontSize: 14, color: '#eca6a4' }}
                                                                />
                                                            </div>
                                                            <div style={{ marginTop: 8, fontSize: 12, color: '#eca6a4' }}>
                                                                Calories: {getMetric(it.parsed, ['calories', 'energy_kcal', 'energy']) ?? 'NA'} |
                                                                Protein: {getMetric(it.parsed, ['protein', 'proteins', 'protein_g']) ?? 'NA'}g |
                                                                Carbs: {getMetric(it.parsed, ['carbs', 'carbohydrates', 'total_carbohydrates', 'carbs_g']) ?? 'NA'}g |
                                                                Fat: {getMetric(it.parsed, ['fat', 'total_fat', 'fat_g']) ?? 'NA'}g |
                                                                Sugar: {getMetric(it.parsed, ['sugar', 'total_sugars', 'sugar_g']) ?? 'NA'}g
                                                            </div>
                                                        </>
                                                    )}
                                                </div>
                                                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                                                    <button disabled={it.status !== 'done'} onClick={() => saveItem(it)} style={{ padding: '8px 10px', borderRadius: 8, background: '#e27575', color: '#fff', border: 'none' }}>Save</button>
                                                    <button onClick={() => setItems((prev) => prev.filter((x) => x.id !== it.id))} style={{ padding: '8px 10px', borderRadius: 8, background: '#fff', border: '1px solid #eee' }}>Delete</button>
                                                </div>
                                            </>
                                        )}
                                    </div>
                                ))}
                            </div>

                            {items.length > 0 && !showThankYou && (
                                <div style={{ marginTop: 18, display: 'flex', justifyContent: 'space-between', gap: 12 }}>
                                    <button onClick={clearAll} style={{ flex: 1, padding: '10px 16px', borderRadius: 999, background: '#fff', border: '1px solid #eee' }}>Back</button>
                                    <button onClick={handleNext} style={{ flex: 1, padding: '10px 16px', borderRadius: 999, background: '#e27575', color: '#fff' }}>Next</button>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
            {/* styles moved to global stylesheet to avoid runtime style insertion issues */}
        </section>
    )
}
