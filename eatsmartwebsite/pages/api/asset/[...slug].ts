import { NextApiRequest, NextApiResponse } from 'next'
import fs from 'fs'
import path from 'path'

function getContentType(ext: string) {
    const e = ext.toLowerCase()
    if (e === '.jpg' || e === '.jpeg') return 'image/jpeg'
    if (e === '.png') return 'image/png'
    if (e === '.svg') return 'image/svg+xml'
    if (e === '.webp') return 'image/webp'
    return 'application/octet-stream'
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
    try {
        const slug = req.query.slug
        if (!slug) return res.status(400).end('missing file')

        // slug can be array when using [...slug]
        const parts = Array.isArray(slug) ? slug : [slug as string]

        // Build the safe path under the project's `asset` directory
        const projectRoot = process.cwd()
        const assetDir = path.join(projectRoot, 'asset')

        const requested = path.join(assetDir, ...parts)

        // Prevent path traversal: ensure requested starts with assetDir
        const normalized = path.normalize(requested)
        if (!normalized.startsWith(path.normalize(assetDir))) {
            return res.status(403).end('forbidden')
        }

        if (!fs.existsSync(normalized)) {
            return res.status(404).end('not found')
        }

        const stat = fs.statSync(normalized)
        if (!stat.isFile()) return res.status(404).end('not found')

        const ext = path.extname(normalized)
        res.setHeader('Content-Type', getContentType(ext))
        res.setHeader('Cache-Control', 'public, max-age=0, must-revalidate')

        const stream = fs.createReadStream(normalized)
        stream.pipe(res)
        stream.on('error', () => res.status(500).end('error'))
    } catch (err) {
        res.status(500).end('server error')
    }
}
