import { useEffect, useRef } from 'react'

/**
 * particles.js index.html'de global olarak yüklü.
 * Bir kez init edilir; sayfa geçişlerinde DOM'dan kaldırılmaz (SPA).
 */
export default function ParticlesBackground() {
  const initedRef = useRef(false)

  useEffect(() => {
    if (initedRef.current) return
    initedRef.current = true
    if (typeof window === 'undefined' || !window.particlesJS) return

    window.particlesJS('particles-js', {
      particles: {
        number: { value: 80, density: { enable: true, value_area: 800 } },
        color: { value: '#ffffff' },
        shape: { type: 'circle' },
        opacity: { value: 0.5, random: true },
        size: { value: 3, random: true },
        line_linked: {
          enable: true, distance: 150,
          color: '#ffffff', opacity: 0.4, width: 1
        },
        move: {
          enable: true, speed: 4,
          direction: 'none', random: false,
          straight: false, out_mode: 'out'
        }
      },
      interactivity: {
        detect_on: 'canvas',
        events: {
          onhover: { enable: true, mode: 'grab' },
          onclick: { enable: true, mode: 'push' }
        },
        modes: {
          grab: { distance: 140, line_linked: { opacity: 1 } },
          push: { particles_nb: 4 }
        }
      },
      retina_detect: true
    })
  }, [])

  return <div id="particles-js" />
}
