"use client"

import { useEffect, useState } from "react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000"

export default function EditPage() {
  const [prompt, setPrompt] = useState("")
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [localVideoUrl, setLocalVideoUrl] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      if (localVideoUrl) URL.revokeObjectURL(localVideoUrl)
    }
  }, [previewUrl, localVideoUrl])

  const handleVideoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setVideoFile(file)
    setPreviewUrl(null)
    setError(null)
    if (localVideoUrl) URL.revokeObjectURL(localVideoUrl)
    setLocalVideoUrl(file ? URL.createObjectURL(file) : null)
  }

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setImageFile(file)
  }

  const handleSubmit = async () => {
    if (!videoFile) {
      setError("Please upload a video before processing.")
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append("video", videoFile)
      formData.append("text", prompt)

      const response = await fetch(`${API_BASE_URL}/process-video`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        throw new Error(payload?.error ?? "Processing failed.")
      }

      const blob = await response.blob()
      const nextUrl = URL.createObjectURL(blob)
      setPreviewUrl(nextUrl)
    } catch (fetchError) {
      const message = fetchError instanceof Error ? fetchError.message : "Processing failed."
      setError(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="relative h-[calc(100vh-140px)] overflow-hidden bg-[#0b0b0f] text-base text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(31,212,212,0.35),rgba(10,10,14,0))]" />
        <div className="absolute -left-36 top-1/3 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(88,101,242,0.25),rgba(10,10,14,0))]" />
        <div className="absolute bottom-0 right-0 h-[480px] w-[480px] rounded-full bg-[radial-gradient(circle,rgba(236,72,153,0.2),rgba(10,10,14,0))]" />
        <div className="absolute -bottom-32 left-1/4 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(16,185,129,0.18),rgba(10,10,14,0))]" />
      </div>
      <div className="relative isolate flex h-full flex-col overflow-hidden">
        <div className="relative z-10 flex h-full w-full flex-col">
          <div className="w-full px-4 pt-10 lg:px-10">
            <div className="mx-auto grid w-full max-w-[96rem] grid-cols-1 gap-3 rounded-2xl border border-[#2f2f2f] bg-[#15151a]/90 px-4 py-4 shadow-[0_20px_40px_-30px_rgba(0,0,0,0.7)] sm:grid-cols-3 sm:items-stretch">
              <label className="group flex w-full cursor-pointer items-center justify-center rounded-xl border border-dashed border-[#3a3a3a] bg-[#23232b] px-4 py-3 text-center transition hover:border-[#4a4a4a] hover:bg-[#2b2b34]">
                <span className="font-semibold text-white">Upload video</span>
                {videoFile ? <span className="ml-3 text-sm text-white">{videoFile.name}</span> : null}
                <input type="file" accept="video/*" className="sr-only" onChange={handleVideoChange} />
              </label>
              <label className="group flex w-full cursor-pointer items-center justify-center rounded-xl border border-dashed border-[#3a3a3a] bg-[#23232b] px-4 py-3 text-center transition hover:border-[#4a4a4a] hover:bg-[#2b2b34]">
                <span className="font-semibold text-white">Upload image</span>
                {imageFile ? <span className="ml-3 text-sm text-white">{imageFile.name}</span> : null}
                <input type="file" accept="image/*" className="sr-only" onChange={handleImageChange} />
              </label>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="w-full rounded-xl bg-[#23232b] px-6 py-3 font-semibold text-white transition hover:bg-[#2b2b34] disabled:cursor-not-allowed disabled:bg-[#23232b]/60"
              >
                {isSubmitting ? "Processing..." : "Generate video"}
              </button>
            </div>
          </div>

          <div className="mx-auto flex h-full w-full max-w-[96rem] flex-1 flex-col px-6 py-4 lg:px-10">
            <div className="flex flex-1 flex-col gap-6 fade-up fade-up-delay-1 lg:flex-row lg:items-stretch">
              <section className="flex flex-col lg:w-[45%]">
              <textarea
                name="prompt"
                placeholder="Describe what you would like changed"
                  className="h-full w-full flex-1 resize-none rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-6 text-white outline-none transition placeholder:text-white/60 focus:border-[#4a4a4a] md:p-8"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
              />
              {error ? <p className="mt-4 text-rose-300">{error}</p> : null}
              </section>
              <section className="flex flex-1 flex-col lg:pl-0">
                <div className="flex h-full flex-1 items-center justify-center rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-6 md:p-8">
                {previewUrl || localVideoUrl ? (
                  <video
                    key={previewUrl ?? localVideoUrl ?? "preview"}
                    controls
                      className="h-full w-full rounded-2xl bg-black"
                  >
                    <source src={previewUrl ?? localVideoUrl ?? undefined} />
                  </video>
                ) : (
                    <div className="flex h-full w-full flex-col items-center justify-center gap-2 text-center text-white/70">
                    <span className="text-white">Video preview</span>
                    <span className="uppercase tracking-[0.2em] text-white/60">placeholder</span>
                  </div>
                )}
              </div>
              </section>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
