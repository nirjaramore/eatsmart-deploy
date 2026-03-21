import React, { useState } from 'react'
import { uploadFileWithProgress, listenForProductBySourcePath } from '../lib/firebaseClient'

export default function FirebaseUploader() {
    const [uploading, setUploading] = useState(false)
    const [progress, setProgress] = useState(0)
    const [message, setMessage] = useState<string | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [productDocs, setProductDocs] = useState<any[]>([])

    const onFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return
        setMessage(null)
        setUploading(true)
        setProgress(0)
        const path = `uploads/${Date.now()}-${file.name}`
        try {
            const url = await uploadFileWithProgress(path, file, (p) => setProgress(p))
            setPreviewUrl(url)
            setMessage('Upload complete — waiting for server processing (Cloud Function).')

            // listen for product doc created by Cloud Function
            const unsub = listenForProductBySourcePath(path, (docs) => {
                setProductDocs(docs)
                if (docs.length) {
                    setMessage('Processing complete — product document available.')
                    unsub()
                    setUploading(false)
                }
            })
        } catch (err: any) {
            setMessage(err?.message || 'Upload failed')
            setUploading(false)
        }
    }

    return (
        <section style={{ padding: 24, background: '#fff' }}>
            <h2 style={{ marginTop: 0 }}>Upload (Firebase Storage → Cloud Function)</h2>
            <input type="file" accept="image/*" onChange={onFile} />

            <div style={{ marginTop: 12 }}>
                {uploading && <div>Uploading: {progress}%</div>}
                {previewUrl && <img src={previewUrl} alt="preview" style={{ width: 140, marginTop: 12, borderRadius: 8 }} />}
                {message && <div style={{ marginTop: 8 }}>{message}</div>}
            </div>

            {productDocs.length > 0 && (
                <div style={{ marginTop: 12 }}>
                    <h3>Product documents</h3>
                    {productDocs.map((d) => (
                        <div key={d.id} style={{ padding: 8, border: '1px solid #eee', borderRadius: 8, marginBottom: 8 }}>
                            <div><strong>{d.product?.product_name || d.fileName || 'Unnamed'}</strong></div>
                            <div style={{ fontSize: 13, color: '#eca6a4' }}>{d.source}</div>
                            <pre style={{ whiteSpace: 'pre-wrap' }}>{d.text}</pre>
                            {d.parsed && (
                                <div>
                                    <strong>Parsed:</strong>
                                    <div>{Object.entries(d.parsed).map(([k, v]) => <div key={k}>{k}: {String(v)}</div>)}</div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </section>
    )
}
