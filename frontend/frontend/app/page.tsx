'use client'

import React, { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import {
  AlertCircle,
  BarChart3,
  Check,
  Copy,
  Database,
  LayoutDashboard,
  Lightbulb,
  Link2,
  Loader2,
  PieChart as PieChartIcon,
  Play,
  Sparkles,
  Table2,
  TerminalSquare,
  TrendingUp,
} from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts'

type QueryResult = {
  columns: string[]
  rows: Record<string, unknown>[]
  row_count: number
}

type ChartSuggestion = {
  type: 'bar' | 'pie' | 'line' | 'none'
  title?: string
  reason?: string
  x_axis?: string
  y_axis?: string
  label_key?: string
  value_key?: string
}

type DatasetTablePreview = {
  table_name: string
  columns: string[]
  sample_rows: Record<string, unknown>[]
}

type DatasetPreview = {
  ok: boolean
  stats: {
    total_users: number
    total_orders: number
    distinct_categories: number
    distinct_cities: number
  }
  tables: DatasetTablePreview[]
}

type ApiResponse = {
  ok: boolean
  prompt: string
  sql: string
  sql_source?: string
  text_response?: string
  insights?: string[]
  result?: QueryResult
  chart_suggestion?: ChartSuggestion
  detail?: unknown
}

type ChartSpec = {
  kind: 'bar' | 'pie' | 'line' | 'none'
  title: string
  reason: string
  xKey?: string
  yKey?: string
  nameKey?: string
  valueKey?: string
}

const API_BASE = 'http://127.0.0.1:8000'
const EXAMPLE_PROMPTS = [
  'show all users',
  'top 10 users by total spending',
  'show total sales by category',
  'average order amount by payment method',
  'show repeat customers',
  'show number of users by segment',
  'show sales by city',
  'show monthly sales',
]

const PIE_COLORS = [
  '#38bdf8',
  '#a78bfa',
  '#34d399',
  '#f59e0b',
  '#f87171',
  '#22d3ee',
  '#818cf8',
  '#4ade80',
]

function prettyDetail(detail: unknown) {
  if (!detail) return 'Unknown error'
  if (typeof detail === 'string') return detail
  try {
    return JSON.stringify(detail, null, 2)
  } catch {
    return String(detail)
  }
}

function isNumericValue(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value)
}

function looksLikeDateColumn(name: string) {
  const key = name.toLowerCase()
  return (
    key.includes('date') ||
    key.includes('month') ||
    key.includes('time') ||
    key.includes('year')
  )
}

function looksLikeDimensionColumn(name: string) {
  const key = name.toLowerCase()
  return [
    'city',
    'state',
    'segment',
    'status',
    'category',
    'payment',
    'channel',
    'name',
    'month',
    'product',
  ].some((word) => key.includes(word))
}

function getHeuristicChartSpec(result?: QueryResult): ChartSpec {
  if (!result || !result.rows.length || result.columns.length < 2) {
    return {
      kind: 'none',
      title: 'No chart available',
      reason: 'Run a grouped query to visualize the result.',
    }
  }

  const { columns, rows } = result
  const numericColumns = columns.filter((col) =>
    rows.some((row) => isNumericValue(row[col])),
  )
  const textColumns = columns.filter((col) => !numericColumns.includes(col))

  const metric =
    numericColumns.find((col) =>
      /total|count|avg|amount|sales|spending|quantity|value|revenue/i.test(col),
    ) ?? numericColumns[0]
  const dimension =
    textColumns.find((col) => looksLikeDateColumn(col)) ??
    textColumns.find((col) => looksLikeDimensionColumn(col)) ??
    textColumns[0]

  if (!metric || !dimension) {
    return {
      kind: 'none',
      title: 'No chart available',
      reason: 'The result does not contain a clear metric and grouping column.',
    }
  }

  if (looksLikeDateColumn(dimension)) {
    return {
      kind: 'line',
      title: `${metric} over ${dimension}`,
      reason: 'Time-like data is better shown as a trend.',
      xKey: dimension,
      yKey: metric,
    }
  }

  if (rows.length <= 6) {
    return {
      kind: 'pie',
      title: `${metric} by ${dimension}`,
      reason: 'Small grouped distributions are easy to compare in a pie chart.',
      nameKey: dimension,
      valueKey: metric,
    }
  }

  return {
    kind: 'bar',
    title: `${metric} by ${dimension}`,
    reason: 'Category comparisons work well in a bar chart.',
    xKey: dimension,
    yKey: metric,
  }
}

