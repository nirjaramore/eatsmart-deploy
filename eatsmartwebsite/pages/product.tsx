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
const SUPABASE_PUBLIC_URL = (
  process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://reqfxmbjbfzhxvufrpsr.supabase.co'
).replace(/\/$/, '')
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

/** Resolve Supabase storage URLs and relative paths from the DB */
function normalizeImageUrl(
  rawImageUrl: string | undefined,
  opts: { supabaseUrl: string; apiBase: string }
): string | undefined {
  if (!rawImageUrl) return undefined
  const trimmed = rawImageUrl.trim()
  if (!trimmed) return undefined

  const { supabaseUrl, apiBase } = opts

  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return encodeURI(trimmed)
  }

  if (trimmed.startsWith('//')) {
    return encodeURI(`https:${trimmed}`)
  }

  if (trimmed.startsWith('/storage/v1/object/public/')) {
    return encodeURI(`${supabaseUrl}${trimmed}`)
  }

  if (trimmed.startsWith('storage/v1/object/public/')) {
    return encodeURI(`${supabaseUrl}/${trimmed}`)
  }

  if (trimmed.startsWith('/static/') || trimmed.startsWith('static/')) {
    const resolved = trimmed.startsWith('/')
      ? `${apiBase}${trimmed}`
      : `${apiBase}/${trimmed}`
    return encodeURI(resolved)
  }

  /* Bucket-relative path stored in Supabase (e.g. eatsmart/photo.webp) */
  if (!trimmed.includes('://') && /^[a-z0-9_-]+\//i.test(trimmed)) {
    return encodeURI(`${supabaseUrl}/storage/v1/object/public/${trimmed}`)
  }

  return encodeURI(trimmed)
}

function mapProductRow(r: Record<string, unknown>): ProductItem {
  const id = String(r.id ?? '')
  return {
    id: `p-${id}`,
    barcode: r.barcode != null ? String(r.barcode) : undefined,
    product_name: String(r.product_name ?? 'Product'),
    brand: r.brand != null ? String(r.brand) : undefined,
    manufacturer: r.manufacturer != null ? String(r.manufacturer) : undefined,
    region: r.region != null ? String(r.region) : undefined,
    weight: r.weight != null ? String(r.weight) : undefined,
    fssai_license: r.fssai_license != null ? String(r.fssai_license) : undefined,
    image_url: r.image_url != null ? String(r.image_url) : undefined,
    is_verified: Boolean(r.is_verified),
    created_at: r.created_at != null ? String(r.created_at) : undefined,
    uploaded_at:
      r.updated_at != null
        ? String(r.updated_at)
        : r.created_at != null
          ? String(r.created_at)
          : undefined,
  }
}

/** `food_images` table (legacy catalog + extra shots) */
function mapFoodImageRow(r: Record<string, unknown>): ProductItem {
  const id = String(r.id ?? '')
  return {
    id: `fi-${id}`,
    barcode: r.barcode != null ? String(r.barcode) : undefined,
    product_name: String(r.product_name ?? r.alt_text ?? 'Product'),
    image_url: r.image_url != null ? String(r.image_url) : undefined,
    image_type: r.image_type != null ? String(r.image_type) : undefined,
    uploaded_at: r.uploaded_at != null ? String(r.uploaded_at) : undefined,
  }
}

/** Stable key so "123" and 123 match; trims whitespace */
function barcodeKey(barcode?: string | null) {
  if (barcode == null || String(barcode).trim() === '') return ''
  return String(barcode).trim()
}

function rowTimestamp(p: ProductItem) {
  return new Date(p.uploaded_at || p.created_at || 0).getTime()
}

/**
 * One card per product: `/save-product-complete` writes to `products` only.
 * If the DB has duplicate rows (same barcode or same name with no barcode), keep the newest row.
 */
