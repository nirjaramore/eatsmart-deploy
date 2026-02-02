import React, { useRef, useEffect, useState, useMemo, useId, FC, PointerEvent } from 'react'
import styles from './CurvedLoop.module.css'

interface CurvedLoopProps {
  marqueeText?: string
  speed?: number
  className?: string
  curveAmount?: number
  direction?: 'left' | 'right'
  interactive?: boolean
}

const CurvedLoop: FC<CurvedLoopProps> = ({
  marqueeText = '',
  speed = 2,
  className,
  curveAmount = 800,
  direction = 'left',
  interactive = true
}) => {
  const text = useMemo(() => {
    const hasTrailing = /\s|\u00A0$/.test(marqueeText)
    return (hasTrailing ? marqueeText.replace(/\s+$/, '') : marqueeText) + '\u00A0'
  }, [marqueeText])

  const measureRef = useRef<SVGTextElement | null>(null)
  const totalMeasureRef = useRef<SVGTextElement | null>(null)
  const textPathRef = useRef<SVGTextPathElement | null>(null)
  const pathRef = useRef<SVGPathElement | null>(null)
  const [spacing, setSpacing] = useState(0)
  const [fullLength, setFullLength] = useState(0)
  const [offset, setOffset] = useState(0)
  const uid = useId()
  const pathId = `curve-${uid}`
  const pathD = `M-800,40 Q720,${40 + curveAmount} 2800,40`

  const dragRef = useRef(false)
  const lastXRef = useRef(0)
  const dirRef = useRef<'left' | 'right'>(direction)
  const velRef = useRef(0)

  const textLength = spacing
  // Increase repetition significantly so full phrases are always visible
  const repetition = textLength ? Math.ceil(3600 / textLength) + 10 : 1
  // embed a star glyph after the word 'community' so it always travels with the phrase
  const basePhrase = (marqueeText || '').trim()
  const phraseWithStar = (basePhrase.match(/community$/i) ? basePhrase.replace(/community$/i, (m) => m + '✦') : basePhrase) + '\u00A0'
  const totalText = textLength ? Array(repetition).fill(phraseWithStar).join('') : phraseWithStar || text
  const ready = spacing > 0

  useEffect(() => {
    if (measureRef.current) setSpacing(measureRef.current.getComputedTextLength())
  }, [text, className])

  useEffect(() => {
    if (!spacing) return
    // measure full repeated text length
    if (totalMeasureRef.current) {
      const fl = totalMeasureRef.current.getComputedTextLength()
      setFullLength(fl)
      // Start with offset so at least 2-3 full phrases are visible
      const initial = -spacing * 2
      if (textPathRef.current) textPathRef.current.setAttribute('startOffset', initial + 'px')
      setOffset(initial)

      // star glyphs are embedded in the repeated text; no extra measurement needed
    }
  }, [spacing])

  useEffect(() => {
    if (!spacing || !ready || !pathRef.current || !fullLength) return
    const pathLen = pathRef.current.getTotalLength()
    let frame = 0
    const step = () => {
      if (!dragRef.current && textPathRef.current) {
        const delta = dirRef.current === 'right' ? speed : -speed
        const curA = parseFloat(textPathRef.current.getAttribute('startOffset') || '0')
        let newA = curA + delta
        const wrapPoint = fullLength
        if (newA <= -wrapPoint) newA += wrapPoint
        if (newA > 0) newA -= wrapPoint
        textPathRef.current.setAttribute('startOffset', newA + 'px')
        setOffset(newA)

        // no separate sparkles — star glyphs are embedded in the text
      }
      frame = requestAnimationFrame(step)
    }
    frame = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frame)
  }, [spacing, speed, ready, fullLength])

  const onPointerDown = (e: PointerEvent) => {
    if (!interactive) return
    dragRef.current = true
    lastXRef.current = e.clientX
    velRef.current = 0
      ; (e.target as HTMLElement).setPointerCapture(e.pointerId)
  }

  const onPointerMove = (e: PointerEvent) => {
    if (!interactive || !dragRef.current || !textPathRef.current) return
    const dx = e.clientX - lastXRef.current
    lastXRef.current = e.clientX
    velRef.current = dx
    const currentOffset = parseFloat(textPathRef.current.getAttribute('startOffset') || '0')
    let newOffset = currentOffset + dx
    const wrapPoint = fullLength || spacing
    if (newOffset <= -wrapPoint) newOffset += wrapPoint
    if (newOffset > 0) newOffset -= wrapPoint
    textPathRef.current.setAttribute('startOffset', newOffset + 'px')
    setOffset(newOffset)
  }

  const endDrag = () => {
    if (!interactive) return
    dragRef.current = false
    dirRef.current = velRef.current > 0 ? 'right' : 'left'
  }

  const cursorStyle = interactive ? (dragRef.current ? 'grabbing' : 'grab') : 'auto'

  return (
    <div
      className={styles['curved-loop-jacket']}
      style={{ visibility: ready ? 'visible' : 'hidden', cursor: cursorStyle }}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={endDrag}
      onPointerLeave={endDrag}
    >
      <svg className={styles['curved-loop-svg']} viewBox="-400 0 2240 120">
        <text ref={measureRef} xmlSpace="preserve" style={{ visibility: 'hidden', opacity: 0, pointerEvents: 'none' }}>
          {text}
        </text>
        <text ref={totalMeasureRef} xmlSpace="preserve" style={{ visibility: 'hidden', opacity: 0, pointerEvents: 'none' }}>
          {totalText}
        </text>
        <defs>
          <path ref={pathRef} id={pathId} d={pathD} fill="none" stroke="transparent" />
        </defs>
        {ready && (
          <>
            <text fontWeight="bold" xmlSpace="preserve" className={`${className ?? ''} ${styles['curved-loop-text']}`}>
              <textPath ref={textPathRef} href={`#${pathId}`} startOffset={offset + 'px'} xmlSpace="preserve">
                {totalText}
              </textPath>
            </text>

            {/* star glyphs are embedded in the text (✦) so they move with the phrase */}
          </>
        )}
      </svg>
    </div>
  )
}

export default CurvedLoop
