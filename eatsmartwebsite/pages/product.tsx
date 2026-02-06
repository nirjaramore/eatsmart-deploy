import Head from 'next/head'
import { useState, useEffect } from 'react'

type ProductItem = {
    id: string
    barcode?: string
    product_name: string
    brand?: string
    image_url?: string
    created_at?: string
}

export default function Product() {
    const [query, setQuery] = useState('')
    const [products, setProducts] = useState<ProductItem[]>([])

    useEffect(() => {
        // Fetch from backend, fall back to localStorage
        (async () => {
            try {
                const res = await fetch('http://localhost:3000/products')
                if (res.ok) {
                    const j = await res.json()
                    if (j && Array.isArray(j.products)) {
                        setProducts(j.products)
                        return
                    }
                }
            } catch (e) {
                // ignore
            }

            // Fallback: read localStorage
            const stored = JSON.parse(localStorage.getItem('eatsmart_products') || '[]')
            const mapped = stored.map((s: any) => ({ id: s.id, product_name: s.name, image_url: s.url }))
            setProducts(mapped)
        })()
    }, [])

    const onSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        alert(`Search for: ${query}`)
    }

    return (
        <>
            <Head>
                <title>Product - EatSmart</title>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
            </Head>

            <main style={{ minHeight: '100vh', background: 'var(--brand-bg)' }}>
                <section className="product-hero">
                    <div className="product-hero-inner">
                        <h1 className="product-title">A Curated List For Products</h1>
                        <p className="product-sub">Search India-friendly packaged products and discover nutrition details.</p>

                        <form className="product-search" onSubmit={onSubmit} role="search">
                            <button type="submit" className="product-search-button" aria-label="Search">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
                                    <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2" />
                                    <path d="M21 21l-4.35-4.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                            </button>
                            <input
                                className="product-search-input"
                                placeholder="Search products, brands or barcodes"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                aria-label="Search products"
                            />
                        </form>

                        <div style={{ marginTop: 24 }}>
                            {products.length === 0 && <div>No products yet.</div>}
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 12, marginTop: 12 }}>
                                {products.map((p) => (
                                    <div key={p.id} style={{ padding: 12, borderRadius: 8, background: '#fff' }}>
                                        <img src={p.image_url || '/placeholder.png'} alt={p.product_name} style={{ width: '100%', height: 140, objectFit: 'cover', borderRadius: 6 }} />
                                        <h3 style={{ margin: '8px 0 4px' }}>{p.product_name}</h3>
                                        <div style={{ fontSize: 13, color: '#666' }}>{p.brand}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </>
    )
}
