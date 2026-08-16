// Shared TypeScript types for the code-analysis feature. These mirror the
// Pydantic schemas in backend/app/schemas/analysis.py field-for-field, so if
// the backend response shape ever changes, this is the first file to update.

export type Language = "python" | "cpp" | "javascript";

// Drives the language dropdown in CodeEditor.tsx. `backendReady` controls
// whether we show the "coming soon" warning — only Python is wired up
// server-side right now (see analysis_service.py's _SUPPORTED_LANGUAGES).
export const SUPPORTED_LANGUAGES: { value: Language; label: string; backendReady: boolean }[] = [
  { value: "python", label: "Python", backendReady: true },
  { value: "cpp", label: "C++", backendReady: false },
  { value: "javascript", label: "JavaScript", backendReady: false },
];

// Body of POST /api/v1/analyze.
export interface AnalyzeRequest {
  language: Language;
  source_code: string;
  iterations?: number;
}

export type AnalysisStatus = "pending" | "running" | "complete" | "error";

// One function's shape/size/branching stats, from the static analyzer.
export interface FunctionMetrics {
  name: string;
  line_number: number;
  line_count: number;
  cyclomatic_complexity: number;
}

// A function/class/variable name that breaks Python naming conventions.
export interface NamingViolation {
  kind: "function" | "class" | "variable";
  name: string;
  line_number: number;
  reason: string;
}

// A variable that was assigned but never read.
export interface UnusedVariable {
  name: string;
  line_number: number;
  scope: string;
}

// raw_results.static_analysis — everything the ast-based analyzer found.
export interface StaticAnalysisRaw {
  lines_of_code: number;
  function_count: number;
  average_cyclomatic_complexity: number;
  max_cyclomatic_complexity: number;
  quality_score: number;
  syntax_error: string | null;
  functions: FunctionMetrics[];
  naming_violations: NamingViolation[];
  unused_variables: UnusedVariable[];
}

// raw_results.benchmark — timing stats from the C++/Python engine.
export interface BenchmarkRaw {
  execution_time_ms: number;
  median_time_ms: number;
  p95_time_ms: number;
  min_time_ms: number;
  max_time_ms: number;
  memory_bytes: number;
  iterations: number;
  source: "cpp_engine" | "python_fallback";
}

// One row of raw_results.profile.hotspots — a single profiled function.
export interface ProfileHotspot {
  function_name: string;
  filename: string;
  line_number: number;
  call_count: number;
  total_time_ms: number;
  cumulative_time_ms: number;
}

// raw_results.profile — cProfile output, ranked slowest-first.
export interface ProfileRaw {
  total_time_ms: number;
  function_count: number;
  total_call_count: number;
  hotspots: ProfileHotspot[];
}

// raw_results.sandbox — whether the submitted code ran successfully.
export interface SandboxRaw {
  success: boolean;
  error: string | null;
  stdout: string;
}

// The full "raw_results" JSON blob attached to every AnalysisOut. Every field
// is optional because a failed step (e.g. a syntax error) can leave later
// steps unset.
export interface RawResults {
  static_analysis?: StaticAnalysisRaw;
  sandbox?: SandboxRaw;
  benchmark?: BenchmarkRaw;
  profile?: ProfileRaw;
  ai_error?: string;
}

// One suggestion from the Claude recommendations panel.
export interface AIRecommendation {
  title: string;
  severity: "high" | "medium" | "low";
  explanation: string;
  suggested_fix: string;
}

// ai_recommendations — the full structured report from Claude, or null if
// no API key was configured / the call failed.
export interface AIReport {
  summary: string;
  overall_score: number;
  recommendations: AIRecommendation[];
}

// Response shape for POST /analyze and GET /results/{id}.
export interface AnalysisOut {
  id: number;
  language: string;
  status: AnalysisStatus;
  execution_time_ms: number | null;
  memory_bytes: number | null;
  cyclomatic_complexity: number | null;
  lines_of_code: number | null;
  function_count: number | null;
  quality_score: number | null;
  ai_recommendations: AIReport | null;
  raw_results: RawResults | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

// Response shape for one row of GET /history — a trimmed-down AnalysisOut.
export interface AnalysisHistoryItem {
  id: number;
  language: string;
  status: AnalysisStatus;
  quality_score: number | null;
  execution_time_ms: number | null;
  created_at: string;
}
