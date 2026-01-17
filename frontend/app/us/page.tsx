const team = [
  {
    name: "Your Name",
    role: "Product / Design",
    note: "Guiding the interface and overall experience.",
  },
  {
    name: "Teammate",
    role: "Engineering",
    note: "Building the interactive flow and polish.",
  },
]

export default function UsPage() {
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
          <h1 className="text-3xl font-semibold md:text-5xl">Us</h1>
          <p className="mt-4 max-w-2xl text-sm text-gray-300 md:text-base">
            The people shaping the Nexhacks2026 experience.
          </p>
        </div>

        <div className="mt-10 grid gap-4 md:grid-cols-2 fade-up fade-up-delay-1">
          {team.map((person) => (
            <div key={person.name} className="rounded-2xl border border-white/10 bg-black/70 p-6 backdrop-blur">
              <p className="text-sm text-white">{person.name}</p>
              <p className="mt-2 text-[11px] uppercase tracking-[0.35em] text-teal-300">{person.role}</p>
              <p className="mt-4 text-sm text-gray-300">{person.note}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
