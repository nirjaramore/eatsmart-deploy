import { useEffect, useRef, useState } from 'react'
import styles from './AutoZoomGallery.module.css'
import { gsap } from 'gsap'

import img28 from '../asset/download (28).jpeg'
import img29 from '../asset/download (29).jpeg'
import img30 from '../asset/download (30).jpeg'
import pizza from '../asset/Corat Coret Pizza_ A Fun and Colorful Twist on Your Favorite Slice.jpeg'
import bts from '../asset/Content Creator BTS Photoshoot.jpeg'
import transforma from '../asset/Transforma tu ig_ Fotografía_Iluminación.jpeg'

const galleryData = [
    {
        image: img28,
        title: 'Healthy Breakfast Bowl',
        description: '85% of us check brand names, but only 20% actually read ingredients. just 18% of Gen Z consistently reads labels even though 58% buy packaged food regularly. we\'re out here trusting vibes over facts. the problem? labels can be misleading even with strict FSSAI norms—"sugar-free" loaded with fats, "real fruit" juices with 10% actual fruit. most of us find nutrition info either too confusing or too cramped.'
    },
    {
        image: img29,
        title: 'Fresh Organic Produce',
        description: 'Farm to table freshness guaranteed. We partner with local farmers to bring you the freshest organic produce. Every item is carefully selected to ensure the highest quality and nutritional value for your family.'
    },
    {
        image: img30,
        title: 'Gourmet Dishes',
        description: 'Expertly crafted culinary experiences that combine traditional techniques with modern flavors. Each dish is prepared with passion and attention to detail, ensuring every bite is memorable.'
    },
    {
        image: pizza,
        title: 'Artisan Pizza',
        description: 'Hand-tossed perfection with quality toppings. Our pizzas are made with authentic Italian techniques, using premium ingredients and aged dough for that perfect crispy yet chewy texture.'
    },
    {
        image: bts,
        title: 'Food Photography',
        description: 'Capturing the essence of every meal through stunning visuals. We believe food should look as good as it tastes, and our photography brings out the beauty in every dish.'
    },
    {
        image: transforma,
        title: 'Transform Your Plate',
        description: 'Creative presentations that inspire healthy eating habits. Learn how to make your meals both nutritious and visually appealing with our expert tips and techniques.'
    }
]

