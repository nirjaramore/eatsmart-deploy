import Head from 'next/head'
import dynamic from 'next/dynamic'
import Hero from '../components/Hero'
import CurvedLoop from '../components/CurvedLoop'
// import AutoZoomGallery from '../components/AutoZoomGallery'
import ScrollPinnedSection from '../components/ScrollPinnedSection'

// 🔥 IMPORTANT: Disable SSR for this component
const ImageUploadExtract = dynamic(
  () => import('../components/ImageUploadExtract'),
  { ssr: false }
)

export default function Home() {
  return (
    <>
      <Head>
        <title>EatSmart - Know what you are eating</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main>
        <Hero />

        {/* Curved loop section */}
        <section
          aria-label="Join our community"
          style={{
            position: 'relative',
            zIndex: 1,
            paddingTop: '2rem',
            paddingBottom: '4rem',
            background: 'transparent'
          }}
        >
          <CurvedLoop
            marqueeText="Join our community"
            className="curved-loop-text"
            interactive
          />
        </section>

        {/* Upload Section (SSR disabled component) */}
        <section id="upload-section" aria-label="Upload product">
          <ImageUploadExtract />
        </section>

        {/* Scroll Section */}
        <ScrollPinnedSection />

        {/* What we offer */}
        <section
          aria-label="What we offer"
          className="what-we-offer"
          style={{
            backgroundImage: `url(${encodeURI('/asset/download (33).jpeg')})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            padding: '6rem 0',
            minHeight: '360px'
          }}
        />
      </main>
    </>
  )
}