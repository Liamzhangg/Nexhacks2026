export default function DemoPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0b0b0f] text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(31,212,212,0.35),rgba(10,10,14,0))]" />
        <div className="absolute -left-36 top-1/3 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(88,101,242,0.25),rgba(10,10,14,0))]" />
        <div className="absolute bottom-0 right-0 h-[480px] w-[480px] rounded-full bg-[radial-gradient(circle,rgba(236,72,153,0.2),rgba(10,10,14,0))]" />
        <div className="absolute -bottom-32 left-1/4 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(16,185,129,0.18),rgba(10,10,14,0))]" />
      </div>

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
