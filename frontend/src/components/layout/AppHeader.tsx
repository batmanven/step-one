import { SidebarTrigger } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { useNavigate, useLocation } from "react-router-dom"
import { Plus, Bell, Search, User } from "lucide-react"

export function AppHeader() {
  const navigate = useNavigate()
  const location = useLocation()

  const getPageTitle = () => {
    const path = location.pathname.split('/')[1]
    return path.charAt(0).toUpperCase() + path.slice(1) || 'Dashboard'
  }

  return (
    <header className="flex h-16 shrink-0 items-center gap-4 px-6 sticky top-0 bg-background/50 backdrop-blur-md z-10 border-b border-white/5">
      <div className="flex items-center gap-4">
        <SidebarTrigger className="-ml-1 hover:bg-white/5 rounded-full" />
        <h1 className="text-xs font-medium tracking-wide text-shade-50">/ {getPageTitle()}</h1>
      </div>

      <div className="flex-1 flex justify-center">
      </div>

      <div className="flex items-center gap-4">

        <button
          onClick={() => navigate('/dashboard')}
          className="btn-pill min-w-[160px] bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold uppercase tracking-widest flex items-center justify-center gap-2 shadow-lg shadow-blue-900/20 transition-all"
        >
          <Plus className="h-3.5 w-3.5" />
          New Pipeline
        </button>


      </div>
    </header>
  )
}
