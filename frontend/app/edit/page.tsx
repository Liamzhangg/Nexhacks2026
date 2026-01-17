"use client"

import { useEffect, useRef, useState } from "react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000"

export default function EditPage() {
  const [mode, setMode] = useState<"prompt" | "manual">("prompt")
  const [prompt, setPrompt] = useState("")
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [localVideoUrl, setLocalVideoUrl] = useState<string | null>(null)
  const [videoDuration, setVideoDuration] = useState<number | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(1)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const manualVideoRef = useRef<HTMLVideoElement | null>(null)

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
    setVideoDuration(null)
    setCurrentTime(0)
    setIsPlaying(false)
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

  const timelineProgress = videoDuration ? Math.min(100, (currentTime / videoDuration) * 100) : 0

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
          <div className="w-full px-4 pt-6 lg:px-10">
            <div className="mx-auto flex w-full max-w-[96rem] flex-col gap-4 rounded-2xl border border-[#2f2f2f] bg-[#15151a]/90 px-4 py-4 shadow-[0_20px_40px_-30px_rgba(0,0,0,0.7)] lg:flex-row lg:items-center lg:justify-between">
              <div className="flex w-full flex-col gap-3 sm:flex-row lg:w-auto">
                {(["prompt", "manual"] as const).map((nextMode) => {
                  const isActive = mode === nextMode
                  return (
                    <button
                      key={nextMode}
                      type="button"
                      onClick={() => setMode(nextMode)}
                      className={`rounded-xl px-6 py-3 text-sm font-semibold uppercase tracking-[0.2em] transition ${
                        isActive
                          ? "border border-teal-300/60 bg-teal-300/10 text-teal-200"
                          : "border border-white/15 bg-[#23232b] text-white/80 hover:border-white/30"
                      }`}
                    >
                      {nextMode}
                    </button>
                  )
                })}
              </div>
              <div className="grid w-full grid-cols-1 gap-3 sm:grid-cols-3 lg:w-[62%]">
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
          </div>

          <div className="mx-auto flex h-full w-full max-w-[96rem] flex-1 flex-col px-6 py-4 lg:px-10">
            {mode === "manual" ? (
              <div className="relative flex flex-1 flex-col fade-up fade-up-delay-1">
                <section className="flex min-h-0 flex-1 flex-col pb-[230px]">
                  <div className="flex h-full max-h-[calc(100vh-520px)] flex-1 items-center justify-center overflow-hidden rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-4 md:p-6">
                    {previewUrl || localVideoUrl ? (
                      <video
                        key={previewUrl ?? localVideoUrl ?? "preview"}
                        ref={manualVideoRef}
                        onLoadedMetadata={(event) => {
                          setVideoDuration(event.currentTarget.duration)
                          setCurrentTime(0)
                          event.currentTarget.volume = volume
                        }}
                        onTimeUpdate={(event) => setCurrentTime(event.currentTarget.currentTime)}
                        onPlay={() => setIsPlaying(true)}
                        onPause={() => setIsPlaying(false)}
                        className="max-h-full max-w-full rounded-2xl bg-black object-contain"
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
                <section className="fixed bottom-24 left-0 right-0 z-20">
                  <div className="mx-auto flex h-[120px] max-w-[96rem] px-6 lg:px-10">
                    <div className="flex h-full w-full flex-col rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-4">
                    <div className="rounded-2xl border border-white/10 bg-black/40 p-3">
                      {videoDuration ? (
                        <div className="flex flex-col gap-3">
                          <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-white/50">
                            <span>Timeline</span>
                            <span>00:00 → {Math.ceil(videoDuration)}s</span>
                          </div>
                          <div className="relative h-16 overflow-hidden rounded-xl border border-white/10 bg-gradient-to-r from-[#1a1a24] via-[#2a2a2f] to-[#1a1a24]">
                            <div className="absolute inset-y-0 left-0 bg-teal-300/20" style={{ width: `${timelineProgress}%` }} />
                            <div
                              className="absolute inset-y-0 w-[2px] bg-teal-300"
                              style={{ left: `${timelineProgress}%` }}
                            />
                            <input
                              type="range"
                              min={0}
                              max={videoDuration ?? 0}
                              step={0.01}
                              value={currentTime}
                              disabled={!videoDuration}
                              onChange={(event) => {
                                const next = Number(event.target.value)
                                setCurrentTime(next)
                                if (manualVideoRef.current) {
                                  manualVideoRef.current.currentTime = next
                                }
                              }}
                              className="absolute inset-0 z-10 h-full w-full cursor-pointer opacity-0"
                            />
                            <div className="absolute inset-0 z-0 flex items-end justify-between px-3 pb-3">
                              {Array.from({ length: Math.min(12, Math.max(4, Math.ceil(videoDuration / 4))) }).map(
                                (_, index) => (
                                  <div key={index} className="flex flex-col items-center gap-2">
                                    <div className="h-6 w-[2px] rounded-full bg-white/40" />
                                    <span className="text-[10px] text-white/50">
                                      {Math.round((videoDuration / Math.min(12, Math.max(4, Math.ceil(videoDuration / 4)))) * index)}
                                      s
                                    </span>
                                  </div>
                                )
                              )}
                            </div>
                          </div>
                          <div className="flex flex-wrap items-center gap-3 text-xs text-white/60">
                            <button
                              type="button"
                              className="rounded-full border border-white/10 bg-black/40 px-3 py-1"
                              onClick={() => {
                                const video = manualVideoRef.current
                                if (!video) return
                                if (video.paused) {
                                  video.play().catch(() => {})
                                } else {
                                  video.pause()
                                }
                              }}
                              disabled={!videoDuration}
                            >
                              {isPlaying ? "Pause" : "Play"}
                            </button>
                            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-black/40 px-3 py-1">
                              <span>Vol</span>
                              <input
                                type="range"
                                min={0}
                                max={1}
                                step={0.01}
                                value={volume}
                                onChange={(event) => {
                                  const next = Number(event.target.value)
                                  setVolume(next)
                                  if (manualVideoRef.current) {
                                    manualVideoRef.current.volume = next
                                  }
                                }}
                                className="h-1 w-24 accent-teal-300"
                              />
                            </div>
                            <div className="rounded-full border border-white/10 bg-black/40 px-3 py-1">
                              {new Date(currentTime * 1000).toISOString().slice(14, 19)} /{" "}
                              {new Date((videoDuration ?? 0) * 1000).toISOString().slice(14, 19)}
                            </div>
                            <div className="rounded-full border border-white/10 bg-black/40 px-3 py-1">
                              Drag timeline above to scrub
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="flex h-28 items-center justify-center text-sm text-white/60">
                          Upload a video to see the manual timeline.
                        </div>
                      )}
                    </div>
                  </div>
                </div>
                </section>
              </div>
            ) : (
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
                  <div className="flex h-full max-h-[calc(100vh-320px)] flex-1 items-center justify-center overflow-hidden rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-6 md:p-8">
                {previewUrl || localVideoUrl ? (
                  <video
                    key={previewUrl ?? localVideoUrl ?? "preview"}
                        onLoadedMetadata={(event) => setVideoDuration(event.currentTarget.duration)}
                    controls
                        className="max-h-full max-w-full rounded-2xl bg-black object-contain"
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
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
