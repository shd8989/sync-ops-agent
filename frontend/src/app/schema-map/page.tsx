"use client"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Network, ArrowRightLeft } from "lucide-react"

export default function SchemaMapPage() {
  const [targetTable, setTargetTable] = useState("TB_ORDER")
  
  // graph_map.py의 리턴 데이터 구조 규격 예시
  const [graphData] = useState({
    baseTable: "TB_ORDER",
    dependencies: [
      { name: "TB_USER", relation: "FK_ORDER_USER (부모)", strategy: "Cascaded Include" },
      { name: "TB_PRODUCT", relation: "FK_ORDER_PROD (부모)", strategy: "Cascaded Include" },
      { name: "TB_PAYMENT", relation: "FK_PAY_ORDER (자식)", strategy: "Optional Select" }
    ]
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">FK 구조 및 연관 이관 맵</h1>
        <p className="text-muted-foreground">외래 키(FK) 토폴로지를 분석하여 이관 시 참조 무결성이 보장되는 연관 테이블 목록을 구성합니다.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="w-5 h-5 text-primary" />
            의존성 그래프 탐색 (graph_map)
          </CardTitle>
          <CardDescription>기준 테이블을 입력하면 연동 이관이 필요한 상/하위 오브젝트를 에이전트가 매핑합니다.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex gap-2 max-w-sm">
            <Input value={targetTable} onChange={(e) => setTargetTable(e.target.value)} />
            <Button variant="secondary">관계 추적</Button>
          </div>

          <div className="p-6 bg-muted/30 rounded-xl border border-dashed flex flex-col justify-center items-center gap-6">
            <div className="bg-primary text-primary-foreground font-bold p-4 rounded-xl shadow-sm text-center min-w-[150px]">
              {graphData.baseTable}
              <div className="text-[10px] font-normal opacity-80 mt-1">이관 타겟 마스터</div>
            </div>

            <div className="flex flex-col gap-3 w-full max-w-xl">
              {graphData.dependencies.map((dep, idx) => (
                <div key={idx} className="flex items-center justify-between bg-card p-3 rounded-lg border shadow-sm">
                  <div className="flex items-center gap-3">
                    <ArrowRightLeft className="w-4 h-4 text-muted-foreground" />
                    <div>
                      <span className="font-semibold text-sm block">{dep.name}</span>
                      <span className="text-xs text-muted-foreground font-mono">{dep.relation}</span>
                    </div>
                  </div>
                  <Badge variant={dep.strategy.includes("Include") ? "default" : "secondary"}>
                    {dep.strategy}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
          
          <div className="flex justify-end">
            <Button className="font-semibold">연관 관계 포함 이관 파일럿 생성</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}