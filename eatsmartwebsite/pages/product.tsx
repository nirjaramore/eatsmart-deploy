import Head from 'next/head'
import { useState, useEffect } from 'react'
import ProductCard from '../components/ProductCard'
import SiteHeader from '../components/SiteHeader'
import styles from '../styles/ProductsPage.module.css'

/* ===============================
   API BASE URL (PRODUCTION)
   =============================== */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'https://eatsmart-backend-je3d.onrender.com'

const SUPABASE_PUBLIC_URL =
  process.env.NEXT_PUBLIC_SUPABASE_URL ||
  'https://reqfxmbjbfzhxvufrpsr.supabase.co'

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

/* ===============================
   IMAGE NORMALIZER
   =============================== */
function normalizeImageUrl(
  rawImageUrl: string | undefined
): string | undefined {
  if (!rawImageUrl) return undefined
  const trimmed = rawImageUrl.trim()
  if (!trimmed) return undefined

  if (trimmed.startsWith('http')) return encodeURI(trimmed)

  if (trimmed.startsWith('/storage/v1/object/public/')) {
    return encodeURI(`${SUPABASE_PUBLIC_URL}${trimmed}`)
  }

  if (trimmed.startsWith('storage/v1/object/public/')) {
    return encodeURI(`${SUPABASE_PUBLIC_URL}/${trimmed}`)
  }

  if (!trimmed.includes('://') && /^[a-z0-9_-]+\//i.test(trimmed)) {
    return encodeURI(
      `${SUPABASE_PUBLIC_URL}/storage/v1/object/public/${trimmed}`
    )
  }

  return encodeURI(trimmed)
}

/* ===============================
   HELPERS
   =============================== */
function mapProductRow(r: any): ProductItem {
  return {
    id: `p-${r.id}`,
    barcode: r.barcode,
    product_name: r.product_name,
    brand: r.brand,
    image_url: r.image_url,
    is_verified: r.is_verified,
    created_at: r.created_at,
    uploaded_at: r.updated_at || r.created_at,
  }
}

function mapFoodImageRow(r: any): ProductItem {
  return {
    id: `fi-${r.id}`,
    barcode: r.barcode,
    product_name: r.product_name,
    image_url: r.image_url,
    image_type: r.image_type,
    uploaded_at: r.uploaded_at,
  }
}

function dedupeProducts(items: ProductItem[]): ProductItem[] {
  const map = new Map<string, ProductItem>()

  for (const item of items) {
    const key = item.barcode || item.product_name
    const existing = map.get(key)

    if (!existing || new Date(item.uploaded_at || 0) > new Date(existing.uploaded_at || 0)) {
      map.set(key, item)
    }
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
      p.product_name?.toLowerCase().includes(q) ||
      p.brand?.toLowerCase().includes(q) ||
      p.barcode?.includes(query)
    )

    setFilteredProducts(filtered)
  }, [query, products])

  /* ===============================
     FETCH (FIXED)
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

      const mapped = [
        ...prodJson.products.map(mapProductRow),
        ...foodJson.products.map(mapFoodImageRow),
      ]

      const deduped = dedupeProducts(mapped)

      const enriched = deduped.map(p => ({
        ...p,
        image_url: normalizeImageUrl(p.image_url),
      }))

      setProducts(enriched)
      setFilteredProducts(enriched)
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

        <section className={styles.productsHero}>
          <h1>Discover Healthy Products</h1>
        </section>

        <section>
          <input
            placeholder="Search..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
        </section>

        <section>
          {loading ? (
            <p>Loading...</p>
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