export default function AutoZoomGallery() {
    const containerRef = useRef<HTMLDivElement>(null)
    const [currentIndex, setCurrentIndex] = useState(0)
    const [isInView, setIsInView] = useState(false)
    const timelineRef = useRef<gsap.core.Timeline | null>(null)
    const isAnimatingRef = useRef(false)

    useEffect(() => {
        if (!containerRef.current) return

        const galleryItems = containerRef.current.querySelectorAll(`.${styles.item}`)
        const descriptionSection = containerRef.current.querySelector(`.${styles.descriptionSection}`)
        const bottomCard = containerRef.current.querySelector(`.${styles.bottomCard}`)
        const descriptions = containerRef.current.querySelectorAll(`.${styles.description}`)

        if (galleryItems.length === 0) return

        // Set initial state - all items visible in grid
        gsap.set(galleryItems, { scale: 1, zIndex: 1, opacity: 1 })
        if (descriptionSection) {
            gsap.set(descriptionSection, { opacity: 0 })
        }
        if (bottomCard) {
            gsap.set(bottomCard, { y: 100, opacity: 0 })
        }

        let currentIdx = 0
        let isAnimating = false
        let isInViewport = false

        // Intersection Observer to detect when section is in view
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    isInViewport = entry.isIntersecting
                    setIsInView(entry.isIntersecting)
                    if (!entry.isIntersecting) {
                        // Hide bottom card immediately when scrolling away
                        if (bottomCard) {
                            gsap.set(bottomCard, { y: 100, opacity: 0 })
                        }
                        // Pause current animation
                        if (timelineRef.current) {
                            timelineRef.current.pause()
                        }
                        isAnimating = false
                    } else {
                        // Resume or start animation when in view
                        if (timelineRef.current && timelineRef.current.paused()) {
                            timelineRef.current.resume()
                        } else if (!isAnimating) {
                            animateItem(currentIdx)
                        }
                    }
                })
            },
            {
                threshold: 0.3, // Section must be at least 30% visible
                rootMargin: '0px'
            }
        )

        // Observe the container
        if (containerRef.current) {
            observer.observe(containerRef.current)
        }

        // Scroll handler to hide bottom card on any scroll
        const handleScroll = () => {
            if (bottomCard && isAnimating) {
                const cardOpacity = gsap.getProperty(bottomCard, 'opacity')
                if (cardOpacity > 0) {
                    gsap.to(bottomCard, {
                        y: 100,
                        opacity: 0,
                        duration: 0.3,
                        ease: 'power2.out'
                    })
                }
            }
        }

        window.addEventListener('scroll', handleScroll, { passive: true })

        const animateItem = (index: number) => {
            isAnimating = true
            isAnimatingRef.current = true
            const item = galleryItems[index] as HTMLElement

            // Get current position and size
            const rect = item.getBoundingClientRect()
            const scaleX = window.innerWidth / rect.width
            const scaleY = window.innerHeight / rect.height
            const translateX = (window.innerWidth / 2 - (rect.left + rect.width / 2))
            const translateY = (window.innerHeight / 2 - (rect.top + rect.height / 2))

            const tl = gsap.timeline({
                onComplete: () => {
                    isAnimating = false
                    isAnimatingRef.current = false
                    // Only move to next item if still in view
                    if (isInViewport) {
                        currentIdx = (currentIdx + 1) % galleryItems.length
                        setCurrentIndex(currentIdx)
                        // Small delay before starting next animation
                        setTimeout(() => {
                            if (isInViewport) {
                                animateItem(currentIdx)
                            }
                        }, 500)
                    }
                }
            })

            // Stage 1: Zoom slightly bigger (1.5x)
            tl.to(item, {
                scale: 1.5,
                zIndex: 50,
                duration: 0.8,
                ease: 'power2.out'
            })
                // Brief pause
                .to({}, { duration: 0.3 })
                // Stage 2: Expand to fullscreen from slightly zoomed state
                .to(item, {
                    x: translateX,
                    y: translateY,
                    scale: Math.max(scaleX, scaleY),
                    zIndex: 100,
                    duration: 1,
                    ease: 'power2.inOut'
                })
                // Show bottom card with slide up animation
                .to(bottomCard, {
                    y: 0,
                    opacity: 1,
                    duration: 0.6,
                    ease: 'power2.out'
                }, '-=0.2')
                // Auto-scroll the text content
                .to(bottomCard.querySelector(`.${styles.bottomCardContent}`), {
                    scrollTop: '+=150',
                    duration: 3,
                    ease: 'power1.inOut',
                    repeat: 1,
                    yoyo: true
                }, '+=0.5')
                // Hold for viewing
                .to({}, { duration: 1.5 })
                // Hide bottom card
                .to(bottomCard, {
                    y: 100,
                    opacity: 0,
                    duration: 0.5,
                    ease: 'power2.in'
                })
                // Stage 1: Zoom back to slightly bigger (1.5x) from fullscreen
                .to(item, {
                    x: 0,
                    y: 0,
                    scale: 1.5,
                    zIndex: 50,
                    duration: 0.8,
                    ease: 'power2.out'
                }, '-=0.2')
                // Brief pause
                .to({}, { duration: 0.3 })
                // Stage 2: Final zoom back to original position
                .to(item, {
                    scale: 1,
                    zIndex: 1,
                    duration: 0.8,
                    ease: 'power2.inOut'
                })
                // Brief pause before next
                .to({}, { duration: 0.5 })

            timelineRef.current = tl
        }

        return () => {
            observer.disconnect()
            window.removeEventListener('scroll', handleScroll)
            if (timelineRef.current) {
                timelineRef.current.kill()
            }
        }
    }, [])

    const getSrc = (img: any) => {
        return img && typeof img === 'object' && 'src' in img ? img.src : img
    }

    return (
        <section className={styles.wrapper} ref={containerRef}>
            <div className={styles.galleryContainer}>
                <div className={styles.gallery}>
                    {galleryData.map((item, index) => (
                        <div
                            key={index}
                            className={`${styles.item} ${currentIndex === index ? styles.active : ''}`}
                            data-index={index}
                        >
                            <img src={getSrc(item.image)} alt={item.title} />
                        </div>
                    ))}
                </div>
            </div>

            {/* Bottom card that appears when image is fullscreen */}
            <div className={styles.bottomCard}>
                <div className={styles.bottomCardContent}>
                    {galleryData.map((item, index) => (
                        <div
                            key={index}
                            className={`${styles.cardText} ${currentIndex === index ? styles.activeCard : ''}`}
                        >
                            <h3>{item.title}</h3>
                            <p>{item.description}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Description section below gallery */}
            <div className={styles.descriptionSection}>
                {galleryData.map((item, index) => (
                    <div
                        key={index}
                        className={`${styles.description} ${currentIndex === index ? styles.activeDesc : ''}`}
                    >
                        <h3>{item.title}</h3>
                        <p>{item.description}</p>
                    </div>
                ))}
            </div>
        </section>
    )
}
