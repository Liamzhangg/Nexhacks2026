export default function HomePage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0b0b0f] text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(31,212,212,0.35),rgba(10,10,14,0))]" />
        <div className="absolute -left-36 top-1/3 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(88,101,242,0.25),rgba(10,10,14,0))]" />
        <div className="absolute bottom-0 right-0 h-[480px] w-[480px] rounded-full bg-[radial-gradient(circle,rgba(236,72,153,0.2),rgba(10,10,14,0))]" />
        <div className="absolute -bottom-32 left-1/4 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(16,185,129,0.18),rgba(10,10,14,0))]" />
      </div>

      <div className="relative z-10 mx-auto flex max-w-5xl flex-col gap-10 px-6 py-20">
        <div className="fade-up">
          <p className="text-xs uppercase tracking-[0.5em] text-teal-300">Nexhacks2026</p>
          <h1 className="mt-6 text-4xl font-semibold md:text-6xl">Design cinematic prompts in minutes.</h1>
          <p className="mt-6 max-w-2xl text-base text-white/70 md:text-lg">
            Upload a video, describe the change, and generate an instant preview. This home page sets the tone for the
            creative flow across the app.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-3 fade-up fade-up-delay-1">
          {[
            { title: "Upload", detail: "Bring your video and reference imagery." },
            { title: "Describe", detail: "Write a clear, cinematic prompt." },
            { title: "Generate", detail: "Review and iterate on the output." },
          ].map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border border-white/10 bg-black/40 p-6 backdrop-blur"
            >
              <p className="text-sm uppercase tracking-[0.3em] text-teal-300">{item.title}</p>
              <p className="mt-4 text-sm text-white/80">{item.detail}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
