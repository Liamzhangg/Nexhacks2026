"use client";

import { Sora } from "next/font/google";
import { useState } from "react";

const sora = Sora({
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
});

export default function HomePage() {
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);

  return (
    <main className={`${sora.className} relative min-h-screen overflow-hidden bg-[#0a0a0a] text-white`}>
      {/* Animated gradient background */}
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
          { left: 35, top: 90, duration: 11, delay: 2 },
          { left: 65, top: 25, duration: 8, delay: 0.8 },
          { left: 80, top: 65, duration: 12, delay: 3 },
          { left: 20, top: 45, duration: 10, delay: 1.2 },
          { left: 45, top: 5, duration: 9, delay: 4.5 },
          { left: 75, top: 85, duration: 11, delay: 0.3 },
          { left: 30, top: 35, duration: 7, delay: 2.8 },
          { left: 60, top: 75, duration: 13, delay: 1.7 },
          { left: 95, top: 55, duration: 8, delay: 3.2 },
          { left: 12, top: 95, duration: 10, delay: 0.9 }
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
        @keyframes glow {
          0%, 100% { box-shadow: 0 0 20px rgba(168, 85, 247, 0.4); }
          50% { box-shadow: 0 0 40px rgba(168, 85, 247, 0.6), 0 0 60px rgba(236, 72, 153, 0.4); }
        }
        @keyframes gradient-shift {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }
        .animated-slogan {
          background-size: 300% 300%;
          animation: gradient-shift 6s ease infinite;
        }
      `}</style>

      {/* Hero Section */}
      <div className="relative z-10 mx-auto flex min-h-screen w-full max-w-none items-center justify-center px-6 pt-20 pb-32">
        <div className="text-center">
          <h1 className="text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-black leading-[1.05] mb-8">
            <span className="block text-white">Make Every Ad</span>
            <span className="animated-slogan block bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
              <span className="block">Relevant.</span>
              <span className="block">Personal.</span>
              <span className="block">Local.</span>
            </span>
          </h1>

          <p className="mx-auto max-w-3xl text-xl text-white/60 leading-relaxed mb-12">
            Post-production product placement that adapts to your audience. With one scene, generate seamless product
            placements that obey physics.
            <span className="mt-3 block text-white/90 font-semibold">One scene, endless ad adaption potential</span>
          </p>
          <div className="flex flex-col items-center justify-center mb-12 text-white/70">
            <span className="text-sm font-semibold uppercase tracking-[0.3em]">See the capabilities</span>
            <svg className="mt-2 h-5 w-5 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          {/* Video Preview Card */}
          <div className="relative mx-auto mt-8 w-full max-w-none">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 blur-3xl rounded-3xl" />
            <div className="relative rounded-3xl border border-white/10 bg-gradient-to-b from-white/10 to-white/5 backdrop-blur-xl overflow-hidden">
              <div className="p-4 sm:p-6 lg:p-8">
                {/* Mock video player */}
                <div className="relative aspect-video rounded-2xl bg-gradient-to-br from-gray-900 to-black border border-white/10 overflow-hidden group">
                  {/* Video thumbnail effect */}
                  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_0%,_rgba(0,0,0,0.8)_100%)]" />
                  
                  {/* Product placements showcase */}
                  <div className="absolute inset-0 flex items-center justify-center gap-12">
                    <div className="text-center transform -rotate-6 transition-transform group-hover:rotate-0 group-hover:scale-110">
                      <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 border border-white/20 flex items-center justify-center mb-3 shadow-2xl">
                        <span className="text-4xl">📱</span>
                      </div>
                      <div className="text-xs text-white/60">USA: iPhone</div>
                    </div>
                    <div className="text-center transition-transform group-hover:scale-110">
                      <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 border border-white/20 flex items-center justify-center mb-3 shadow-2xl">
                        <span className="text-4xl">📱</span>
                      </div>
                      <div className="text-xs text-white/60">China: Huawei</div>
                    </div>
                    <div className="text-center transform rotate-6 transition-transform group-hover:rotate-0 group-hover:scale-110">
                      <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-gray-800 to-gray-900 border border-white/20 flex items-center justify-center mb-3 shadow-2xl">
                        <span className="text-4xl">📱</span>
                      </div>
                      <div className="text-xs text-white/60">Nigeria: Tecno</div>
                    </div>
                  </div>

                  {/* Play button overlay */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <button className="h-20 w-20 rounded-full bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center transition-all hover:scale-110 hover:bg-white/20 group-hover:shadow-[0_0_40px_rgba(168,85,247,0.6)]">
                      <svg className="h-8 w-8 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </button>
                  </div>
                </div>

                {/* Edit button */}
                <div className="flex justify-center mt-8">
                  <a
                    href="/edit"
                    className="group relative rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 px-12 py-4 text-lg font-bold shadow-2xl shadow-purple-500/50 transition-all hover:scale-105 hover:shadow-purple-500/70"
                    style={{ animation: "glow 3s ease-in-out infinite" }}
                  >
                    <span className="relative z-10 flex items-center gap-3">
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                      Start Editing
                      <svg
                        className="h-5 w-5 transition-transform group-hover:translate-x-1"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </span>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

      

      </div>
    </main>
  );
}