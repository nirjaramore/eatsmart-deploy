import React, { useState } from 'react'
import CircularText from './CircularText'

const Hero: React.FC = () => {
    // Reference the video placed in the project's `asset/` folder (URL-encoded when used in the src)
    const videoFileName = 'From KlickPin CF Super Nonna → Illustration animation [Video] _ Graphic design posters Graphic design inspiration Branding design.mp4'
    const videoSrc = encodeURI(`/asset/${videoFileName}`)

    // Pattern: Word 1 "Know" - special 4th letter (outline),
    // Word 2 "what" - special 3rd letter (a) should be outline (keep 'w' filled),
    // Word 3 "you" - special 2nd letter (outline),
    // Word 4 "are" - special 3rd letter (outline),
    // Word 5 "eating" - special 4th letter (outline)
    const renderWord = (word: string, specialIndex: number, key: string, specialType: 'outline' | 'empty' | 'filled' = 'outline') => {
        return word.split('').map((letter, i) => {
            let cls = 'letter-filled'
            if (i === specialIndex) {
                if (specialType === 'outline') cls = 'letter-outline'
                else if (specialType === 'empty') cls = 'letter-empty'
                else cls = 'letter-filled'
            }
            return (
                <span key={`${key}-${i}`} className={cls} aria-hidden={cls === 'letter-empty'}>
                    {letter}
                </span>
            )
        })
    }

    const [activeLabel, setActiveLabel] = useState<string | null>(null)

    return (
        <section className="hero-root relative flex flex-col items-start justify-start" style={{ minHeight: '120vh', background: 'transparent', overflow: 'visible', position: 'relative', zIndex: 9999, paddingBottom: '6rem' }}>
            {/* Top header: left/right brand text and center nav links */}
            <header className="top-header" role="banner" style={{ zIndex: 11000 }}>
                <div className="top-brand">
                    <CircularText text="EATSMART" onHover="speedUp" spinDuration={120} className="top-brand-circular" centerImage={'/asset/Black and Purple Illustrative Beauty and Nail Art Studio Logo.png'} />
                </div>
                <nav className="top-nav">
                    <a
                        href="#"
                        className={`top-link ${activeLabel === 'Home' ? 'active' : ''}`}
                        data-text="Home"
                        onMouseEnter={() => setActiveLabel('Home')}
                        onMouseLeave={() => setActiveLabel(null)}
                    >
                        <span className="link-inner">Home</span>
                    </a>

                    <a
                        href="/about"
                        className={`top-link ${activeLabel === 'About Us' ? 'active' : ''}`}
                        data-text="About Us"
                        onMouseEnter={() => setActiveLabel('About Us')}
                        onMouseLeave={() => setActiveLabel(null)}
                    >
                        <span className="link-inner">About Us</span>
                    </a>

                    <a
                        href="#"
                        className={`top-link ${activeLabel === 'Community' ? 'active' : ''}`}
                        data-text="Community"
                        onMouseEnter={() => setActiveLabel('Community')}
                        onMouseLeave={() => setActiveLabel(null)}
                    >
                        <span className="link-inner">Community</span>
                    </a>
                </nav>
            </header>
            {/* Background video (covers full hero area) */}
            <video
                className="absolute w-full h-full object-cover pointer-events-none hero-bg-video"
                src={videoSrc}
                autoPlay
                muted
                loop
                playsInline
                style={{ zIndex: 9998, top: 0, left: 0, right: 0, bottom: 0, objectPosition: 'center center', background: 'transparent', outline: 'none', border: 'none' }}
            />

            {/* Overlay content (above the video) */}
            <div className="w-full pt-20 px-8 relative" style={{ zIndex: 10001 }}>
                <h1 className="heading mb-2">
                    {renderWord('Know', 3, 'know', 'outline')}&nbsp;{renderWord('what', 2, 'what', 'outline')}&nbsp;{renderWord('you', 1, 'you', 'outline')}&nbsp;{renderWord('are', 2, 'are', 'outline')}
                    <br />
                    {renderWord('eating', 3, 'eating', 'outline')}
                </h1>
                <p className="text-sm text-brandText/80 mb-6" style={{ marginLeft: '4px' }}>Together we can make everything better.</p>
            </div>

            {/* Curved marquee removed from hero — moved to the next page section */}
        </section>
    )
}

export default Hero
