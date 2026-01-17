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
    <main className="relative min-h-screen overflow-hidden bg-black text-white">
      <div className="pointer-events-none absolute -top-36 right-16 h-64 w-64 rounded-full bg-teal-500/20 blur-[130px]" />
      <div className="pointer-events-none absolute -bottom-28 left-0 h-72 w-72 rounded-full bg-emerald-400/20 blur-[150px]" />

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
