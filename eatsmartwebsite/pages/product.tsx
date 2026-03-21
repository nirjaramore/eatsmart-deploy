import Head from 'next/head'
import { useState, useEffect } from 'react'
import ProductCard from '../components/ProductCard'
import SiteHeader from '../components/SiteHeader'
import styles from '../styles/ProductsPage.module.css'

/* ===============================
   API BASE URL (IMPORTANT FIX)
   =============================== */
const DEFAULT_API_BASE_URL = 'http://localhost:8007'
const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL || DEFAULT_API_BASE_URL
).replace(/\/$/, '')
const SUPABASE_PUBLIC_URL = 'https://reqfxmbjbfzhxvufrpsr.supabase.co'
const API_CANDIDATE_BASES = Array.from(
  new Set([
    API_BASE_URL,
    'http://localhost:8007',
    'http://localhost:8004',
    'http://localhost:8003',
    'http://localhost:8002',
    'http://localhost:8001',
    'http://localhost:8000',
  ])
)

/* ===============================
   MANUAL SUPABASE IMAGE MAPPING
   =============================== */
const MANUAL_IMAGE_MAP: Record<string, string> = {
  '8901063090637':
    'https://reqfxmbjbfzhxvufrpsr.supabase.co/storage/v1/object/public/eatsmart/Britannia%20Nutrichoice%20Digestive%20Zero_front.webp',
}

/* ===============================
   TYPES
   =============================== */
type ProductItem = {
  id: string
  barcode?: string
  product_name: string
  brand?: string
  image_type?: string
  manufacturer?: string
  region?: string
  weight?: string
  fssai_license?: string
  image_url?: string
  is_verified?: boolean
  created_at?: string
  uploaded_at?: string
}

type ProductsResponse = {
  products: ProductItem[]
  total: number
  regions?: string[]
  brands?: string[]
}