function getChartSpec(response: ApiResponse | null): ChartSpec {
  const suggestion = response?.chart_suggestion
  if (suggestion && suggestion.type !== 'none') {
    if (suggestion.type === 'bar') {
      return {
        kind: 'bar',
        title:
          suggestion.title ?? `${suggestion.y_axis} by ${suggestion.x_axis}`,
        reason: suggestion.reason ?? 'Suggested by backend.',
        xKey: suggestion.x_axis,
        yKey: suggestion.y_axis,
      }
    }
    if (suggestion.type === 'line') {
      return {
        kind: 'line',
        title:
          suggestion.title ?? `${suggestion.y_axis} over ${suggestion.x_axis}`,
        reason: suggestion.reason ?? 'Suggested by backend.',
        xKey: suggestion.x_axis,
        yKey: suggestion.y_axis,
      }
    }
    if (suggestion.type === 'pie') {
      return {
        kind: 'pie',
        title:
          suggestion.title ??
          `${suggestion.value_key} by ${suggestion.label_key}`,
        reason: suggestion.reason ?? 'Suggested by backend.',
        nameKey: suggestion.label_key,
        valueKey: suggestion.value_key,
      }
    }
  }
  return getHeuristicChartSpec(response?.result)
}

function getChartData(response: ApiResponse | null, spec: ChartSpec) {
  const rows = response?.result?.rows ?? []
  if (spec.kind === 'none') return []

  const sliced = rows.slice(0, 12)
  if (spec.kind === 'pie') {
    return sliced.map((row, idx) => ({
      ...row,
      fill: PIE_COLORS[idx % PIE_COLORS.length],
    }))
  }
  return sliced
}

function formatValue(value: unknown) {
  if (typeof value === 'number') {
    return Number.isInteger(value)
      ? value.toLocaleString()
      : value.toLocaleString(undefined, { maximumFractionDigits: 2 })
  }
  return String(value ?? '')
}

function SectionTitle({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description?: string
}) {
  return (
    <div>
      <div className="flex items-center gap-2 text-white">
        {icon}
        <h3 className="text-lg font-semibold">{title}</h3>
      </div>
      {description ? (
        <p className="mt-1 text-sm text-slate-400">{description}</p>
      ) : null}
    </div>
  )
}

