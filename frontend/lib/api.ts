// Central Axios client for every call to the FastAPI backend. Every other
// file that needs to talk to the API imports from here rather than calling
// axios directly, so the base URL and auth header only need to be set up once.
import axios from "axios";
import type { AnalyzeRequest, AnalysisOut, AnalysisHistoryItem } from "@/types/analysis";
import type { Token, UserCreate, UserOut } from "@/types/auth";
import { useAuthStore } from "@/lib/store";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  headers: { "Content-Type": "application/json" },
});

// Runs before every request: attaches the logged-in user's JWT (if any) so
// individual pages never have to remember to do it themselves.
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// POST /analyze — run the full benchmark + static analysis + AI pipeline.
export const analyzeCode = (payload: AnalyzeRequest) =>
  api.post<AnalysisOut>("/api/v1/analyze", payload).then((r) => r.data);

// GET /results/{public_id} — fetch one past analysis by its public token.
export const getResult = (publicId: string) =>
  api.get<AnalysisOut>(`/api/v1/results/${publicId}`).then((r) => r.data);

// GET /history — list the logged-in user's past analyses.
export const getHistory = () =>
  api.get<AnalysisHistoryItem[]>("/api/v1/history").then((r) => r.data);

// POST /auth/register — create a new account.
export const registerUser = (payload: UserCreate) =>
  api.post<UserOut>("/api/v1/auth/register", payload).then((r) => r.data);

// POST /auth/login — the backend expects OAuth2 form-encoded fields, not
// JSON, so this builds that request shape instead of reusing the default
// JSON header. Its "username" field carries the user's email.
export const loginUser = (email: string, password: string) => {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  return api
    .post<Token>("/api/v1/auth/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    })
    .then((r) => r.data);
};

export default api;
