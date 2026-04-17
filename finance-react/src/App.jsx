import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Home from './pages/Home.jsx'
import Converter from './pages/Converter.jsx'
import Analysis from './pages/Analysis.jsx'
import News from './pages/News.jsx'
import About from './pages/About.jsx'
import Comments from './pages/Comments.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Profile from './pages/Profile.jsx'
import AssetDetail from './pages/AssetDetail.jsx'
import NotFound from './pages/NotFound.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/converter" element={<Converter />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/news" element={<News />} />
        <Route path="/about" element={<About />} />
        <Route path="/comments" element={<Comments />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/profile/:username" element={<Profile />} />
        <Route path="/assets/:assetName" element={<AssetDetail />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
