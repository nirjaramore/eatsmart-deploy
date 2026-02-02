import type { NextApiRequest, NextApiResponse } from 'next'
import path from 'path'
import fs from 'fs'
import sharp from 'sharp'

function getContentType(ext: string) {
    const e = ext.toLowerCase()
    if (e === '.jpg' || e === '.jpeg') return 'image/jpeg'
    if (e === '.png') return 'image/png'
    if (e === '.webp') return 'image/webp'
    return 'application/octet-stream'
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    try {
        const { file, scale, width } = req.query
        if (!file || Array.isArray(file)) return res.status(400).send('missing file')

        const fileName = file as string
        const projectRoot = process.cwd()
        const assetDir = path.join(projectRoot, 'asset')
        const requested = path.join(assetDir, fileName)
        const normalized = path.normalize(requested)
        if (!normalized.startsWith(path.normalize(assetDir))) return res.status(403).send('forbidden')
        if (!fs.existsSync(normalized)) return res.status(404).send('not found')

        const ext = path.extname(normalized)
        // Basic safety limits
        const s = parseFloat(Array.isArray(scale) ? scale[0] : (scale as string || '1')) || 1
        const w = width ? parseInt(Array.isArray(width) ? width[0] : (width as string), 10) : undefined
        if (isNaN(s) || s <= 0 || s > 8) return res.status(400).send('invalid scale (0-8)')
        if (w !== undefined && (isNaN(w) || w <= 0 || w > 8000)) return res.status(400).send('invalid width')

        // Use sharp to read metadata and resize
        const image = sharp(normalized)
        const meta = await image.metadata()
        let targetWidth = w
        if (!targetWidth) targetWidth = Math.round((meta.width || 800) * s)

        const buffer = await image.resize({ width: targetWidth }).toBuffer()

        res.setHeader('Content-Type', getContentType(ext))
        res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate')
        res.status(200).send(buffer)
    } catch (err) {
        res.status(500).send('server error')
    }
}
