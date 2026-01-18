import type { Metadata } from "next"
import Link from "next/link"
import { Oxanium } from "next/font/google"
import "./globals.css"

const oxanium = Oxanium({
  subsets: ["latin"],
  variable: "--font-oxanium",
})

export const metadata: Metadata = {
  title: "ADaptiv",
  description: "Minimal front-end UI for video + image prompts.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  const linkClassName =
    "rounded-2xl border border-white/20 px-6 py-3 text-sm font-medium text-white/75 transition hover:border-white/40 hover:text-white md:px-8 md:py-4 md:text-base"

  return (
    <html lang="en" className={oxanium.variable}>
      <body className="bg-black font-sans antialiased text-white">
        <div className="min-h-screen bg-black text-white">
          <header className="sticky top-0 z-20 border-b border-white/10 bg-black/70 backdrop-blur">
            <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-6 px-6 py-6 md:px-10 md:py-8">
              <div className="flex items-center gap-3 text-2xl font-semibold text-purple-300 md:text-3xl">
                <div className="relative flex h-10 w-10 items-center justify-center rounded-full border border-white/15 bg-white/5 shadow-[0_0_24px_rgba(56,189,248,0.25)]">
                  <div className="absolute inset-1 rounded-full bg-gradient-to-br from-purple-500/40 via-fuchsia-400/30 to-cyan-400/30" />
                  <div className="relative h-5 w-5">
                    <div className="absolute inset-0 rounded-full bg-white/10" />
                    <svg viewBox="0 0 24 24" className="relative h-5 w-5 text-white">
                      <path
                        fill="currentColor"
                        d="M8 6.5c0-1 1.1-1.6 2-1l8 5c.9.6.9 1.9 0 2.5l-8 5c-.9.6-2 .1-2-1v-10z"
                      />
                    </svg>
                  </div>
                </div>
                ADaptiv
              </div>
              <nav className="flex flex-wrap items-center gap-2">
                <Link href="/home" className={linkClassName}>
                  Home
                </Link>
                <Link href="/edit" className={linkClassName}>
                  Playground
                </Link>
                <Link href="/about" className={linkClassName}>
                  About
                </Link>
              </nav>
            </div>
          </header>
          {children}
        </div>
      </body>
    </html>
  )
}
