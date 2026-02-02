const functions = require('firebase-functions')
const admin = require('firebase-admin')
const { ImageAnnotatorClient } = require('@google-cloud/vision')
const fetch = require('node-fetch')
const os = require('os')
const path = require('path')
const fs = require('fs')

admin.initializeApp()
const visionClient = new ImageAnnotatorClient()

function parseNutritionFromText(text) {
    const findValue = (keys) => {
        for (const k of keys) {
            const re = new RegExp(k + "\\s*[:\\-]?\\s*(\\d+(?:\\.\\d+)?)\\s*(g|mg|kcal|cal)?", 'i')
            const m = text.match(re)
            if (m) return { value: parseFloat(m[1]), unit: m[2] || '' }
        }
        return null
    }

    const protein = findValue(['protein'])
    const fat = findValue(['fat', 'total fat', 'lipid'])
    const carbs = findValue(['carbohydrate', 'carbs'])
    const sugar = findValue(['sugar', 'sugars'])
    const calories = findValue(['calories', 'energy', 'kcal'])

    const parsed = {}
    if (protein) parsed.protein = protein.value
    if (fat) parsed.fat = fat.value
    if (carbs) parsed.carbs = carbs.value
    if (sugar) parsed.sugar = sugar.value
    if (calories) parsed.calories = calories.value

    const categories = []
    const p = protein?.value || 0
    const f = fat?.value || 0
    const s = sugar?.value || 0
    if (p >= 10) categories.push('High protein')
    if (f >= 17.5) categories.push('High fat')
    if (s >= 22.5) categories.push('High sugar')
    if (categories.length) parsed.categories = categories

    return parsed
}

exports.processImage = functions.storage.object().onFinalize(async (object) => {
    const contentType = object.contentType || ''
    if (!contentType.startsWith('image/')) {
        console.log('Not an image, skipping:', contentType)
        return null
    }

    const bucket = admin.storage().bucket(object.bucket)
    const filePath = object.name
    const fileName = path.basename(filePath)
    const tempFilePath = path.join(os.tmpdir(), fileName)

    console.log('Downloading', filePath, 'to', tempFilePath)
    await bucket.file(filePath).download({ destination: tempFilePath })

    let text = ''
    try {
        const [result] = await visionClient.textDetection(tempFilePath)
        text = result.fullTextAnnotation?.text || ''
    } catch (err) {
        console.error('Vision error', err)
    }

    // try to find barcode-like number in OCR text
    const barcodeMatch = text.match(/\b(\d{12,13})\b/)
    let ofProduct = null
    if (barcodeMatch) {
        const barcode = barcodeMatch[1]
        try {
            const res = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`)
            const j = await res.json()
            if (j && j.status === 1) ofProduct = j.product
        } catch (e) {
            console.warn('OpenFoodFacts lookup failed', e)
        }
    }

    const parsed = parseNutritionFromText(text)

    const doc = {
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        sourceBucket: object.bucket,
        sourcePath: filePath,
        fileName,
        text,
        parsed,
        source: ofProduct ? 'openfoodfacts' : 'vision'
    }

    if (ofProduct) {
        doc.product = {
            product_name: ofProduct.product_name || null,
            brands: ofProduct.brands || null,
            nutriments: ofProduct.nutriments || null,
            code: ofProduct.code || null
        }
    }

    await admin.firestore().collection('products').add(doc)

    try { fs.unlinkSync(tempFilePath) } catch (e) { /* ignore */ }

    console.log('Processed', filePath)
    return null
})
