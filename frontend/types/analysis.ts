export type Language = "python" | "cpp" | "javascript";

export interface AnalysisRequest {
  language: Language;
  source_code: string;
}

export interface AIRecommendation {
  title: string;
  severity: "high" | "medium" | "low";
  description: string;
  suggestion: string;
}

export interface AnalysisResult {
  id: number;
  language: Language;
  status: "pending" | "running" | "complete" | "error";
  execution_time_ms: number | null;
  memory_bytes: number | null;
  loop_depth: number | null;
  cyclomatic_complexity: number | null;
  quality_score: number | null;
  ai_recommendations: AIRecommendation[] | null;
  created_at: string;
  completed_at: string | null;
  error_message: string | null;
}
