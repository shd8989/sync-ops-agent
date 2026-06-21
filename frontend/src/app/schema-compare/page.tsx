"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

interface DBInfo {
  key: string
  driver: string
}

export default function SchemaComparePage() {
  const [dbList, setDbList] = useState<DBInfo[]>([]) // 백엔드에서 불러온 DB 리스트
  const [driver, setDriver] = useState("mysql")
  const [sourceDb, setSourceDb] = useState("")
  const [targetDb, setTargetDb] = useState("")
  const [loading, setLoading] = useState(false)
  const [fetchLoading, setFetchLoading] = useState(true)
  const [diffResults, setDiffResults] = useState<any[]>([])

  // 1. 컴포넌트 마운트 시 백엔드 API에서 DB 정보 로드
  useEffect(() => {
    async function fetchDatabases() {
      try {
        const res = await fetch("http://localhost:8000/api/schema/databases")
        if (!res.ok) throw new Error("DB 목록을 불러오는데 실패했습니다.")
        const data = await res.json()
        setDbList(data)
      } catch (error) {
        console.error("API 연동 에러:", error)
      } finally {
        setFetchLoading(false)
      }
    }
    fetchDatabases()
  }, [])

  // 2. 소스 DB 선택 시 드라이버 자동 매핑 로직 (선택 편의성용)
  const handleSourceChange = (value: string) => {
    setSourceDb(value)
    const selected = dbList.find(db => db.key === value)
    if (selected && selected.driver !== "unknown") {
      setDriver(selected.driver)
    }
  }

  // FastAPI 백엔드 연동 핸들러
  const handleCompareTrigger = async () => {
    if (!sourceDb || !targetDb) {
      alert("비교할 소스 및 타겟 데이터베이스를 모두 선택해주세요.")
      return
    }

    setLoading(true)
    
    try {
      // 실제 연동 시 주석 해제하여 백엔드로 API 요청 송신
      const res = await fetch(`http://localhost:8000/api/schema/compare?driver=${driver}&source=${sourceDb}&target=${targetDb}`)
      const data = await res.json()
      
      // 가상 Mock 데이터 세팅 (테스트 완료 후 백엔드 실제 output 구조와 연동)
      setTimeout(() => {
        setDiffResults([
          { table: "TB_USER_MAIN", type: "Column Missing", dev: "LOGIN_FAIL_CNT (NUMBER)", prod: "[Missing]", status: "CRITICAL" },
          { table: "TB_ORDER_HIST", type: "Index Missing", dev: "IDX_ORDER_DATE_01", prod: "[Missing]", status: "WARNING" },
          { table: "SP_DAILY_SETTLE", type: "Procedure Changed", dev: "Modified (2026-06-15)", prod: "Old Version (2025-12-01)", status: "CRITICAL" },
        ])
        setLoading(false)
      }, 1200)
    } catch (error) {
      console.error(error)
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">스키마 동기화 검증</h1>
        <p className="text-muted-foreground">백엔드 에이전트 시스템 환경 파일(.env)에 정의된 인프라 DB의 구조 차이를 동적으로 추출합니다.</p>
      </div>

      <div className="flex flex-wrap gap-4 items-center bg-card p-4 rounded-xl border">
        {/* 1. 비교 기준 DB (Source / Dev) */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-muted-foreground">비교 기준 DB (Source / Dev)</label>
          <Select value={sourceDb} onValueChange={handleSourceChange} disabled={fetchLoading}>
            <SelectTrigger className="w-[220px]">
              <SelectValue placeholder={fetchLoading ? "DB 로딩 중..." : "기준 DB 선택"} />
            </SelectTrigger>
            <SelectContent>
              {dbList.map((db) => (
                <SelectItem key={db.key} value={db.key}>
                  {db.key} ({db.driver.toUpperCase()})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* 2. 비교 대상 DB (Target / Prod) */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-muted-foreground">비교 대상 DB (Target / Prod)</label>
          <Select value={targetDb} onValueChange={setTargetDb} disabled={fetchLoading}>
            <SelectTrigger className="w-[220px]">
              <SelectValue placeholder={fetchLoading ? "DB 로딩 중..." : "대상 DB 선택"} />
            </SelectTrigger>
            <SelectContent>
              {dbList.map((db) => (
                <SelectItem key={db.key} value={db.key}>
                  {db.key} ({db.driver.toUpperCase()})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* 3. DBMS 종류 (자동 추론되나 수동 변경 가능) */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-muted-foreground">DBMS 종류</label>
          <Select value={driver} onValueChange={setDriver}>
            <SelectTrigger className="w-[160px]">
              <SelectValue placeholder="DBMS 드라이버" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="oracle">Oracle</SelectItem>
              <SelectItem value="mysql">MySQL / MariaDB</SelectItem>
              <SelectItem value="postgresql">PostgreSQL</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* 4. 실행 버튼 */}
        <div className="flex flex-col justify-end h-full pt-5">
          <Button onClick={handleCompareTrigger} disabled={loading || fetchLoading} className="h-10">
            {loading ? "에이전트 스킬 분석 중..." : "스키마 비교 스킬 실행"}
          </Button>
        </div>
      </div>

      {/* 분석 리포트 결과 영역 */}
      <Card>
        <CardHeader>
          <CardTitle>분석 로그 레포트</CardTitle>
          <CardDescription>
            {sourceDb && targetDb ? (
              <span className="font-medium text-foreground">
                [{sourceDb}] 환경과 [{targetDb}] 환경 간의 불일치 메타 정보 목록입니다.
              </span>
            ) : (
              "두 데이터베이스 간 불일치가 발견된 물리 구조 리스트입니다."
            )}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>대상 객체 / 테이블</TableHead>
                <TableHead>변동 타입</TableHead>
                <TableHead>비교 기준 ({sourceDb || "Source"})</TableHead>
                <TableHead>비교 대상 ({targetDb || "Target"})</TableHead>
                <TableHead>위험도</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {diffResults.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                    인프라 데이터베이스를 지정한 후 검증 스킬을 실행해 주세요.
                  </TableCell>
                </TableRow>
              ) : (
                diffResults.map((item, idx) => (
                  <TableRow key={idx}>
                    <TableCell className="font-mono font-bold">{item.table}</TableCell>
                    <TableCell>{item.type}</TableCell>
                    <TableCell className="text-blue-600 font-mono text-xs">{item.dev}</TableCell>
                    <TableCell className="text-rose-600 font-mono text-xs">{item.prod}</TableCell>
                    <TableCell>
                      <Badge variant={item.status === "CRITICAL" ? "destructive" : "outline"}>
                        {item.status}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}