function dedupeProductsFromDb(items: ProductItem[]): ProductItem[] {
  const byBarcode = new Map<string, ProductItem>()
  const byNameKey = new Map<string, ProductItem>()

  for (const p of items) {
    const bk = barcodeKey(p.barcode)
    if (bk) {
      const existing = byBarcode.get(bk)
      if (!existing || rowTimestamp(p) >= rowTimestamp(existing)) {
        byBarcode.set(bk, p)
      }
      continue
    }

    const nk = (p.product_name || '').trim().toLowerCase()
    if (!nk) continue
    const existing = byNameKey.get(nk)
    if (!existing || rowTimestamp(p) >= rowTimestamp(existing)) {
      byNameKey.set(nk, p)
    }
  }

  return [...byBarcode.values(), ...byNameKey.values()]
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
     FETCH — `products` (uploads/Save) + `food_images` (original catalog)
     =============================== */
  const imgOpts = {
    supabaseUrl: SUPABASE_PUBLIC_URL,
    apiBase: API_BASE_URL,
  }

  const normalizeProductUrls = (items: ProductItem[]) =>
    items.map(product => ({
      ...product,
      image_url: normalizeImageUrl(product.image_url, imgOpts),
    }))

  const fetchProducts = async () => {
    setLoading(true)

    try {
      for (const baseUrl of API_CANDIDATE_BASES) {
        try {
          const [prodRes, foodRes] = await Promise.all([
            fetch(`${baseUrl}/products?limit=500`),
            fetch(`${baseUrl}/food-images?limit=500`),
          ])

          const prodJson: ProductsResponse = prodRes.ok
            ? await prodRes.json()
            : { products: [], total: 0 }
          const foodJson: ProductsResponse = foodRes.ok
            ? await foodRes.json()
            : { products: [], total: 0 }

          const prodRows = (prodJson.products || []) as Record<string, unknown>[]
          const foodRows = (foodJson.products || []) as Record<string, unknown>[]

          if (prodRows.length || foodRows.length) {
            const mapped = [
              ...prodRows.map(mapProductRow),
              ...foodRows.map(mapFoodImageRow),
            ]
            const deduped = dedupeProductsFromDb(mapped)
            const enriched = normalizeProductUrls(deduped)

            setProducts(enriched)
            setFilteredProducts(enriched)
            setTotal(enriched.length)
            return
          }
        } catch {
          /* try next API base */
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
        const [prodRes, foodRes] = await Promise.all([
          fetch(`${baseUrl}/products?limit=500`),
          fetch(`${baseUrl}/food-images?limit=500`),
        ])

        if (prodRes.ok || foodRes.ok) {
          const prodJson: ProductsResponse = prodRes.ok
            ? await prodRes.json()
            : { products: [], total: 0 }
          const foodJson: ProductsResponse = foodRes.ok
            ? await foodRes.json()
            : { products: [], total: 0 }

          const prodRows = (prodJson.products || []) as Record<string, unknown>[]
          const foodRows = (foodJson.products || []) as Record<string, unknown>[]

          if (prodRows.length || foodRows.length) {
            const mapped = [
              ...prodRows.map(mapProductRow),
              ...foodRows.map(mapFoodImageRow),
            ]
            const deduped = dedupeProductsFromDb(mapped)
            const enriched = normalizeProductUrls(deduped)

            setProducts(enriched)
            setFilteredProducts(enriched)
            setTotal(enriched.length)
            return
          }
        }
      } catch (err) {
        console.error(`Secondary fetch failed for ${baseUrl}`, err)
      }
    }

    // 🔁 LocalStorage fallback (offline / no API)
    const stored = JSON.parse(
      localStorage.getItem('eatsmart_products') || '[]'
    )

    const mapped = dedupeProductsFromDb(
      stored.map((s: any) => ({
        id: `p-${String(s.id)}`,
        product_name: s.name,
        barcode: s.barcode,
        image_url: s.url,
      }))
    )

    const enriched = normalizeProductUrls(mapped)
    setProducts(enriched)
    setFilteredProducts(enriched)
    setTotal(enriched.length)
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
