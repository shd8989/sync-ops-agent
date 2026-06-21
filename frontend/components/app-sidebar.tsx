import { Database, Columns, RefreshCw, GitFork, Settings } from "lucide-react"
import { Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar"

const items = [
  { title: "스키마 비교", url: "/schema-compare", icon: Columns },
  { title: "데이터 이관 (Sync)", url: "/data-sync", icon: RefreshCw },
  { title: "FK 구조 맵", url: "/schema-map", icon: GitFork },
  { title: "커넥션 설정", url: "/connections", icon: Database },
]

export function AppSidebar() {
  return (
    <Sidebar variant="sidebar" collapsible="icon">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-lg font-bold px-4 py-6 text-primary">Sync Ops Agent</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild className="py-6 px-4 gap-4">
                    <a href={item.url}>
                      <item.icon className="w-5 h-5" />
                      <span className="text-sm font-medium">{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}