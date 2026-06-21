import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import "./globals.css"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>
        <SidebarProvider>
          <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground">
            {/* 사이드바 내비게이션 */}
            <AppSidebar />
            
            <main className="flex-1 flex flex-col overflow-y-auto">
              {/* 상단 툴바 */}
              <div className="flex items-center p-4 border-b h-14 justify-between bg-card">
                <SidebarTrigger />
                <div className="text-sm font-semibold text-muted-foreground">Sync Ops Agent Web Console</div>
              </div>
              
              {/* 메인 콘텐츠 대시보드 */}
              <div className="p-6 max-w-7xl w-full mx-auto">{children}</div>
            </main>
          </div>
        </SidebarProvider>
      </body>
    </html>
  )
}