export default function SqlQueryRunnerFrontend() {
  const [datasetPreview, setDatasetPreview] = useState<DatasetPreview | null>(
    null,
  )
  const [connectionUri, setConnectionUri] = useState('sqlite:///./test.db')
  const [prompt, setPrompt] = useState('top 10 users by total spending')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [response, setResponse] = useState<ApiResponse | null>(null)
  const [error, setError] = useState('')
  const [history, setHistory] = useState<ApiResponse[]>([])

  React.useEffect(() => {
    async function loadPreview() {
      try {
        const res = await fetch(
          `${API_BASE}/dataset/preview?connection_uri=${encodeURIComponent(
            connectionUri,
          )}`,
        )
        const data = await res.json()
        if (res.ok) setDatasetPreview(data)
      } catch {
        // ignore preview failures for now
      }
    }
    loadPreview()
  }, [connectionUri])

  const chartSpec = useMemo(() => getChartSpec(response), [response])
  const chartData = useMemo(() => getChartData(response, chartSpec), [
    response,
    chartSpec,
  ])
  const rows = response?.result?.rows ?? []
  const columns = response?.result?.columns ?? []

  async function runQuery() {
    setLoading(true)
    setError('')

    try {
      const res = await fetch(`${API_BASE}/query/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ connection_uri: connectionUri, prompt }),
      })

      const data = await res.json()
      if (!res.ok) throw new Error(prettyDetail(data?.detail ?? data))

      setResponse(data)
      setHistory((prev) =>
        [data, ...prev.filter((item) => item.prompt !== data.prompt)].slice(
          0,
          8,
        ),
      )
    } catch (err) {
      setResponse(null)
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  async function copySql() {
    if (!response?.sql) return
    await navigator.clipboard.writeText(response.sql)
    setCopied(true)
    setTimeout(() => setCopied(false), 1200)
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(59,130,246,0.18),_transparent_25%),radial-gradient(circle_at_bottom_right,_rgba(168,85,247,0.16),_transparent_28%),linear-gradient(to_bottom,#020617,#0f172a,#020617)] text-slate-100">
      <div className="mx-auto max-w-7xl p-4 md:p-8">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 space-y-6"
        >
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-4">
              <div className="rounded-3xl bg-sky-500/15 p-4 text-sky-400 shadow-lg shadow-sky-500/10">
                <LayoutDashboard className="h-7 w-7" />
              </div>
              <div>
                <h1 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">
                  AI SQL Workspace
                </h1>
                <p className="mt-1 text-sm text-slate-400 md:text-base">
                  Query your data in plain English, inspect SQL, review
                  insights, and visualize results.
                </p>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3">
              <Card className="rounded-2xl border-slate-800 bg-slate-900/70 px-4 py-3">
                <div className="text-xs text-slate-500">Rows</div>
                <div className="mt-1 text-2xl font-semibold text-white">
                  {response?.result?.row_count ?? 0}
                </div>
              </Card>
              <Card className="rounded-2xl border-slate-800 bg-slate-900/70 px-4 py-3">
                <div className="text-xs text-slate-500">Columns</div>
                <div className="mt-1 text-2xl font-semibold text-white">
                  {columns.length}
                </div>
              </Card>
              <Card className="rounded-2xl border-slate-800 bg-slate-900/70 px-4 py-3">
                <div className="text-xs text-slate-500">Source</div>
                <div className="mt-2">
                  <Badge className="rounded-full bg-emerald-500/15 text-emerald-300 hover:bg-emerald-500/15">
                    {response?.sql_source ?? '—'}
                  </Badge>
                </div>
              </Card>
            </div>
          </div>

          <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
            <CardHeader>
              <SectionTitle
                icon={<Database className="h-5 w-5 text-cyan-400" />}
                title="Dataset Explorer"
                description="Preview the data you are querying so prompts become easier to write."
              />
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="grid gap-4 md:grid-cols-4">
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Total users
                  </div>
                  <div className="mt-2 text-2xl font-semibold text-white">
                    {datasetPreview?.stats?.total_users ?? '—'}
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Total orders
                  </div>
                  <div className="mt-2 text-2xl font-semibold text-white">
                    {datasetPreview?.stats?.total_orders ?? '—'}
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Categories
                  </div>
                  <div className="mt-2 text-2xl font-semibold text-white">
                    {datasetPreview?.stats?.distinct_categories ?? '—'}
                  </div>
                </div>
                <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                  <div className="text-xs uppercase tracking-wide text-slate-500">
                    Cities
                  </div>
                  <div className="mt-2 text-2xl font-semibold text-white">
                    {datasetPreview?.stats?.distinct_cities ?? '—'}
                  </div>
                </div>
              </div>

              <div className="grid gap-5 xl:grid-cols-2">
                {(datasetPreview?.tables ?? []).map((table) => (
                  <div
                    key={table.table_name}
                    className="rounded-2xl border border-slate-800 bg-slate-950 p-4"
                  >
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <div>
                        <div className="text-base font-semibold text-white">
                          {table.table_name}
                        </div>
                        <div className="text-xs text-slate-500">
                          Sample rows + columns
                        </div>
                      </div>
                      <Badge
                        variant="outline"
                        className="border-slate-700 text-slate-300"
                      >
                        {table.columns.length} columns
                      </Badge>
                    </div>

                    <div className="mb-3 flex flex-wrap gap-2">
                      {table.columns.map((col) => (
                        <Badge
                          key={`${table.table_name}-${col}`}
                          variant="outline"
                          className="border-slate-800 text-slate-400"
                        >
                          {col}
                        </Badge>
                      ))}
                    </div>

                    <div className="overflow-hidden rounded-2xl border border-slate-800">
                      <div className="max-h-[240px] overflow-auto">
                        <table className="w-max min-w-full border-collapse text-sm">
                          <thead className="sticky top-0 bg-slate-900/95">
                            <tr className="border-b border-slate-800">
                              {table.columns.map((col) => (
                                <th
                                  key={`${table.table_name}-head-${col}`}
                                  className="whitespace-nowrap px-3 py-2 text-left font-medium text-slate-300"
                                >
                                  {col}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {table.sample_rows.map((row, idx) => (
                              <tr
                                key={`${table.table_name}-row-${idx}`}
                                className="border-b border-slate-900/80 last:border-0"
                              >
                                {table.columns.map((col) => (
                                  <td
                                    key={`${table.table_name}-${idx}-${col}`}
                                    className="whitespace-nowrap px-3 py-2 text-slate-200"
                                  >
                                    {formatValue(row[col])}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <div className="grid gap-6 xl:grid-cols-[360px_minmax(0,1fr)]">
          <div className="space-y-6">
            <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-2xl backdrop-blur">
              <CardHeader>
                <SectionTitle
                  icon={<Database className="h-5 w-5 text-sky-400" />}
                  title="Query Composer"
                  description="Write a question and run it against your backend."
                />
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">
                    Connection URI
                  </label>
                  <div className="relative">
                    <Link2 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                    <Input
                      value={connectionUri}
                      onChange={(e) => setConnectionUri(e.target.value)}
                      className="h-11 rounded-2xl border-slate-800 bg-slate-950 pl-10 text-slate-100 placeholder:text-slate-500"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-300">
                    Question
                  </label>
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="min-h-[140px] resize-none rounded-2xl border-slate-800 bg-slate-950 text-base text-slate-100 placeholder:text-slate-500"
                    placeholder="Example: show total sales by category"
                  />
                </div>

                <Button
                  onClick={runQuery}
                  disabled={loading || !prompt.trim()}
                  className="h-11 w-full rounded-2xl"
                >
                  {loading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="mr-2 h-4 w-4" />
                  )}
                  {loading ? 'Running...' : 'Run Query'}
                </Button>
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
              <CardHeader>
                <SectionTitle
                  icon={<Sparkles className="h-5 w-5 text-fuchsia-400" />}
                  title="Example Prompts"
                />
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {EXAMPLE_PROMPTS.map((item) => (
                    <button
                      key={item}
                      onClick={() => setPrompt(item)}
                      className="rounded-full border border-slate-800 bg-slate-950 px-3 py-1.5 text-sm text-slate-300 transition hover:border-slate-700 hover:bg-slate-900 hover:text-white"
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
              <CardHeader>
                <SectionTitle
                  icon={<TrendingUp className="h-5 w-5 text-emerald-400" />}
                  title="Recent Runs"
                />
              </CardHeader>
              <CardContent className="space-y-3">
                {history.length === 0 ? (
                  <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-950 p-5 text-sm text-slate-500">
                    Your recent queries will appear here.
                  </div>
                ) : (
                  history.map((item, idx) => (
                    <button
                      key={`${item.prompt}-${idx}`}
                      onClick={() => {
                        setPrompt(item.prompt)
                        setResponse(item)
                        setError('')
                      }}
                      className="w-full rounded-2xl border border-slate-800 bg-slate-950 p-4 text-left transition hover:border-slate-700 hover:bg-slate-900"
                    >
                      <div className="mb-2 flex items-center justify-between gap-3">
                        <div className="line-clamp-2 text-sm font-medium text-white">
                          {item.prompt}
                        </div>
                        <Badge className="rounded-full bg-slate-800 text-slate-300 hover:bg-slate-800">
                          {item.result?.row_count ?? 0}
                        </Badge>
                      </div>
                      <div className="line-clamp-2 text-xs text-slate-400">
                        {item.sql}
                      </div>
                    </button>
                  ))
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            {error ? (
              <Card className="rounded-3xl border-red-900/70 bg-red-950/40 text-red-50">
                <CardContent className="flex items-start gap-3 p-4">
                  <AlertCircle className="mt-0.5 h-5 w-5 text-red-300" />
                  <div className="space-y-2">
                    <div className="font-medium">Request failed</div>
                    <pre className="whitespace-pre-wrap text-sm text-red-100">
                      {error}
                    </pre>
                  </div>
                </CardContent>
              </Card>
            ) : null}

            <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
              <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
                <CardHeader>
                  <SectionTitle
                    icon={<Lightbulb className="h-5 w-5 text-amber-400" />}
                    title="Answer & Insights"
                    description="Plain-English explanation alongside a few quick observations."
                  />
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5 text-slate-200">
                    {response?.text_response ??
                      'Run a query to get a direct answer here.'}
                  </div>
                  <div className="grid gap-3 md:grid-cols-3">
                    {(response?.insights?.length
                      ? response.insights
                      : ['Insights will appear here after a successful run.']
                    ).map((insight, idx) => (
                      <div
                        key={`${insight}-${idx}`}
                        className="rounded-2xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-300"
                      >
                        {insight}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
                <CardHeader className="flex flex-row items-start justify-between">
                  <SectionTitle
                    icon={<TerminalSquare className="h-5 w-5 text-sky-400" />}
                    title="Generated SQL"
                    description="Review the executed query."
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={copySql}
                    disabled={!response?.sql}
                    className="border-slate-700 bg-slate-950 text-slate-200 hover:bg-slate-900"
                  >
                    {copied ? (
                      <Check className="mr-2 h-4 w-4" />
                    ) : (
                      <Copy className="mr-2 h-4 w-4" />
                    )}
                    {copied ? 'Copied' : 'Copy'}
                  </Button>
                </CardHeader>
                <CardContent>
                  <pre className="max-h-[260px] overflow-auto rounded-2xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-200">
                    <code>{response?.sql ?? '-- SQL will appear here'}</code>
                  </pre>
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
              <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
                <CardHeader>
                  <SectionTitle
                    icon={
                      chartSpec.kind === 'pie' ? (
                        <PieChartIcon className="h-5 w-5 text-fuchsia-400" />
                      ) : (
                        <BarChart3 className="h-5 w-5 text-violet-400" />
                      )
                    }
                    title="Smart Chart"
                    description={chartSpec.reason}
                  />
                </CardHeader>
                <CardContent>
                  {chartSpec.kind === 'none' ? (
                    <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-950 p-8 text-center text-slate-500">
                      No chart suggestion for this result.
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-sm font-medium text-slate-300">
                        {chartSpec.title}
                      </div>
                      <div className="h-[320px] rounded-2xl border border-slate-800 bg-slate-950 p-3">
                        <ResponsiveContainer width="100%" height="100%">
                          {chartSpec.kind === 'bar' ? (
                            <BarChart
                              data={chartData}
                              margin={{ top: 8, right: 8, left: 0, bottom: 40 }}
                            >
                              <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="rgba(148,163,184,0.15)"
                              />
                              <XAxis
                                dataKey={chartSpec.xKey}
                                tick={{ fill: '#94a3b8', fontSize: 12 }}
                                angle={-20}
                                textAnchor="end"
                                height={60}
                              />
                              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                              <Tooltip />
                              <Legend />
                              <Bar
                                dataKey={chartSpec.yKey}
                                radius={[10, 10, 0, 0]}
                                fill="#8b5cf6"
                              />
                            </BarChart>
                          ) : chartSpec.kind === 'pie' ? (
                            <PieChart>
                              <Tooltip />
                              <Legend />
                              <Pie
                                data={chartData}
                                dataKey={chartSpec.valueKey}
                                nameKey={chartSpec.nameKey}
                                outerRadius={110}
                                label
                              >
                                {chartData.map((entry: any, idx) => (
                                  <Cell
                                    key={idx}
                                    fill={
                                      entry.fill ??
                                      PIE_COLORS[idx % PIE_COLORS.length]
                                    }
                                  />
                                ))}
                              </Pie>
                            </PieChart>
                          ) : (
                            <LineChart
                              data={chartData}
                              margin={{ top: 8, right: 8, left: 0, bottom: 16 }}
                            >
                              <CartesianGrid
                                strokeDasharray="3 3"
                                stroke="rgba(148,163,184,0.15)"
                              />
                              <XAxis
                                dataKey={chartSpec.xKey}
                                tick={{ fill: '#94a3b8', fontSize: 12 }}
                              />
                              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
                              <Tooltip />
                              <Legend />
                              <Line
                                type="monotone"
                                dataKey={chartSpec.yKey}
                                stroke="#34d399"
                                strokeWidth={3}
                                dot={{ r: 4 }}
                              />
                            </LineChart>
                          )}
                        </ResponsiveContainer>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
                <CardHeader>
                  <SectionTitle
                    icon={<BarChart3 className="h-5 w-5 text-emerald-400" />}
                    title="Result Metadata"
                    description="A quick structural summary of the current result."
                  />
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <div className="text-xs uppercase tracking-wide text-slate-500">
                        Rows
                      </div>
                      <div className="mt-2 text-2xl font-semibold text-white">
                        {response?.result?.row_count ?? 0}
                      </div>
                    </div>
                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
                      <div className="text-xs uppercase tracking-wide text-slate-500">
                        Columns
                      </div>
                      <div className="mt-2 text-2xl font-semibold text-white">
                        {columns.length}
                      </div>
                    </div>
                  </div>
                  <Separator className="bg-slate-800" />
                  <div>
                    <div className="mb-2 text-sm font-medium text-slate-300">
                      Columns returned
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {columns.length ? (
                        columns.map((col) => (
                          <Badge
                            key={col}
                            variant="outline"
                            className="border-slate-700 text-slate-300"
                          >
                            {col}
                          </Badge>
                        ))
                      ) : (
                        <span className="text-sm text-slate-500">
                          No columns yet
                        </span>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card className="rounded-3xl border-slate-800 bg-slate-900/70 shadow-xl backdrop-blur">
              <CardHeader>
                <SectionTitle
                  icon={<Table2 className="h-5 w-5 text-emerald-400" />}
                  title="Result Table"
                  description="Structured rows returned from the backend."
                />
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-slate-800 bg-slate-950/70 px-4 py-3 text-sm text-slate-400">
                  <div>
                    Showing{' '}
                    <span className="font-medium text-slate-200">
                      {rows.length}
                    </span>{' '}
                    row(s) and{' '}
                    <span className="font-medium text-slate-200">
                      {columns.length}
                    </span>{' '}
                    column(s)
                  </div>
                  <div className="text-xs text-slate-500">
                    Tip: for richer results, ask prompts like{' '}
                    <span className="text-slate-300">
                      “show user name and order amount”
                    </span>{' '}
                    or{' '}
                    <span className="text-slate-300">
                      “top users by total spending with names”
                    </span>
                    .
                  </div>
                </div>

                {!rows.length ? (
                  <div className="rounded-2xl border border-dashed border-slate-800 bg-slate-950 p-8 text-center text-slate-400">
                    No rows to display yet.
                  </div>
                ) : (
                  <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-950">
                    <div className="max-h-[520px] overflow-auto">
                      <table className="w-max min-w-full border-collapse text-sm">
                        <thead className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur">
                          <tr className="border-b border-slate-800">
                            {columns.map((col) => (
                              <th
                                key={col}
                                className="whitespace-nowrap px-4 py-3 text-left font-medium text-slate-300"
                              >
                                {col}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {rows.map((row, idx) => (
                            <tr
                              key={idx}
                              className="border-b border-slate-900/80 align-top last:border-0 hover:bg-slate-900/40"
                            >
                              {columns.map((col) => (
                                <td
                                  key={`${idx}-${col}`}
                                  className="max-w-[280px] whitespace-nowrap px-4 py-3 text-slate-200"
                                  title={formatValue(row[col])}
                                >
                                  {formatValue(row[col])}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
