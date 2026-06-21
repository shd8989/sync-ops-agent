// src/app/data-sync/page.tsx
"use client"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function DataSyncPage() {
  const [syncType, setSyncType] = useState("recent")
  const [progress, setProgress] = useState(0)
  const [isSyncing, setIsSyncing] = useState(false)

  const handleSync = () => {
    setIsSyncing(true)
    setProgress(10)
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval)
          setIsSyncing(false)
          return 100
        }
        return prev + 30
      })
    }, 800)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight font-sans">데이터 동기화 (Sync)</h1>
        <p className="text-muted-foreground">이관 전략을 수립하여 소스 DB에서 타겟 DB로 데이터를 안전하게 전송합니다.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* 전략 설정 설정창 */}
        <Card>
          <CardHeader>
            <CardTitle>이관 전략 옵션</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between border-b pb-4">
              <div>
                <div className="font-semibold">마스터 & 코드 데이터 전체 이관</div>
                <div className="text-sm text-muted-foreground">기준 정보 및 공통 코드성 테이블을 100% 동기화합니다.</div>
              </div>
              <Switch defaultChecked />
            </div>

            <div className="space-y-3">
              <div>
                <div className="font-semibold">대용량 트랜잭션 데이터 제한 규칙</div>
                <div className="text-sm text-muted-foreground">로그성 데이터의 마이그레이션 범위를 제한합니다.</div>
              </div>
              <Select value={syncType} onValueChange={setSyncType}>
                <SelectTrigger>
                  <SelectValue placeholder="범위 선택" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="recent">최근 1달 데이터만 포함</SelectItem>
                  <SelectItem value="percent">전체 크기의 10% 무작위 샘플링</SelectItem>
                  <SelectItem value="all">전체 데이터 이관 (주의)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button className="w-full h-12 text-md" onClick={handleSync} disabled={isSyncing}>
              {isSyncing ? "데이터 이관 진행 중..." : "동기화(Sync) 작업 시작"}
            </Button>
          </CardContent>
        </Card>

        {/* 실시간 이관 상태 모니터링 */}
        <Card className="flex flex-col justify-between">
          <CardHeader>
            <CardTitle>진행 현황 모니터링</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 flex-1 flex flex-col justify-center">
            {isSyncing || progress > 0 ? (
              <div className="space-y-4">
                <div className="flex justify-between text-sm font-medium">
                  <span>테이블 마이그레이션 수행 중...</span>
                  <span>{progress}%</span>
                </div>
                <Progress value={progress} className="h-3 w-full" />
                <div className="text-xs text-muted-foreground font-mono bg-muted p-3 rounded border">
                  {progress >= 10 && "↳ [OK] 마스터 코드 데이터 전송 완료..\n"}
                  {progress >= 40 && "↳ [RUN] 트랜잭션 데이터 추출 중 (조건: 최근 1달)..\n"}
                  {progress >= 100 && "↳ [SUCCESS] 모든 타겟 인덱스 재빌드 및 검증 완료."}
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-muted-foreground">
                상단의 작업 시작 버튼을 누르면 동기화 파이프라인 로그가 여기에 표시됩니다.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}