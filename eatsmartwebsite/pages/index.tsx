import Head from 'next/head'
import Hero from '../components/Hero'
import CurvedLoop from '../components/CurvedLoop'
import AutoZoomGallery from '../components/AutoZoomGallery'
import ScrollPinnedSection from '../components/ScrollPinnedSection'
import ImageUploadExtract from '../components/ImageUploadExtract'

export default function Home() {
    return (
        <>
            <Head>
                <title>EatSmart - Know what you are eating</title>
                <meta name="viewport" content="width=device-width, initial-scale=1" />
            </Head>
            <main>
                <Hero />

                {/* Second section: curved marquee placed below the hero so it is not behind the video */}
                <section aria-label="Join our community" style={{ position: 'relative', zIndex: 1, paddingTop: '2rem', paddingBottom: '4rem', background: 'transparent' }}>
                    <CurvedLoop marqueeText="Join our community" className="curved-loop-text" interactive />
                </section>

                {/* Third section: Image upload (placed above the auto-zoom gallery) */}
                <ImageUploadExtract />

                {/* Fourth section: GSAP auto-zoom bento gallery */}
                <AutoZoomGallery />

                {/* Fifth section: Scroll-pinned section with transitioning images */}
                <ScrollPinnedSection />

                {/* Firebase upload removed — using client-side OCR only (ImageUploadExtract) */}
            </main>
        </>
    )
}
