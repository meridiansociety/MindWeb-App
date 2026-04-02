import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import LoginForm from './components/auth/LoginForm'
import RegisterForm from './components/auth/RegisterForm'
import Home from './pages/Home'
import Explore from './pages/Explore'
import Timeline from './pages/Timeline'
import Settings from './pages/Settings'
import Sidebar from './components/layout/Sidebar'
import Navbar from './components/layout/Navbar'

function PrivateLayout({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.accessToken)
  if (!token) return <Navigate to="/login" replace />
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0">
        <Navbar />
        <main className="flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route
          path="/"
          element={
            <PrivateLayout>
              <Home />
            </PrivateLayout>
          }
        />
        <Route
          path="/explore"
          element={
            <PrivateLayout>
              <Explore />
            </PrivateLayout>
          }
        />
        <Route
          path="/timeline"
          element={
            <PrivateLayout>
              <Timeline />
            </PrivateLayout>
          }
        />
        <Route
          path="/settings"
          element={
            <PrivateLayout>
              <Settings />
            </PrivateLayout>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
