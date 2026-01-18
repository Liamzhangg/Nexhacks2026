"use client";

import { useState } from 'react';

export default function HomePage() {
  const [hoveredCard, setHoveredCard] = useState(null);

  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0a0a0a] text-white">
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
      `}</style>

      {/* Header */}
      <header className="relative z-20 px-8 py-6">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 blur-md opacity-75" />
              <div className="relative h-10 w-10 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                </svg>
              </div>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">AdaptiveAds</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm text-white/60">
          </nav>
          <button className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-2.5 text-sm font-semibold shadow-lg shadow-purple-500/25 transition-all hover:scale-105 hover:shadow-xl hover:shadow-purple-500/40">
            Get Started
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <div className="relative z-10 mx-auto max-w-7xl px-6 pt-20 pb-32">
        <div className="text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-4 py-2 backdrop-blur-sm mb-8">
            <div className="h-2 w-2 rounded-full bg-purple-400 animate-pulse" />
            <span className="text-xs font-medium text-purple-300">Revolutionizing Post-Production Advertising</span>
          </div>

          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black leading-[1.1] mb-8">
            <span className="block">Make Every Ad</span>
            <span className="block bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
              Relevant. Personal. Local.
            </span>
          </h1>

          <p className="mx-auto max-w-3xl text-xl text-white/60 leading-relaxed mb-12">
            Post-production product placement that adapts to your audience. Show iPhones in America, 
            Huawei in China, Tecno in Nigeria. <span className="text-white/80 font-medium">One movie, infinite possibilities.</span>
          </p>

          {/* Video Preview Card */}
          <div className="relative mx-auto max-w-5xl mt-16">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20 blur-3xl rounded-3xl" />
            <div className="relative rounded-3xl border border-white/10 bg-gradient-to-b from-white/10 to-white/5 backdrop-blur-xl overflow-hidden">
              <div className="p-8">
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
                  <button className="group relative rounded-2xl bg-gradient-to-r from-purple-600 to-pink-600 px-12 py-4 text-lg font-bold shadow-2xl shadow-purple-500/50 transition-all hover:scale-105 hover:shadow-purple-500/70" style={{animation: 'glow 3s ease-in-out infinite'}}>
                    <span className="relative z-10 flex items-center gap-3">
                      <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      Start Editing
                      <svg className="h-5 w-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mt-32 grid md:grid-cols-3 gap-6">
          {[
            {
              icon: (
                <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ),
              title: "Global Localization",
              desc: "Automatically adapt products for every region, culture, and demographic"
            },
            {
              icon: (
                <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              ),
              title: "AI-Powered",
              desc: "Machine learning identifies placement opportunities and optimizes conversions"
            },
            {
              icon: (
                <svg className="h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ),
              title: "Maximize Revenue",
              desc: "Show relevant products that viewers can actually buy and increase ROI"
            }
          ].map((feature, i) => (
            <div
              key={i}
              onMouseEnter={() => setHoveredCard(i)}
              onMouseLeave={() => setHoveredCard(null)}
              className="group relative rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-8 backdrop-blur-sm transition-all hover:border-purple-500/50 hover:shadow-[0_0_50px_rgba(168,85,247,0.15)]"
            >
              <div className={`mb-6 inline-flex rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 p-4 text-purple-400 transition-all ${hoveredCard === i ? 'scale-110 rotate-6' : ''}`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
              <p className="text-white/60 leading-relaxed">{feature.desc}</p>
            </div>
          ))}
        </div>


      </div>
    </main>
  );
}