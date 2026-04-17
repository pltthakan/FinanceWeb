import { Outlet } from 'react-router-dom'
import LiveRateBar from './LiveRateBar.jsx'
import Navbar from './Navbar.jsx'
import ParticlesBackground from './ParticlesBackground.jsx'

export default function Layout() {
  return (
    <>
      <ParticlesBackground />
      <LiveRateBar />
      <Navbar />
      <main className="page">
        <Outlet />
      </main>
    </>
  )
}
