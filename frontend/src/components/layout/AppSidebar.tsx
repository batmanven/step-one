import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { useNavigate, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  FolderOpen,
  Image as ImageIcon,
  BookOpen,
  Home,
  Sparkles,
  Settings,
  Terminal
} from "lucide-react"

const items = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Sessions", url: "/sessions", icon: FolderOpen },
  { title: "Outputs", url: "/outputs", icon: ImageIcon },
  { title: "API Docs", url: "/docs", icon: BookOpen },
]

const systemItems = [
  { title: "Settings", url: "/settings", icon: Settings },
  { title: "Cluster Logs", url: "/logs", icon: Terminal },
]

export function AppSidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Sidebar className="bg-[#0B0F14] border-r border-white/5">
      <SidebarHeader className="px-6 py-5">
        <div
          className="flex items-center gap-3 cursor-pointer"
          onClick={() => navigate("/")}
        >
          <span className="text-sm font-semibold text-white tracking-tight">
            Content Engine
          </span>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-3">
        <SidebarGroup>
      

          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {items.map((item) => {
                const active = location.pathname === item.url
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      isActive={active}
                      onClick={() => navigate(item.url)}
                      className={`h-10 px-3 rounded-lg flex items-center gap-3 transition ${active
                        ? "bg-white text-black"
                        : "text-white/60 hover:text-white hover:bg-white/5"
                        }`}
                    >
                      <item.icon
                        className={`h-4 w-4 ${active ? "text-black" : "text-white/60"
                          }`}
                      />
                      <span className="text-sm font-medium">
                        {item.title}
                      </span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>


      </SidebarContent>
    </Sidebar>
  )
}