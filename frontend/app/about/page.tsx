const stack = [
  { label: "AI Models", value: "Gemini & SAM 3" },
  { label: "Backend", value: "Python & FastAPI" },
  { label: "Frontend", value: "Next.js & TypeScript" },
  { label: "Deep Learning", value: "PyTorch & ComfyUI" },
  { label: "Infrastructure", value: "Vast.ai GPU Compute" },
  { label: "Styling", value: "Tailwind CSS" },
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
          <h1 className="text-3xl font-semibold md:text-5xl">Adaptive Post-Production Product Placement</h1>
          <p className="mt-6 max-w-3xl text-base text-white/70 md:text-lg leading-relaxed">
            Traditional product placement in movies is static, generalized, and often irrelevant to global audiences. We built a post-production system that dynamically replaces branded objects in videos based on viewer context—without reshooting or altering the storyline.
          </p>
          <p className="mt-4 max-w-3xl text-sm text-purple-400 md:text-base font-medium">
            Instead of changing the movie, we change the ads inside the movie.
          </p>
        </div>

        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-6">How It Works</h2>
          <div className="space-y-6">
            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-purple-400 mb-3">1. Video Input & User Control</h3>
              <p className="text-sm text-white/60 leading-relaxed">
                Users can submit full videos for automatic detection or use manual on-screen selection to target specific regions. This creates a lightweight video-editing workflow combining user intent with automated understanding.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-purple-400 mb-3">2. Video Understanding with Gemini</h3>
              <p className="text-sm text-white/60 leading-relaxed">
                Gemini watches the video end-to-end, identifies frames containing relevant branded objects, and filters semantically meaningful scenes based on user requests and manual selections.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-purple-400 mb-3">3. Object Segmentation with SAM 3</h3>
              <p className="text-sm text-white/60 leading-relaxed">
                SAM 3 (Segment Anything Model v3) performs precise pixel-accurate object segmentation, handling occlusion, lighting consistency, and perspective to generate masks for selected objects.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <h3 className="text-lg font-semibold text-purple-400 mb-3">4. Brand Replacement</h3>
              <p className="text-sm text-white/60 leading-relaxed">
                Using generated masks, we apply post-production inpainting and embedding with ComfyUI to replace brands with context-aware alternatives based on location, availability, and viewer relevance.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-6">Tech Stack</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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

        <div className="mt-12">
          <h2 className="text-2xl font-semibold mb-6">Example Use Cases</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <p className="text-white/80 leading-relaxed">iPhones in U.S. releases → <span className="text-purple-400 font-medium">Huawei</span> for China</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <p className="text-white/80 leading-relaxed">Starbucks cups → <span className="text-purple-400 font-medium">Milo</span> in regions without Starbucks</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <p className="text-white/80 leading-relaxed">Ford F-150 → <span className="text-purple-400 font-medium">VW Golf</span> for viewers in Germany</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-6 backdrop-blur-sm">
              <p className="text-white/80 leading-relaxed">Coke cans → <span className="text-purple-400 font-medium">Pepsi</span> in local markets</p>
            </div>
          </div>
        </div>

        <div className="mt-12 rounded-2xl border border-purple-500/30 bg-gradient-to-b from-purple-500/10 to-transparent p-8 backdrop-blur-sm">
          <h2 className="text-2xl font-semibold mb-4">Why It Matters</h2>
          <p className="text-lg text-white/80 leading-relaxed">
            Instead of advertising at everyone, we advertise to the right audience. This system transforms static product placement into a dynamic, personalized advertising layer without breaking immersion—no reshoots required, post-production only, and scalable to long-form content.
          </p>
        </div>
      </div>
    </main>
  )
}