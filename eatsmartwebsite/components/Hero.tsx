import React from 'react'
import SiteHeader from './SiteHeader'

const Hero: React.FC = () => {
    /**
     * Hero image: eatsmartwebsite/public/asset/hero-background.png
     * Served as /asset/hero-background.png
     */
    const heroImageFileName = 'hero-background.png'
    const heroImageSrc = encodeURI(`/asset/${heroImageFileName}`)

    return (
        <section className="hero-root relative flex flex-col items-stretch" style={{ minHeight: '120vh', background: 'transparent', overflow: 'visible', position: 'relative', zIndex: 9999, paddingBottom: '6rem' }}>
            <SiteHeader active="home" />
            {/* Image anchored right; headline stacked on the left in 3 lines */}
            <div className="hero-stage">
                <img
                    className="hero-bg-media hero-stage__bg"
                    src={heroImageSrc}
                    alt="Nutrition label illustration"
                    decoding="async"
                />
                <div className="hero-headline-wrap">
                    <div className="hero-text-block">
                        <h1 className="hero-main-text hero-main-text--stacked">
                            <span className="hero-line">know</span>
                            <span className="hero-line">what you are</span>
                            <span className="hero-line">
                                <em>eating</em>
                            </span>
                        </h1>
                    </div>
                </div>
            </div>
        </section>
    )
}

export default Hero
