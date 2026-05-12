export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-zinc-950 text-white px-4">
      <div className="text-center max-w-2xl">
        <h1 className="text-5xl font-bold tracking-tight mb-4">
          Dev<span className="text-sky-400">Pulse</span>
        </h1>
        <p className="text-zinc-400 text-lg mb-8">
          Code performance analysis, powered by C++ and AI.
        </p>
        <a
          href="/analyze"
          className="inline-block bg-sky-500 hover:bg-sky-400 text-white font-semibold px-8 py-3 rounded-lg transition-colors"
        >
          Analyze Your Code
        </a>
      </div>
    </main>
  );
}
