export default function DemoPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">
      <div className="pointer-events-none absolute -top-36 right-10 h-64 w-64 rounded-full bg-teal-500/20 blur-[130px]" />
      <div className="pointer-events-none absolute -bottom-24 left-0 h-72 w-72 rounded-full bg-emerald-400/20 blur-[150px]" />

      <div className="relative z-10 mx-auto max-w-5xl px-6 py-16">
        <div className="fade-up">
          <h1 className="text-3xl font-semibold md:text-5xl">Demo</h1>
          <p className="mt-4 max-w-2xl text-sm text-gray-300 md:text-base">
            Drop your demo experience here. This section is ready for an embedded prototype, video, or interactive
            preview.
          </p>
        </div>

        <div className="mt-10 rounded-2xl border border-white/10 bg-black/70 p-6 backdrop-blur md:p-8 fade-up fade-up-delay-1">
          <div className="flex aspect-video w-full items-center justify-center rounded-xl border border-dashed border-white/20 text-sm text-gray-400">
            Demo placeholder
          </div>
        </div>
      </div>
    </main>
  )
}
