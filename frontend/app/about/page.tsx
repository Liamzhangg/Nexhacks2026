const stack = [
  { label: "Framework", value: "Next.js App Router" },
  { label: "Styling", value: "Tailwind CSS" },
  { label: "Typography", value: "Oxanium" },
  { label: "Deployment", value: "Vercel-ready" },
]

export default function AboutPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">
      <div className="pointer-events-none absolute -top-28 left-10 h-64 w-64 rounded-full bg-teal-500/20 blur-[130px]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 rounded-full bg-emerald-400/20 blur-[160px]" />

      <div className="relative z-10 mx-auto max-w-5xl px-6 py-16">
        <div className="fade-up">
          <h1 className="text-3xl font-semibold md:text-5xl">About</h1>
          <p className="mt-4 max-w-2xl text-sm text-gray-300 md:text-base">
            A quick snapshot of the tech stack behind the prompt interface.
          </p>
        </div>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 fade-up fade-up-delay-1">
          {stack.map((item) => (
            <div key={item.label} className="rounded-2xl border border-white/10 bg-black/70 p-5 backdrop-blur">
              <p className="text-[10px] uppercase tracking-[0.35em] text-teal-300">{item.label}</p>
              <p className="mt-3 text-lg text-white">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
