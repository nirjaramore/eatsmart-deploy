import { useState } from 'react'
import styles from './ProductCard.module.css'

type ProductCardProps = {
    id: string
    barcode?: string
    product_name: string
    brand?: string
    manufacturer?: string
    region?: string
    weight?: string
    image_url?: string
    is_verified?: boolean
    created_at?: string
}

export default function ProductCard({
    product_name,
    brand,
    manufacturer,
    region,
    weight,
    image_url,
    is_verified,
    barcode
}: ProductCardProps) {
    const [imageError, setImageError] = useState(false)
    const [imageLoading, setImageLoading] = useState(true)

    const handleImageError = () => {
        setImageError(true)
        setImageLoading(false)
    }

    const handleImageLoad = () => {
        setImageLoading(false)
    }

    const displayImage = imageError || !image_url
        ? '/asset/placeholder.svg'
        : image_url

    return (
        <div className={styles.productCard}>
            <div className={styles.imageWrapper}>
                {imageLoading && !imageError && (
                    <div className={styles.imagePlaceholder}>
                        <div className={styles.imageLoader}></div>
                    </div>
                )}
                <img
                    src={displayImage}
                    alt={product_name}
                    className={`${styles.productImage} ${imageLoading ? styles.imageHidden : ''}`}
                    onError={handleImageError}
                    onLoad={handleImageLoad}
                    loading="lazy"
                />
                {is_verified && (
                    <div className={styles.verifiedBadge} title="Verified Product">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                )}
                {region && (
                    <div className={styles.regionBadge}>
                        {region}
                    </div>
                )}
            </div>

            <div className={styles.productInfo}>
                <h3 className={styles.productName}>{product_name}</h3>
            </div>
        </div>
    )
}
