const stack = [
  { label: "Framework", value: "Next.js App Router" },
  { label: "Styling", value: "Tailwind CSS" },
  { label: "Typography", value: "Oxanium" },
  { label: "Deployment", value: "Vercel-ready" },
]

export default function AboutPage() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0a0a0a] text-white">
      {/* Animated gradient background - matching landing page */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 left-1/4 h-[600px] w-[600px] rounded-full bg-purple-600/20 blur-[120px] animate-pulse" style={{animationDuration: '4s'}} />
        <div className="absolute top-1/3 -right-40 h-[500px] w-[500px] rounded-full bg-pink-600/20 blur-[120px] animate-pulse" style={{animationDuration: '5s', animationDelay: '1s'}} />
        <div className="absolute -bottom-40 left-1/2 h-[550px] w-[550px] rounded-full bg-cyan-600/15 blur-[120px] animate-pulse" style={{animationDuration: '6s', animationDelay: '2s'}} />
      </div>

      {/* Floating particles */}
      <div className="pointer-events-none absolute inset-0">
        {[
          { left: 10, top: 20, duration: 8, delay: 0 },
          { left: 25, top: 60, duration: 10, delay: 2 },
          { left: 40, top: 15, duration: 12, delay: 1 },
          { left: 55, top: 70, duration: 9, delay: 3 },
          { left: 70, top: 30, duration: 11, delay: 1.5 },
          { left: 85, top: 50, duration: 7, delay: 2.5 },
          { left: 15, top: 80, duration: 10, delay: 0.5 },
          { left: 50, top: 40, duration: 8, delay: 4 },
          { left: 90, top: 10, duration: 13, delay: 1 },
          { left: 5, top: 50, duration: 9, delay: 3.5 },
        ].map((particle, i) => (
          <div
            key={i}
            className="absolute h-1 w-1 rounded-full bg-white/20"
            style={{
              left: `${particle.left}%`,
              top: `${particle.top}%`,
              animation: `float ${particle.duration}s ease-in-out infinite`,
              animationDelay: `${particle.delay}s`
            }}
          />
        ))}
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) translateX(0px); opacity: 0; }
          50% { transform: translateY(-100px) translateX(50px); opacity: 1; }
        }
      `}</style>

      <div className="relative z-10 mx-auto max-w-5xl px-6 py-16">
        <div>
          <h1 className="text-3xl font-semibold md:text-5xl">About</h1>
          <p className="mt-4 max-w-2xl text-sm text-white/60 md:text-base">
            A quick snapshot of the tech stack behind the prompt interface.
          </p>
        </div>
        
        <div className="mt-10 grid gap-4 sm:grid-cols-2">
          {stack.map((item) => (
            <div 
              key={item.label} 
              className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm transition-all hover:border-purple-500/50 hover:shadow-[0_0_50px_rgba(168,85,247,0.15)]"
            >
              <p className="text-[10px] uppercase tracking-[0.35em] text-purple-400">{item.label}</p>
              <p className="mt-3 text-lg text-white">{item.value}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}