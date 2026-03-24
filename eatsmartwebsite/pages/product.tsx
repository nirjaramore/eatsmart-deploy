import Head from 'next/head'
import { useState, useEffect } from 'react'
import ProductCard from '../components/ProductCard'
import SiteHeader from '../components/SiteHeader'
import styles from '../styles/ProductsPage.module.css'

/* ===============================
   API BASE URL (SAFE)
   =============================== */
const API_BASE_URL =
  (process.env.NEXT_PUBLIC_API_BASE_URL || '').replace(/\/$/, '')

const SUPABASE_PUBLIC_URL =
  process.env.NEXT_PUBLIC_SUPABASE_URL || ''

/* ===============================
   TYPES
   =============================== */
type ProductItem = {
  id: string
  barcode?: string
  product_name?: string
  brand?: string
  image_type?: string
  manufacturer?: string
  region?: string
  weight?: string
  image_url?: string
  is_verified?: boolean
  created_at?: string
  uploaded_at?: string
}

type ProductsResponse = {
  products: ProductItem[]
  total: number
}

/* ===============================
   IMAGE NORMALIZER
   =============================== */
function normalizeImageUrl(raw?: string): string | undefined {
  if (!raw) return undefined

  const trimmed = raw.trim()
  if (!trimmed) return undefined

  // already full URL
  if (trimmed.startsWith('http')) return trimmed

  // Supabase full path fix
  return `${SUPABASE_PUBLIC_URL}/storage/v1/object/public/${trimmed}`
}

/* ===============================
   HELPERS
   =============================== */
function mapProductRow(r: any): ProductItem {
  return {
    id: `p-${r.id}`,
    product_name: r.product_name,
    brand: r.brand,
    image_url: r.image_url,
    is_verified: r.is_verified,
    uploaded_at: r.updated_at || r.created_at,
  }
}

function mapFoodImageRow(r: any): ProductItem {
  return {
    id: `fi-${r.id}`,
    product_name: r.product_name,
    image_url: r.image_url,
    uploaded_at: r.uploaded_at,
  }
}

function dedupeProducts(items: ProductItem[]): ProductItem[] {
  const map = new Map<string, ProductItem>()

  for (const item of items) {
    const key = item.product_name || item.id
    map.set(key, item)
  }

  return Array.from(map.values())
}

/* ===============================
   COMPONENT
   =============================== */
export default function Product() {
  const [query, setQuery] = useState('')
  const [products, setProducts] = useState<ProductItem[]>([])
  const [filteredProducts, setFilteredProducts] = useState<ProductItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProducts()
  }, [])

  useEffect(() => {
    const q = query.toLowerCase()

    const filtered = products.filter(p =>
      p.product_name?.toLowerCase().includes(q)
    )

    setFilteredProducts(filtered)
  }, [query, products])

  /* ===============================
     FETCH (SAFE)
     =============================== */
  const fetchProducts = async () => {
    setLoading(true)

    try {
      const [prodRes, foodRes] = await Promise.all([
        fetch(`${API_BASE_URL}/products?limit=500`),
        fetch(`${API_BASE_URL}/food-images?limit=500`),
      ])

      const prodJson: ProductsResponse = prodRes.ok
        ? await prodRes.json()
        : { products: [], total: 0 }

      const foodJson: ProductsResponse = foodRes.ok
        ? await foodRes.json()
        : { products: [], total: 0 }

      const merged = [
        ...prodJson.products.map(mapProductRow),
        ...foodJson.products.map(mapFoodImageRow),
      ]

      const finalProducts = dedupeProducts(merged)
  .map(p => ({
    ...p,
    image_url: normalizeImageUrl(p.image_url),
  }))
  .filter(p => p.image_url && p.product_name !== 'Product')

      setProducts(finalProducts)
      setFilteredProducts(finalProducts)
    } catch (err) {
      console.error('Fetch failed', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Head>
        <title>Products - EatSmart</title>
      </Head>

      <main className={styles.productsMain}>
        <SiteHeader active="product" />

        {/* 🔥 FIXED HEADING STYLE */}
        <div style={{ marginTop: '24px', marginBottom: '24px' }}>
  <section className={styles.searchForm}>
    <div className={styles.searchWrapper}>
      <span className={styles.searchIcon}>🔍</span>

      <input
        className={styles.searchInput}
        placeholder="Search healthy products..."
        value={query}
        onChange={e => setQuery(e.target.value)}
      />
    </div>
  </section>
</div>

        {/* PRODUCTS */}
        <section>
          {loading ? (
            <p className={styles.loading}>Loading...</p>
          ) : (
            <div className={styles.productsGrid}>
              {filteredProducts.map(p => (
                <ProductCard key={p.id} {...p} />
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  )
}