// Monaco (VS Code's editor) with a language dropdown above it. Used on the
// /analyze page. Language choice only changes syntax highlighting here —
// the backend currently only benchmarks Python, so a warning shows for the
// other two.
"use client";

import Editor from "@monaco-editor/react";
import { SUPPORTED_LANGUAGES, type Language } from "@/types/analysis";

// Maps our Language type to the language ids Monaco expects.
const MONACO_LANGUAGE: Record<Language, string> = {
  python: "python",
  cpp: "cpp",
  javascript: "javascript",
};

interface CodeEditorProps {
  language: Language;
  onLanguageChange: (language: Language) => void;
  code: string;
  onCodeChange: (code: string) => void;
}

export default function CodeEditor({ language, onLanguageChange, code, onCodeChange }: CodeEditorProps) {
  return (
    <div className="rounded-lg border border-zinc-800 overflow-hidden bg-[#1e1e1e]">
      <div className="flex items-center justify-between px-3 py-2 border-b border-zinc-800 bg-zinc-900">
        <label className="flex items-center gap-2 text-sm text-zinc-400">
          Language
          <select
            value={language}
            onChange={(e) => onLanguageChange(e.target.value as Language)}
            className="bg-zinc-800 text-zinc-200 text-sm rounded-md px-2 py-1 border border-zinc-700 focus:outline-none focus:ring-1 focus:ring-sky-500"
          >
            {SUPPORTED_LANGUAGES.map((l) => (
              <option key={l.value} value={l.value}>
                {l.label}
                {!l.backendReady ? " (coming soon)" : ""}
              </option>
            ))}
          </select>
        </label>
        {/* Only Python is wired up server-side (see analysis_service.py) */}
        {!SUPPORTED_LANGUAGES.find((l) => l.value === language)?.backendReady && (
          <span className="text-xs text-amber-400">
            Benchmarking currently only supports Python — this submission will return an error.
          </span>
        )}
      </div>
      <Editor
        height="420px"
        language={MONACO_LANGUAGE[language]}
        theme="vs-dark"
        value={code}
        onChange={(value) => onCodeChange(value ?? "")}
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          scrollBeyondLastLine: false,
          padding: { top: 12 },
        }}
      />
    </div>
  );
}
