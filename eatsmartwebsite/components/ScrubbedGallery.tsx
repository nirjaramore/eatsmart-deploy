import { useEffect, useRef } from 'react'
import styles from './ScrubbedGallery.module.css'

import img28 from '../asset/download (28).jpeg'
import img29 from '../asset/download (29).jpeg'
import img30 from '../asset/download (30).jpeg'
import pizza from '../asset/Corat Coret Pizza_ A Fun and Colorful Twist on Your Favorite Slice.jpeg'
import bts from '../asset/Content Creator BTS Photoshoot.jpeg'
import transforma from '../asset/Transforma tu ig_ Fotografía_Iluminación.jpeg'

// Use ESM gsap imports when available for better tree-shaking and plugin registration
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { Flip } from 'gsap/Flip'
gsap.registerPlugin(ScrollTrigger, Flip)

export default function ScrubbedGallery() {
  const containerRef = useRef<HTMLElement | null>(null)
  const ctxRef = useRef<any>(null)

  useEffect(() => {
    // Use the imported ESM `gsap`, `ScrollTrigger`, and `Flip` directly
    // They were registered at module top-level with `gsap.registerPlugin(ScrollTrigger, Flip)`

    const galleryEl = containerRef.current?.querySelector('#gallery-8') as HTMLElement
    if (!galleryEl) return

    let flipCtx: any

    const createTween = () => {
      const galleryElement = galleryEl
      const galleryItems = galleryElement.querySelectorAll('.gallery__item')

      if (flipCtx && flipCtx.revert) flipCtx.revert()
      galleryElement.classList.remove('gallery--final')

      ctxRef.current = gsap.context(() => {
        galleryElement.classList.add('gallery--final')
        const flipState = Flip?.getState ? Flip.getState(galleryItems) : null
        galleryElement.classList.remove('gallery--final')

        const flip = flipState && Flip.to(flipState, { simple: true, ease: 'expoScale(1, 5)' })

        const tl = gsap.timeline({
          scrollTrigger: {
            trigger: galleryElement,
            start: 'center center',
            end: '+=100%',
            scrub: true,
            pin: galleryElement.parentNode,
          },
        })

        if (flip) tl.add(flip)
        else {
          // fallback animation if Flip is not available
          tl.to(galleryItems, { y: -50, duration: 1, stagger: 0.08 })
        }
      }, galleryElement)

      // cleanup function used by resize handler
      return () => gsap.set(galleryItems, { clearProps: 'all' })
    }

    createTween()

    const onResize = () => {
      // debounce a bit
      clearTimeout((onResize as any)._t)
      ;(onResize as any)._t = setTimeout(() => createTween(), 150)
    }

    window.addEventListener('resize', onResize)

    return () => {
      window.removeEventListener('resize', onResize)
      if (ctxRef.current) ctxRef.current.revert && ctxRef.current.revert()
      // kill any ScrollTrigger instances attached to this gallery
      try {
        ScrollTrigger?.getAll?.().forEach((st: any) => {
          if (st.trigger && galleryEl && galleryEl.contains(st.trigger)) st.kill()
        })
      } catch (e) {}
    }
  }, [])

  return (
    <section className={styles.wrapper} ref={containerRef} aria-label="Scrubbed gallery">
      <div className={`${styles.galleryWrap} gallery-wrap`}>
        <div className={`gallery gallery--bento gallery--switch ${styles.gallery}`} id="gallery-8">
          {
            // helper inline: support Next.js StaticImageData imports or string URLs
          }
          {
            (() => {
              const getSrc = (i: any) => (i && typeof i === 'object' && 'src' in i ? i.src : i)
              return (
                <>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(img28)} alt="gallery 1" />
                  </div>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(img29)} alt="gallery 2" />
                  </div>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(img30)} alt="gallery 3" />
                  </div>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(pizza)} alt="pizza artwork" />
                  </div>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(bts)} alt="content creator" />
                  </div>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(transforma)} alt="transforma" />
                  </div>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(img28)} alt="gallery repeat" />
                  </div>
                  <div className={`gallery__item ${styles.item}`}>
                    <img src={getSrc(img29)} alt="gallery repeat 2" />
                  </div>
                </>
              )
            })()
          }
        </div>
      </div>

      <div className={styles.section}>
        <h2>Here is some content</h2>
        <p>Placeholder paragraph text to demonstrate the pinning and scrub effect.</p>
        <p>Additional content below the gallery so ScrollTrigger has page space to scrub.</p>
      </div>
    </section>
  )
}
