import { NavLink } from 'react-router-dom'

const NAV = [
  { to: '/',         label: 'Graph',    icon: '◎' },
  { to: '/explore',  label: 'Explore',  icon: '⊞' },
  { to: '/timeline', label: 'Timeline', icon: '⏱' },
  { to: '/settings', label: 'Settings', icon: '⚙' },
]

export default function Sidebar() {
  return (
    <nav className="w-16 bg-gray-950 border-r border-gray-800 flex flex-col items-center py-4 gap-1 shrink-0">
      {NAV.map(({ to, label, icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          title={label}
          className={({ isActive }) =>
            `w-10 h-10 rounded-lg flex items-center justify-center text-lg transition-colors ${
              isActive
                ? 'bg-brand-700 text-white'
                : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
            }`
          }
        >
          {icon}
        </NavLink>
      ))}
    </nav>
  )
}
