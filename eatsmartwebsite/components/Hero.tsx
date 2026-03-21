import React, { useRef } from 'react'
import SiteHeader from './SiteHeader'

const Hero: React.FC = () => {
    // Reference the video placed in the project's `asset/` folder (URL-encoded when used in the src)
    const videoFileName = 'From KlickPin CF Super Nonna → Illustration animation [Video] _ Graphic design posters Graphic design inspiration Branding design.mp4'
    const videoSrc = encodeURI(`/asset/${videoFileName}`)

    const videoRef = useRef<HTMLVideoElement | null>(null)

    return (
        <section className="hero-root relative flex flex-col items-start justify-start" style={{ minHeight: '120vh', background: 'transparent', overflow: 'visible', position: 'relative', zIndex: 9999, paddingBottom: '6rem' }}>
            <SiteHeader active="home" />
            {/* Background video (covers full hero area) - made static (no autoplay/loop). */}
            <video
                ref={videoRef}
                className="absolute w-full h-full object-cover pointer-events-none hero-bg-video"
                src={videoSrc}
                autoPlay
                muted
                loop
                playsInline
                preload="metadata"
                style={{
                    zIndex: 9998,
                    top: '96px',
                    left: 0,
                    right: 0,
                    bottom: 0,
                    height: 'calc(100% - 96px)',
                    objectPosition: '10% center',
                    transform: 'translate(-24px, 120px)',
                    background: 'transparent',
                    outline: 'none',
                    border: 'none'
                }}
            />

            {/* Overlay content (behind the video) */}
            <div className="w-full pt-20 px-8 relative" style={{ zIndex: 9997 }}>
                {/* Clean typography matching attached design */}
                <div className="hero-text-block">
                    <h1 className="hero-main-text">
                        <span style={{ display: 'block' }}>know <span className="hero-offset-what">what</span></span>
                        <span style={{ display: 'block' }}>you are <span className="hero-offset-eating"><em>eating</em></span></span>
                    </h1>
                </div>
            </div>

            {/* Curved marquee removed from hero — moved to the next page section */}
        </section>
    )
}

export default Hero
