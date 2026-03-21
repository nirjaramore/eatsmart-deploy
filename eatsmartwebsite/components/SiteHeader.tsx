import Link from 'next/link'
import { useState } from 'react'

type SiteHeaderProps = {
  active?: 'home' | 'about' | 'product'
}

export default function SiteHeader({ active = 'home' }: SiteHeaderProps) {
  const [logoError, setLogoError] = useState(false)

  return (
    <header className="top-header" role="banner" style={{ zIndex: 11000 }}>
      <div className="top-brand">
        {!logoError ? (
          <img
            src="/asset/logo.png"
            alt="EatSmart logo"
            style={{ width: 56, height: 56, objectFit: 'contain', marginRight: 12 }}
            onError={() => setLogoError(true)}
          />
        ) : (
          <span
            aria-hidden="true"
            style={{
              width: 12,
              height: 12,
              borderRadius: 999,
              background: '#e27575',
              display: 'inline-block',
              marginRight: 8,
            }}
          />
        )}
        {logoError && <span>eatsmart</span>}
      </div>
      <nav className="top-nav">
        <Link href="/" className={`top-link ${active === 'home' ? 'active' : ''}`} data-text="Home">
          <span className="link-inner">Home</span>
        </Link>
        <Link href="/about" className={`top-link ${active === 'about' ? 'active' : ''}`} data-text="About Us">
          <span className="link-inner">About Us</span>
        </Link>
        <Link href="/product" className={`top-link ${active === 'product' ? 'active' : ''}`} data-text="Product">
          <span className="link-inner">Product</span>
        </Link>
        <Link href="/#upload-section" className="top-link" data-text="Upload Product">
          <span className="link-inner">Upload Product</span>
        </Link>
      </nav>
    </header>
  )
}
