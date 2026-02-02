import React, { useEffect, useRef, useState } from 'react'

interface CircularTextProps {
    text: string
    spinDuration?: number
    onHover?: 'slowDown' | 'speedUp' | 'pause' | 'goBonkers'
    className?: string
    centerImage?: string
}

const CircularText: React.FC<CircularTextProps> = ({
    text,
    spinDuration = 20,
    onHover = 'speedUp',
    className = ''
    , centerImage
}) => {
    const letters = Array.from(text)
    const containerRef = useRef<HTMLDivElement | null>(null)
    const [duration, setDuration] = useState<number>(spinDuration)
    const [paused, setPaused] = useState(false)

    useEffect(() => setDuration(spinDuration), [spinDuration])

    const handleMouseEnter = () => {
        switch (onHover) {
            case 'slowDown':
                setDuration(spinDuration * 2)
                setPaused(false)
                break
            case 'speedUp':
                setDuration(Math.max(0.5, spinDuration / 4))
                setPaused(false)
                break
            case 'pause':
                setPaused(true)
                break
            case 'goBonkers':
                setDuration(Math.max(0.1, spinDuration / 20))
                setPaused(false)
                break
            default:
                setDuration(spinDuration)
                setPaused(false)
        }
    }

    const handleMouseLeave = () => {
        setDuration(spinDuration)
        setPaused(false)
    }

    const radius = 28 // px; positions letters around circle

    return (
        <div
            ref={containerRef}
            className={`circular-text ${className}`}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            style={{ ['--spin-duration' as any]: `${duration}s`, ['--paused' as any]: paused ? 'paused' : 'running' }}
        >
            {letters.map((letter, i) => {
                const rotationDeg = (360 / letters.length) * i
                const transform = `rotate(${rotationDeg}deg) translate(${radius}px) rotate(${-rotationDeg}deg)`
                return (
                    <span key={i} className="circular-item" style={{ transform, WebkitTransform: transform }}>
                        <span className="circular-letter">{letter}</span>
                    </span>
                )
            })}
            {centerImage && (
                <div className="circular-center" aria-hidden>
                    <img src={encodeURI(centerImage)} alt="" />
                </div>
            )}
        </div>
    )
}

export default CircularText
