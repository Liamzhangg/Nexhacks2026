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
    <main className="h-[calc(100vh-150px)] overflow-hidden bg-black text-base text-white">
      <div className="relative isolate overflow-hidden">
        <div className="relative z-10 w-full">
          <div className="w-full px-4 pt-10 lg:px-8">
            <div className="mx-auto flex w-full max-w-[88rem] flex-col gap-3 rounded-2xl border border-[#2f2f2f] bg-[#1b1b1b] px-4 py-4 shadow-[0_20px_40px_-30px_rgba(0,0,0,0.7)] sm:flex-row sm:items-center">
              <label className="group flex flex-1 cursor-pointer items-center justify-center rounded-xl border border-dashed border-[#3a3a3a] bg-[#2a2a2a] px-4 py-3 text-center transition hover:border-[#4a4a4a] hover:bg-[#323232]">
                <span className="font-semibold text-white">upload video</span>
                <span className="ml-3 text-sm text-white/70">MP4, MOV, WebM</span>
                {videoFile ? <span className="ml-3 text-sm text-white">{videoFile.name}</span> : null}
                <input type="file" accept="video/*" className="sr-only" onChange={handleVideoChange} />
              </label>
              <label className="group flex flex-1 cursor-pointer items-center justify-center rounded-xl border border-dashed border-[#3a3a3a] bg-[#2a2a2a] px-4 py-3 text-center transition hover:border-[#4a4a4a] hover:bg-[#323232]">
                <span className="font-semibold text-white">upload image</span>
                <span className="ml-3 text-sm text-white/70">PNG, JPG, HEIC</span>
                {imageFile ? <span className="ml-3 text-sm text-white">{imageFile.name}</span> : null}
                <input type="file" accept="image/*" className="sr-only" onChange={handleImageChange} />
              </label>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="rounded-xl bg-[#2a2a2a] px-6 py-3 font-semibold text-white transition hover:bg-[#323232] disabled:cursor-not-allowed disabled:bg-[#2a2a2a]/60 sm:max-w-[200px]"
              >
                {isSubmitting ? "Processing..." : "Generate video"}
              </button>
            </div>
          </div>

          <div className="mx-auto flex h-full w-full max-w-[88rem] flex-col px-6 py-4 lg:px-8">
            <div className="flex flex-1 flex-col gap-6 fade-up fade-up-delay-1 lg:flex-row lg:items-stretch">
            <section className="flex flex-col lg:w-[40%]">
              <textarea
                name="prompt"
                placeholder="Describe what you would like changed"
                className="min-h-[315px] w-full flex-1 resize-none rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-6 text-white outline-none transition placeholder:text-white/60 focus:border-[#4a4a4a] md:min-h-[390px] md:p-8"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
              />
              {error ? <p className="mt-4 text-rose-300">{error}</p> : null}
            </section>
            <section className="flex flex-1 flex-col lg:pl-0">
              <div className="flex flex-1 items-center justify-center rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-6 md:p-8">
                {previewUrl || localVideoUrl ? (
                  <video
                    key={previewUrl ?? localVideoUrl ?? "preview"}
                    controls
                    className="h-full max-h-[430px] w-full rounded-2xl bg-black"
                  >
                    <source src={previewUrl ?? localVideoUrl ?? undefined} />
                  </video>
                ) : (
                  <div className="flex min-h-[315px] flex-col items-center justify-center gap-2 text-center text-white/70 md:min-h-[390px]">
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