export default function Product() {
  const [query, setQuery] = useState('')
  const [products, setProducts] = useState<ProductItem[]>([])
  const [filteredProducts, setFilteredProducts] = useState<ProductItem[]>([])
  const [loading, setLoading] = useState(true)
  const [total, setTotal] = useState(0)
  const [brandFilter, setBrandFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [verifiedFilter, setVerifiedFilter] = useState<'all' | 'verified' | 'unverified'>('all')
  const [sortBy, setSortBy] = useState<'newest' | 'az' | 'relevant'>('newest')

  useEffect(() => {
    fetchProducts()
  }, [])

  useEffect(() => {
    let filtered = [...products]
    const lowerQuery = query.trim().toLowerCase()

    if (lowerQuery) {
      filtered = filtered.filter(
        p =>
          p.product_name?.toLowerCase().includes(lowerQuery) ||
          p.brand?.toLowerCase().includes(lowerQuery) ||
          p.barcode?.includes(query)
      )
    }

    if (brandFilter !== 'all') {
      filtered = filtered.filter(
        p => (p.brand || 'unknown').toLowerCase() === brandFilter
      )
    }

    if (typeFilter !== 'all') {
      filtered = filtered.filter(p => getDisplayType(p) === typeFilter)
    }

    if (verifiedFilter !== 'all') {
      const shouldBeVerified = verifiedFilter === 'verified'
      filtered = filtered.filter(p => Boolean(p.is_verified) === shouldBeVerified)
    }

    filtered.sort((a, b) => {
      if (sortBy === 'az') {
        return (a.product_name || '').localeCompare(b.product_name || '')
      }

      if (sortBy === 'relevant') {
        const score = (p: ProductItem) => {
          if (!lowerQuery) return 0
          const name = (p.product_name || '').toLowerCase()
          const brand = (p.brand || '').toLowerCase()
          if (name.startsWith(lowerQuery)) return 3
          if (name.includes(lowerQuery)) return 2
          if (brand.includes(lowerQuery)) return 1
          return 0
        }
        return score(b) - score(a)
      }

      const ad = new Date(a.uploaded_at || a.created_at || 0).getTime()
      const bd = new Date(b.uploaded_at || b.created_at || 0).getTime()
      return bd - ad
    })

    setFilteredProducts(filtered)
  }, [query, products, brandFilter, typeFilter, verifiedFilter, sortBy])

  const uniqueBrands = Array.from(
    new Set(products.map(p => (p.brand || 'unknown').toLowerCase()))
  ).sort((a, b) => a.localeCompare(b))

  const getDisplayType = (product: ProductItem) => {
    const rawType = (product.image_type || '').toLowerCase()
    if (rawType === 'front' || rawType === 'back') return rawType

    const name = (product.product_name || '').toLowerCase()
    const imageUrl = (product.image_url || '').toLowerCase()
    const combined = `${name} ${imageUrl}`

    if (combined.includes('_back') || combined.includes(' back')) return 'back'
    if (combined.includes('_front') || combined.includes(' front')) return 'front'
    if (rawType) return rawType
    return 'unknown'
  }

  const uniqueTypes = Array.from(
    new Set(products.map(getDisplayType))
  ).sort((a, b) => a.localeCompare(b))

  /* ===============================
     FETCH PRODUCTS
     =============================== */
  const fetchProducts = async () => {
    setLoading(true)

    try {
      for (const baseUrl of API_CANDIDATE_BASES) {
        const res = await fetch(`${baseUrl}/food-images?limit=200`)

        if (res.ok) {
          const data: ProductsResponse = await res.json()

          if (data.products?.length) {
            const enriched = await keepLoadableImages(attachManualImages(data.products))
            setProducts(enriched)
            setFilteredProducts(enriched)
            setTotal(data.total || 0)

            return
          }
        }
      }

      await fetchFromProductsTable()
    } catch (err) {
      console.error('Primary fetch failed', err)
      await fetchFromProductsTable()
    } finally {
      setLoading(false)
    }
  }

  /* ===============================
     FALLBACK FETCH
     =============================== */
  const fetchFromProductsTable = async () => {
    for (const baseUrl of API_CANDIDATE_BASES) {
      try {
        const res = await fetch(`${baseUrl}/products?limit=100`)

        if (res.ok) {
          const data: ProductsResponse = await res.json()
          const enriched = await keepLoadableImages(
            attachManualImages(data.products || [])
          )

          setProducts(enriched)
          setFilteredProducts(enriched)
          setTotal(data.total || 0)
          return
        }
      } catch (err) {
        console.error(`Secondary fetch failed for ${baseUrl}`, err)
      }
    }

    // 🔁 LocalStorage fallback
    const stored = JSON.parse(
      localStorage.getItem('eatsmart_products') || '[]'
    )

    const mapped = attachManualImages(
      stored.map((s: any) => ({
        id: s.id,
        product_name: s.name,
        barcode: s.barcode,
        image_url: s.url,
      }))
    )

    setProducts(mapped)
    setFilteredProducts(mapped)
  }

  /* ===============================
     IMAGE URL FIX
     =============================== */
  const normalizeImageUrl = (rawImageUrl?: string) => {
    if (!rawImageUrl) return undefined
    const trimmed = rawImageUrl.trim()
    if (!trimmed) return undefined

    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      return encodeURI(trimmed)
    }

    if (trimmed.startsWith('//')) {
      return encodeURI(`https:${trimmed}`)
    }

    if (trimmed.startsWith('/storage/v1/object/public/')) {
      return encodeURI(`${SUPABASE_PUBLIC_URL}${trimmed}`)
    }

    if (trimmed.startsWith('storage/v1/object/public/')) {
      return encodeURI(`${SUPABASE_PUBLIC_URL}/${trimmed}`)
    }

    if (trimmed.startsWith('/static/') || trimmed.startsWith('static/')) {
      const resolved = trimmed.startsWith('/')
        ? `${API_BASE_URL}${trimmed}`
        : `${API_BASE_URL}/${trimmed}`
      return encodeURI(resolved)
    }

    return encodeURI(trimmed)
  }

  const isImageLoadable = (url: string) =>
    new Promise<boolean>(resolve => {
      const img = new Image()
      const timeout = globalThis.setTimeout(() => resolve(false), 5000)
      img.onload = () => {
        globalThis.clearTimeout(timeout)
        resolve(true)
      }
      img.onerror = () => {
        globalThis.clearTimeout(timeout)
        resolve(false)
      }
      img.src = url
    })

  const keepLoadableImages = async (items: ProductItem[]) => {
    const checks = await Promise.all(
      items.map(async item => {
        if (!item.image_url) return false
        return isImageLoadable(item.image_url)
      })
    )

    return items.filter((_, idx) => checks[idx])
  }

  const attachManualImages = (items: ProductItem[]) => {
    return items.map(product => {
      const rawImageUrl =
        product.image_url ||
        (product.barcode ? MANUAL_IMAGE_MAP[product.barcode] : undefined)

      return {
        ...product,
        image_url: normalizeImageUrl(rawImageUrl),
      }
    })
  }

  return (
    <>
      <Head>
        <title>Products - EatSmart</title>
        <meta
          name="description"
          content="Browse healthy packaged food products"
        />
      </Head>

      <main className={styles.productsMain}>
        <SiteHeader active="product" />

        <section className={styles.productsHero}>
          <div className={styles.pageContainer}>
            <div className={styles.heroContent}>
              <h1 className={styles.heroTitle}>Discover Healthy Products</h1>
              <p className={styles.heroSubtitle}>
                Browse {total} verified food products
              </p>
            </div>
          </div>
        </section>

        <section className={styles.controlsSection}>
          <div className={styles.pageContainer}>
            <div className={styles.controlBar}>
              <input
                className={styles.searchInput}
                placeholder="Search by product, brand, or barcode..."
                value={query}
                onChange={e => setQuery(e.target.value)}
              />

              <select
                className={styles.controlSelect}
                value={brandFilter}
                onChange={e => setBrandFilter(e.target.value)}
                aria-label="Filter by brand"
              >
                <option value="all">All Brands</option>
                {uniqueBrands.map(brand => (
                  <option key={brand} value={brand}>
                    {brand === 'unknown' ? 'Unknown Brand' : brand}
                  </option>
                ))}
              </select>

              <select
                className={styles.controlSelect}
                value={typeFilter}
                onChange={e => setTypeFilter(e.target.value)}
                aria-label="Filter by type"
              >
                <option value="all">All Types</option>
                {uniqueTypes.map(type => (
                  <option key={type} value={type}>
                    {type === 'unknown' ? 'Unknown Type' : type}
                  </option>
                ))}
              </select>

              <div className={styles.chipGroup}>
                <button
                  type="button"
                  className={`${styles.chip} ${verifiedFilter === 'all' ? styles.chipActive : ''}`}
                  onClick={() => setVerifiedFilter('all')}
                >
                  All
                </button>
                <button
                  type="button"
                  className={`${styles.chip} ${verifiedFilter === 'verified' ? styles.chipActive : ''}`}
                  onClick={() => setVerifiedFilter('verified')}
                >
                  Verified
                </button>
                <button
                  type="button"
                  className={`${styles.chip} ${verifiedFilter === 'unverified' ? styles.chipActive : ''}`}
                  onClick={() => setVerifiedFilter('unverified')}
                >
                  Unverified
                </button>
              </div>

              <select
                className={styles.controlSelect}
                value={sortBy}
                onChange={e => setSortBy(e.target.value as 'newest' | 'az' | 'relevant')}
                aria-label="Sort products"
              >
                <option value="newest">Newest</option>
                <option value="az">A-Z</option>
                <option value="relevant">Most Relevant</option>
              </select>
            </div>

            <p className={styles.resultCount}>
              Showing {filteredProducts.length} of {products.length} products
            </p>
          </div>
        </section>

        <section className={styles.productsSection}>
          <div className={styles.pageContainer}>
            {loading ? (
              <p>Loading products...</p>
            ) : (
              <div className={styles.productsGrid}>
                {filteredProducts.map(product => (
                  <ProductCard key={product.id} {...product} />
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </>
  )
}
