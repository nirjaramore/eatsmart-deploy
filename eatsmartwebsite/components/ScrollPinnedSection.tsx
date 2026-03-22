import { useEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function ScrollPinnedSection() {
    const pinSectionRef = useRef<HTMLDivElement>(null)
    const ctxRef = useRef<gsap.Context | null>(null)

    useEffect(() => {
        if (!pinSectionRef.current) return

        const section = pinSectionRef.current
        const list = section.querySelector('.list') as HTMLElement
        const fill = section.querySelector('.fill') as HTMLElement
        const listItems = gsap.utils.toArray<HTMLElement>('li', list)
        const slides = gsap.utils.toArray<HTMLElement>('.slide', section)

        ctxRef.current = gsap.context(() => {
            const tl = gsap.timeline({
                scrollTrigger: {
                    trigger: section,
                    start: 'top top',
                    end: '+=' + listItems.length * 50 + '%',
                    pin: true,
                    scrub: true
                }
            })

            // First element visible, set the marker
            if (fill) {
                gsap.set(fill, {
                    scaleY: 1 / listItems.length,
                    transformOrigin: 'top left'
                })
            }

            listItems.forEach((item, i) => {
                const previousItem = listItems[i - 1]
                if (previousItem) {
                    tl.set(item, { color: '#e27575' }, 0.5 * i)
                        .to(
                            slides[i],
                            {
                                autoAlpha: 1,
                                duration: 0.2
                            },
                            '<'
                        )
                        .set(previousItem, { color: 'rgba(226, 117, 117, 0.4)' }, '<')
                        .to(
                            slides[i - 1],
                            {
                                autoAlpha: 0,
                                duration: 0.2
                            },
                            '<'
                        )
                } else {
                    gsap.set(item, { color: '#e27575' })
                    gsap.set(slides[i], { autoAlpha: 1 })
                }
            })

            tl.to(
                fill,
                {
                    scaleY: 1,
                    transformOrigin: 'top left',
                    ease: 'none',
                    duration: tl.duration()
                },
                0
            ).to({}, {}) // add a small pause at the end of the timeline before it un-pins
        }, section)

        return () => {
            // revert GSAP context (removes timelines/ScrollTriggers created inside the context)
            ctxRef.current?.revert()
            // ensure any lingering ScrollTrigger instances are killed to avoid DOM mutation issues
            try {
                ScrollTrigger.getAll().forEach((t) => t.kill())
            } catch (e) {
                // ignore errors during cleanup
            }
        }
    }, [])

    return (
        <>
            <section className="section pin-section" ref={pinSectionRef}>
                <div className="content">
                    <div className="left-side">
                        <ul className="list">
                            <li>How</li>
                            <li>We</li>
                            <li>Work</li>
                            <li>Together</li>
                        </ul>
                    </div>
                    <div className="fill"></div>
                    <div className="right-side">
                        <div className="slide">
                            <div className="image-card">
                                <img className="original-colors" src="/asset/From KlickPin CF Looking for reasons to spend more time in adobe animate So here ya go _ Motion design animation Illustration character design Motion graphics inspirationCriseyde.gif" alt="How we work animation" />
                            </div>
                        </div>
                        <div className="slide">
                            <div className="image-card">
                                <h3>Step 1</h3>
                                <p style={{ marginTop: '8px' }}>Click a photo of your food using your phone or camera.</p>
                            </div>
                        </div>
                        <div className="slide">
                            <div className="image-card">
                                <h3>Step 2</h3>
                                <p style={{ marginTop: '8px' }}>Upload it on our app — add details and confirm.</p>
                            </div>
                        </div>
                        <div className="slide">
                            <div className="image-card">
                                <h3>Step 3</h3>
                                <p style={{ marginTop: '8px' }}>Contribute to our community — share, comment, and help improve data.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <style jsx>{`
                .section {
                    width: 100%;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }

                .pin-section {
                    background: #fae5e7;
                }

                .content {
                    width: 100%;
                    max-width: 1400px;
                    margin: 0 auto;
                    /* Grid: right column must keep width — flex + only position:absolute children collapsed */
                    display: grid;
                    grid-template-columns: minmax(0, max-content) minmax(0, 1fr);
                    gap: 60px;
                    padding: 40px;
                    position: relative;
                    align-items: center;
                    box-sizing: border-box;
                }

                .left-side {
                    position: relative;
                    padding-left: 30px;
                    min-width: 0;
                }

                .content ul {
                    font-size: 72px;
                    color: #e27575;
                    margin: 0;
                    padding: 0;
                    list-style: none;
                    font-weight: bold;
                    line-height: 1.3;
                }

                .content .fill {
                    position: absolute;
                    top: 40px;
                    left: 40px;
                    width: 6px;
                    height: calc(100% - 80px);
                    background-color: #e27575;
                }

                .right-side {
                    position: relative;
                    min-height: 500px;
                    width: 100%;
                    min-width: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .right-side .slide {
                    position: absolute;
                    width: 100%;
                    top: 50%;
                    transform: translateY(-50%);
                    opacity: 0;
                    visibility: hidden;
                    display: flex;
                    justify-content: center;
                }

                .image-card {
                    background: #ffffff;
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 10px 40px rgba(226, 117, 117, 0.2);
                    max-width: 600px;
                    width: 100%;
                }

                /* Step heading styling: use same font as header and brand red color */
                .image-card h3 {
                    margin: 0;
                    font-family: 'Baloo 2', Inter, sans-serif;
                    font-weight: 700;
                    color: #e27575;
                    font-size: 2rem;
                    line-height: 1.05;
                }

                .image-card p {
                    margin: 8px 0 0 0;
                    font-family: 'Baloo 2', Inter, sans-serif;
                    color: #e27575;
                    font-weight: 400;
                    font-size: 1rem;
                }

                .image-card img,
                .image-card video {
                    width: 100%;
                    height: auto;
                    display: block;
                    border-radius: 12px;
                }

                .image-card img {
                    filter: grayscale(100%) sepia(100%) saturate(300%) hue-rotate(320deg) brightness(1.1) contrast(0.95);
                    mix-blend-mode: multiply;
                }

                .image-card img.original-colors {
                    filter: none;
                    mix-blend-mode: normal;
                }

                @media (max-width: 1024px) {
                    .content {
                        gap: 40px;
                        padding: 30px;
                    }

                    .content ul {
                        font-size: 56px;
                    }

                    .image-card {
                        max-width: 450px;
                        padding: 25px;
                    }
                }

                @media (max-width: 768px) {
                    .content {
                        grid-template-columns: 1fr;
                        gap: 30px;
                        padding: 20px;
                    }

                    .left-side {
                        padding-left: 30px;
                    }

                    .content ul {
                        font-size: 48px;
                    }

                    .content .fill {
                        top: 20px;
                        left: 20px;
                        height: 200px;
                    }

                    .right-side {
                        min-height: 400px;
                        width: 100%;
                    }

                    .image-card {
                        max-width: 100%;
                        padding: 20px;
                    }
                }

                @media (max-width: 480px) {
                    .content ul {
                        font-size: 36px;
                    }

                    .left-side {
                        padding-left: 20px;
                    }

                    .image-card {
                        padding: 15px;
                    }
                }
            `}</style>
        </>
    )
}
