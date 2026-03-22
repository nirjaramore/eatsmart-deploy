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
            const name = (it.productName ?? '').trim() || it.name.replace(/\.[^/.]+$/, '').trim()
            if (name.length < 2) {
                alert('Please enter a product name for each file (e.g. "Britannia Marie Gold") before clicking Next.')
                return
            }
        }

        for (const it of pending) {
            if (it.file) {
                const userName = (it.productName ?? '').trim() || it.name.replace(/\.[^/.]+$/, '').trim()
                await processFile(it.file, it.id, userName)
            }
        }
    }

    /** Map Amazon/BigBasket detail response into `parsed` + optional raw product for Save/UI */
    const buildParsedFromScraperProduct = (productData: Record<string, any>, topMatch: Record<string, any>) => {
        const n = productData.nutrition || {}
                        const parsed: Record<string, any> = {
            product_name: productData.product_name || topMatch.product_name,
            brand: productData.brand ?? topMatch.brand,
            price: productData.price ?? topMatch.price,
            rating: productData.rating ?? topMatch.rating,
            protein: n.protein ?? null,
            fat: n.totalFat ?? null,
            carbs: n.carbs ?? null,
            sugar: n.sugars ?? null,
            calories: n.calories ?? null,
            fiber: n.fiber ?? null,
            sodium: n.sodium ?? null,
            image_url: productData.image_url || topMatch.image_url,
            product_url: topMatch.product_url,
            source: topMatch.source,
            description: productData.description,
            features: productData.features || [],
            specifications: productData.specifications || {},
            from_web_scraping: true,
                            categories: [] as string[]
                        }
                        if (parsed.protein && parsed.protein >= 10) parsed.categories.push('High protein')
                        if (parsed.fat && parsed.fat >= 17.5) parsed.categories.push('High fat')
                        if (parsed.sugar && parsed.sugar >= 22.5) parsed.categories.push('High sugar')
        return parsed
    }

    /** When the Python backend gets 0 hits (Amazon captcha, BigBasket timeout, OFF HTML response), query OFF from the browser. */
    const fetchOffFromBrowser = async (q: string): Promise<{ parsed: Record<string, any>; text: string } | null> => {
        const query = q.trim()
        if (query.length < 2) return null
        const tokenScore = (title: string): number => {
            const qw = new Set((query.toLowerCase().match(/\w{2,}/g) || []) as string[])
            const tw = new Set(((title || '').toLowerCase().match(/\w{2,}/g) || []) as string[])
            if (!qw.size) return 0
            let inter = 0
            for (const w of qw) {
                if (tw.has(w)) inter++
            }
            return inter / qw.size
        }
        const searchBases = [
            'https://world.openfoodfacts.org/cgi/search.pl',
            'https://in.openfoodfacts.org/cgi/search.pl'
        ]
        let products: any[] | null = null
        for (const base of searchBases) {
            try {
                const params = new URLSearchParams({
                    search_terms: query,
                    search_simple: '1',
                    action: 'process',
                    json: '1',
                    page_size: '20'
                })
                const res = await fetch(`${base}?${params}`)
                if (!res.ok) continue
                const data = await res.json()
                const list = data?.products
                if (Array.isArray(list) && list.length) {
                    products = list
                    break
            }
        } catch (e) {
                console.warn('Open Food Facts (browser) search failed:', base, e)
            }
        }
        if (!products?.length) return null

        let best = products[0]
        let bestScore = tokenScore(best.product_name || best.product_name_en || '')
        for (const p of products) {
            const name = p.product_name || p.product_name_en || ''
            const sc = tokenScore(name)
            if (p.code && sc > bestScore) {
                bestScore = sc
                best = p
            }
        }
        if (!best?.code) return null

        const code = String(best.code).replace(/\D/g, '') || String(best.code)
        const apiUrl = `https://world.openfoodfacts.org/api/v0/product/${code}.json`
        let prodRes: Response
        try {
            prodRes = await fetch(apiUrl)
        } catch {
            return null
        }
        if (!prodRes.ok) return null
        const pj = await prodRes.json()
        if (pj.status !== 1 || !pj.product) return null
        const prod = pj.product
        const n = prod.nutriments || {}
        const num = (keys: string[]): number | null => {
            for (const k of keys) {
                const v = n[k]
                if (v !== undefined && v !== null && v !== '') {
                    const x = Number(v)
                    if (!Number.isNaN(x)) return x
                }
            }
            return null
        }
        const nutrition: Record<string, any> = {}
        const cal = num(['energy-kcal_100g', 'energy-kcal'])
        if (cal != null) nutrition.calories = cal
        const protein = num(['proteins_100g', 'proteins'])
        if (protein != null) nutrition.protein = protein
        const fat = num(['fat_100g', 'fat'])
        if (fat != null) nutrition.totalFat = fat
        const carbs = num(['carbohydrates_100g', 'carbohydrates'])
        if (carbs != null) nutrition.carbs = carbs
        const sugars = num(['sugars_100g', 'sugars'])
        if (sugars != null) nutrition.sugars = sugars
        const fiber = num(['fiber_100g', 'fiber'])
        if (fiber != null) nutrition.fiber = fiber
        const sodium = num(['sodium_100g', 'sodium'])
        if (sodium != null) nutrition.sodium = sodium

        const product_url = `https://world.openfoodfacts.org/product/${code}`
        const topMatch = {
            product_name: prod.product_name || prod.product_name_en || best.product_name,
            brand: typeof prod.brands === 'string' ? prod.brands.split(',')[0].trim() : null,
            price: null,
            rating: null,
            image_url: prod.image_front_url || prod.image_url || best.image_front_small_url,
            product_url,
            source: 'Open Food Facts'
        }
        const productData = {
            product_name: topMatch.product_name,
            brand: topMatch.brand,
            nutrition,
            image_url: topMatch.image_url,
            description: prod.generic_name || prod.product_name,
            features: prod.ingredients_text
                ? [
                      `Ingredients: ${String(prod.ingredients_text).slice(0, 500)}${
                          String(prod.ingredients_text).length > 500 ? '…' : ''
                      }`
                  ]
                : [],
            specifications: {
                countries: prod.countries,
                quantity: prod.quantity
            }
        }
        const parsed = buildParsedFromScraperProduct(productData, topMatch)
        console.log('✅ Open Food Facts (direct from browser):', topMatch.product_name)
        return { parsed, text: JSON.stringify(prod, null, 2) }
    }

    type NameLookupResult =
        | { ok: true; parsed: Record<string, any>; text: string }
        | { ok: false; message: string }

    /** Search Amazon + BigBasket by name, then fetch first result product page for nutrition */
    const fetchNutritionByProductName = async (productName: string): Promise<NameLookupResult> => {
        const searchResponse = await fetch(`${API_BASE_URL}/search-product-by-name`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_name: productName, max_results: 5 })
        })
        if (!searchResponse.ok) {
            const errText = await searchResponse.text().catch(() => '')
            console.error('search-product-by-name failed', searchResponse.status, errText)
            return {
                ok: false,
                message: `Product search failed (HTTP ${searchResponse.status}). Check NEXT_PUBLIC_API_BASE_URL matches your backend (e.g. http://127.0.0.1:8765).`
            }
        }
                        const searchResult = await searchResponse.json()
        if (!searchResult.found || !searchResult.results?.length) {
            console.warn('Backend search returned no results; trying Open Food Facts from browser…', searchResult)
            const directOff = await fetchOffFromBrowser(productName)
            if (directOff) {
                return { ok: true, parsed: directOff.parsed, text: directOff.text }
            }
            const backendMsg =
                typeof searchResult.error === 'string' && searchResult.error.trim()
                    ? searchResult.error.trim()
                    : 'No results from backend or browser Open Food Facts.'
            return {
                ok: false,
                message: `${backendMsg} Set NEXT_PUBLIC_API_BASE_URL to your running API. Restart backend after git pull. If browser OFF is blocked (CORS), use a normal network/VPN.`
            }
        }

        const topMatch = searchResult.results[0]
        if (!topMatch.product_url) {
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
            return { ok: true, parsed, text: JSON.stringify(topMatch, null, 2) }
        }

        const detailsResponse = await fetch(
            `${API_BASE_URL}/get-product-details?product_url=${encodeURIComponent(topMatch.product_url)}`,
            { method: 'GET' }
        )
        if (!detailsResponse.ok) {
                            const parsed: Record<string, any> = {
                                product_name: topMatch.product_name,
                                brand: topMatch.brand,
                                price: topMatch.price,
                                rating: topMatch.rating,
                                image_url: topMatch.image_url,
                                product_url: topMatch.product_url,
                                source: topMatch.source,
                                from_web_scraping: true,
                categories: [],
                scrape_note: 'Could not load full product page; showing search result only.'
            }
            return { ok: true, parsed, text: JSON.stringify(topMatch, null, 2) }
        }
        const detailsResult = await detailsResponse.json()
        const productData = detailsResult.product
        const parsed = buildParsedFromScraperProduct(productData, topMatch)
        return { ok: true, parsed, text: JSON.stringify(productData, null, 2) }
    }

    const processFile = async (file: File, id: string, userProductName: string) => {
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
            // ignore barcode detection failures, continue to marketplace search by name
        }

        try {
            // Use Amazon India + BigBasket scrapers with the name the user typed (no OCR on label)
            console.log(`🔍 Looking up nutrition via marketplace scrapers for: "${userProductName}"`)
            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, progress: 40 } : it)))

            const scraped = await fetchNutritionByProductName(userProductName.trim())
            if (scraped.ok) {
                setItems((prev) =>
                    prev.map((it) =>
                        it.id === id
                            ? {
                                  ...it,
                    status: 'done',
                    progress: 100,
                                  text: scraped.text,
                                  parsed: scraped.parsed,
                                  productName: userProductName.trim()
                              }
                            : it
                    )
                )
                console.log('✅ Product data from Amazon/BigBasket scrapers')
                return
            }

            setItems((prev) =>
                prev.map((it) =>
                    it.id === id
                        ? {
                              ...it,
                              status: 'error',
                              progress: 0,
                              error: scraped.message
                          }
                        : it
                )
            )
            return
        } catch (err: any) {
            const msg = err?.message || String(err) || 'Marketplace lookup failed'
            console.error('Marketplace lookup error', err)
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
                    brand: it.parsed?.brand,
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
                    brand: (typeof it.parsed?.brand === 'string' ? it.parsed.brand : null) || payload.brand || null,
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
                                    <div style={{ fontWeight: 700, fontSize: '1.25rem', marginBottom: 8, color: '#1a1a1a' }}>Thank you for contributing to our community</div>
                                    <div style={{ fontSize: 14, color: '#333' }}>We’ve received your contribution — it will appear after review.</div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ display: showThankYou ? 'none' : 'block' }}>
                            <h2 style={{ margin: 0, marginBottom: 12, color: '#1a1a1a' }}>Upload Files</h2>
                            <p style={{ marginTop: 0, marginBottom: 18, color: '#333' }}>Upload your user-downloadable files.</p>

                            <div
                                onDrop={onDrop}
                                onDragOver={onDragOver}
                                style={{ borderRadius: 12, background: '#f6f6f6', padding: 28, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}
                            >
                                <div style={{ width: 64, height: 64, borderRadius: 12, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 6px 18px rgba(0,0,0,0.03)' }}>
                                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 16V8" stroke="#444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /><path d="M8 12l4-4 4 4" stroke="#444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /><path d="M21 15v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2" stroke="#444" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                                </div>
                                <div style={{ fontSize: 16, fontWeight: 600, color: '#1a1a1a' }}>Drop your files here or browse</div>
                                <div style={{ fontSize: 12, color: '#444' }}>Max file size up to 1 GB</div>
                                <div style={{ marginTop: 8 }}>
                                    <input ref={browseInputRef} id="browse-files-input" type="file" accept="image/*,application/pdf" multiple onChange={onFiles} style={{ display: 'none' }} />
                                    <button onClick={() => browseInputRef.current?.click()} style={{ marginTop: 8, padding: '8px 14px', borderRadius: 10, background: '#fff', border: '1px solid #eee', color: '#1a1a1a' }}>Browse files</button>
                                </div>
                            </div>

                            <div style={{ marginTop: 18 }}>
                                {items.length === 0 && (
                                    <div style={{ padding: 18, borderRadius: 12, background: '#fff', border: '1px solid #f0f0f0', textAlign: 'center', color: '#555' }}>No files uploaded yet.</div>
                                )}

                                {items.map((it) => (
                                    <div key={it.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', background: '#fff', borderRadius: 10, marginTop: 12, border: '1px solid #f0f0f0' }}>
                                        {it.uploadedAndSaved ? (
                                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', padding: '12px 0' }}>
                                                <img src="/thankyou.jpeg" alt="thankyou" style={{ width: 120, height: 120, objectFit: 'cover', borderRadius: 12, marginBottom: 12 }} />
                                                <div style={{ textAlign: 'center' }}>
                                                    <div style={{ fontWeight: 700, color: '#1a1a1a' }}>Thank you for contributing to our community</div>
                                                    <div style={{ fontSize: 13, color: '#333', marginTop: 6 }}>We’ve received your contribution — it will appear after review.</div>
                                                </div>
                                            </div>
                                        ) : (
                                            <>
                                                <div style={{ width: 44, height: 44, borderRadius: 8, background: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, color: '#1a1a1a' }}>{it.name.split('.').pop()?.toUpperCase() || 'IMG'}</div>
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                        <div style={{ fontWeight: 600, color: '#1a1a1a' }}>{it.name}</div>
                                                        <div style={{ fontSize: 12, color: '#555' }}>{humanSize(it.size || 0)}</div>
                                                    </div>

                                                    <div style={{ marginTop: 8 }}>
                                                        <div style={{ height: 8, background: '#eee', borderRadius: 8, overflow: 'hidden' }}>
                                                            <div style={{ width: `${it.progress}%`, height: '100%', background: '#e27575', transition: 'width 300ms' }} />
                                                        </div>
                                                    </div>
                                                    <div style={{ marginTop: 8 }}>
                                                        <label htmlFor={`product-name-${it.id}`} style={{ display: 'block', fontSize: 12, fontWeight: 600, color: '#1a1a1a', marginBottom: 4 }}>Product name</label>
                                                        <input
                                                            id={`product-name-${it.id}`}
                                                            type="text"
                                                            placeholder="e.g. Britannia Marie Gold 200g"
                                                            disabled={it.status === 'processing'}
                                                            value={it.productName ?? (it.parsed?.product_name || it.name?.replace(/\.[^/.]+$/, '') || '')}
                                                            onChange={(e) => setItems(prev => prev.map(x => x.id === it.id ? { ...x, productName: e.target.value } : x))}
                                                            style={{ width: '100%', padding: '8px 10px', borderRadius: 8, border: '1px solid #eee', fontSize: 14, color: '#1a1a1a' }}
                                                        />
                                                    </div>
                                                    {it.status === 'error' && it.error && (
                                                        <div style={{ marginTop: 8, fontSize: 13, color: '#c44' }}>{it.error}</div>
                                                    )}
                                                    {it.parsed && it.status === 'done' && (
                                                        <>
                                                            <div style={{ marginTop: 10, fontSize: 12, fontWeight: 600, color: '#1a1a1a' }}>
                                                                {it.parsed.source ? `Source: ${it.parsed.source}` : 'Product details'}
                                                                {it.parsed.product_url && (
                                                                    <a href={it.parsed.product_url} target="_blank" rel="noreferrer" style={{ marginLeft: 8, fontWeight: 500, color: '#1a1a1a', textDecoration: 'underline' }}>View product page</a>
                                                                )}
                                                            </div>
                                                            {it.parsed.brand && <div style={{ marginTop: 4, fontSize: 12, color: '#333' }}>Brand: {it.parsed.brand}</div>}
                                                            {it.parsed.description && (
                                                                <p style={{ marginTop: 6, fontSize: 12, color: '#333', lineHeight: 1.45 }}>{String(it.parsed.description).slice(0, 400)}{String(it.parsed.description).length > 400 ? '…' : ''}</p>
                                                            )}
                                                            {Array.isArray(it.parsed.features) && it.parsed.features.length > 0 && (
                                                                <ul style={{ margin: '8px 0 0', paddingLeft: 18, fontSize: 12, color: '#333' }}>
                                                                    {it.parsed.features.slice(0, 8).map((f: string, i: number) => (
                                                                        <li key={i}>{f}</li>
                                                                    ))}
                                                                </ul>
                                                            )}
                                                            {it.parsed.specifications && typeof it.parsed.specifications === 'object' && Object.keys(it.parsed.specifications).length > 0 && (
                                                                <div style={{ marginTop: 8, fontSize: 11, color: '#333' }}>
                                                                    {Object.entries(it.parsed.specifications as Record<string, string>).slice(0, 12).map(([k, v]) => (
                                                                        <div key={k}><strong style={{ color: '#1a1a1a' }}>{k}:</strong> {v}</div>
                                                                    ))}
                                                                </div>
                                                            )}
                                                            {it.parsed.scrape_note && <div style={{ marginTop: 6, fontSize: 11, color: '#555' }}>{it.parsed.scrape_note}</div>}
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
