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
    "rounded-2xl border border-white/20 px-6 py-3 text-sm uppercase tracking-[0.25em] text-white/90 transition hover:border-teal-300/70 hover:text-white md:px-8 md:py-4 md:text-base"

  return (
    <html lang="en" className={oxanium.variable}>
      <body className="bg-black font-sans antialiased text-white">
        <div className="min-h-screen bg-black text-white">
          <header className="z-20 border-b border-white/10 bg-black/70 backdrop-blur">
            <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-6 px-6 py-6 md:px-10 md:py-8">
              <div className="text-2xl font-semibold uppercase tracking-[0.35em] text-teal-300 md:text-3xl">
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
                <Link href="/us" className={linkClassName}>
                  Us
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
