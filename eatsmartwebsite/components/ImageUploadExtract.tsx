import React, { useState, useRef, useEffect } from 'react'

type Item = {
    id: string
    name: string
    url: string
    status: 'idle' | 'processing' | 'done' | 'error'
    progress: number
    text: string
    error?: string
    parsed?: Record<string, number | string>
}

function parseNutrition(text: string) {
    // naive regex-based parser to extract common fields
    const findValue = (keys: string[]) => {
        for (const k of keys) {
            const re = new RegExp(k + '\\s*[:\\-]?\\s*(\\d+(?:\\.\\d+)?)\\s*(g|mg|kcal|cal)?', 'i')
            const m = text.match(re)
            if (m) return { value: parseFloat(m[1]), unit: m[2] || '' }
        }
        return null
    }

    const protein = findValue(['protein'])
    const fat = findValue(['fat', 'total fat', 'lipid'])
    const carbs = findValue(['carbohydrate', 'carbs', 'carbohydrate, total'])
    const sugar = findValue(['sugar', 'sugars'])
    const calories = findValue(['calories', 'energy', 'kcal'])

    const parsed: Record<string, number | string> = {}
    if (protein) parsed.protein = protein.value
    if (fat) parsed.fat = fat.value
    if (carbs) parsed.carbs = carbs.value
    if (sugar) parsed.sugar = sugar.value
    if (calories) parsed.calories = calories.value

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
    const [items, setItems] = useState<Item[]>([])
    const workerRef = useRef<any>(null)
    const processingIdRef = useRef<string | null>(null)

    useEffect(() => {
        return () => {
            // terminate worker on unmount
            if (workerRef.current) {
                try {
                    workerRef.current.terminate()
                } catch (e) {
                    // ignore
                }
                workerRef.current = null
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
            text: ''
        }))

        setItems((s) => [...newItems, ...s])

        // process files sequentially to avoid blocking
        for (let i = 0; i < files.length; i++) {
            const file = files[i]
            const itemId = newItems[i].id
            await processFile(file, itemId)
        }
    }

    const processFile = async (file: File, id: string) => {
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
                        const parsed = {
                            protein: prod.nutriments?.proteins_100g || null,
                            fat: prod.nutriments?.fat_100g || null,
                            carbs: prod.nutriments?.carbohydrates_100g || null,
                            sugar: prod.nutriments?.sugars_100g || null,
                            calories: prod.nutriments?.energy_kcal_100g || prod.nutriments?.energy_100g || null,
                            categories: []
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
            // create worker if necessary
            if (!workerRef.current) {
                const { createWorker } = await import('tesseract.js')
                const worker = createWorker({
                    logger: (m: any) => {
                        // map worker progress to current processing id
                        const pid = processingIdRef.current
                        if (pid && m && typeof m.progress === 'number') {
                            setItems((prev) => prev.map((it) => (it.id === pid ? { ...it, progress: Math.round(m.progress * 100) } : it)))
                        }
                    }
                })

                await worker.load()
                await worker.loadLanguage('eng')
                await worker.initialize('eng')
                workerRef.current = worker
            }

            const worker = workerRef.current
            processingIdRef.current = id

            // preprocess image to improve OCR: scale and increase contrast
            const processedBlob = await preprocessImageForOCR(file)
            const { data } = await worker.recognize(processedBlob)

            const text = data?.text || ''
            const parsed = parseNutrition(text)

            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'done', progress: 100, text, parsed } : it)))
        } catch (err: any) {
            setItems((prev) => prev.map((it) => (it.id === id ? { ...it, status: 'error', error: err?.message || 'OCR failed' } : it)))
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
            // use a non-literal dynamic import to avoid Next.js static resolution
            const libName = '@zxing/library'
            const mod: any = await import(libName)
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
                const result = reader.decodeFromImageElement(img)
                if (result) return result.getText()
            } catch (err) {
                // no barcode
            } finally {
                URL.revokeObjectURL(url)
            }
        } catch (e) {
            // ignore
        }

        return null
    }

    async function preprocessImageForOCR(file: File): Promise<Blob> {
        return new Promise((resolve) => {
            const img = new Image()
            img.onload = () => {
                const canvas = document.createElement('canvas')
                // upscale to width 1600 for better OCR
                const targetW = 1600
                const scale = Math.max(1, targetW / img.width)
                canvas.width = Math.round(img.width * scale)
                canvas.height = Math.round(img.height * scale)
                const ctx = canvas.getContext('2d')!
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height)
                // basic contrast/brightness adjustment
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
                const d = imageData.data
                for (let i = 0; i < d.length; i += 4) {
                    // convert to grayscale
                    const r = d[i], g = d[i + 1], b = d[i + 2]
                    let v = 0.299 * r + 0.587 * g + 0.114 * b
                    // increase contrast
                    v = ((v - 128) * 1.2) + 128
                    d[i] = d[i + 1] = d[i + 2] = Math.max(0, Math.min(255, v))
                }
                ctx.putImageData(imageData, 0, 0)
                canvas.toBlob((blob) => {
                    if (blob) resolve(blob)
                    else resolve(file)
                }, 'image/png')
            }
            img.onerror = () => resolve(file)
            img.src = URL.createObjectURL(file)
        })
    }

    const saveItem = (it: Item) => {
        const stored = JSON.parse(localStorage.getItem('eatsmart_products') || '[]')
        const payload = { id: it.id, name: it.name, text: it.text, parsed: it.parsed || {}, url: it.url, savedAt: new Date().toISOString() }
        stored.push(payload)
        localStorage.setItem('eatsmart_products', JSON.stringify(stored))
        alert('Saved to local products (localStorage). Later we can sync to backend/community page.')
    }

    const clearAll = () => {
        setItems([])
    }

    return (
        <section aria-label="Upload nutrition labels" style={{ padding: '2.5rem', background: '#fff' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                <h2 style={{ margin: 0 }}>Upload nutrition label (back of package)</h2>
                <div>
                    <input type="file" accept="image/*" multiple onChange={onFiles} />
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
                {items.length === 0 && (
                    <div style={{ padding: 24, borderRadius: 12, background: '#fafafa', gridColumn: '1/-1' }}>No images uploaded yet.</div>
                )}

                {items.map((it) => (
                    <div key={it.id} style={{ padding: 12, borderRadius: 12, background: '#fff', boxShadow: '0 6px 18px rgba(0,0,0,0.06)' }}>
                        <div style={{ display: 'flex', gap: 12 }}>
                            <img src={it.url} alt={it.name} style={{ width: 110, height: 110, objectFit: 'cover', borderRadius: 8 }} />
                            <div style={{ flex: 1 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <strong>{it.name}</strong>
                                    <span style={{ fontSize: 12, color: '#666' }}>{it.status}</span>
                                </div>

                                <div style={{ height: 8, background: '#eee', borderRadius: 8, marginTop: 8, overflow: 'hidden' }}>
                                    <div style={{ width: `${it.progress}%`, height: '100%', background: '#E53A33' }} />
                                </div>

                                <div style={{ marginTop: 8, display: 'flex', gap: 8 }}>
                                    <button disabled={it.status !== 'done'} onClick={() => saveItem(it)} style={{ padding: '6px 10px', borderRadius: 8, background: '#E53A33', color: '#fff', border: 'none' }}>Save</button>
                                    <button onClick={() => setItems((prev) => prev.filter((x) => x.id !== it.id))} style={{ padding: '6px 10px', borderRadius: 8, background: '#eee', border: 'none' }}>Remove</button>
                                </div>
                            </div>
                        </div>

                        <details style={{ marginTop: 12 }}>
                            <summary style={{ cursor: 'pointer' }}>View extracted text and parsed data</summary>
                            <pre style={{ whiteSpace: 'pre-wrap', marginTop: 8 }}>{it.text || '—'}</pre>
                            {it.parsed && (
                                <div style={{ marginTop: 8 }}>
                                    <strong>Parsed:</strong>
                                    <div style={{ fontSize: 13, marginTop: 4 }}>
                                        {Object.entries(it.parsed).map(([k, v]) => (
                                            <div key={k}>{k}: {String(v)}</div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </details>
                    </div>
                ))}
            </div>

            {items.length > 0 && (
                <div style={{ marginTop: 16, display: 'flex', gap: 8 }}>
                    <button onClick={() => {
                        // save all done items
                        const done = items.filter((i) => i.status === 'done')
                        const stored = JSON.parse(localStorage.getItem('eatsmart_products') || '[]')
                        const payloads = done.map((it) => ({ id: it.id, name: it.name, text: it.text, parsed: it.parsed || {}, url: it.url, savedAt: new Date().toISOString() }))
                        localStorage.setItem('eatsmart_products', JSON.stringify([...stored, ...payloads]))
                        alert(`Saved ${payloads.length} items to local products.`)
                    }} style={{ padding: '8px 12px', borderRadius: 8, background: '#0b85ff', color: '#fff', border: 'none' }}>Save all done</button>

                    <button onClick={clearAll} style={{ padding: '8px 12px', borderRadius: 8, background: '#eee', border: 'none' }}>Clear all</button>
                </div>
            )}
        </section>
    )
}
