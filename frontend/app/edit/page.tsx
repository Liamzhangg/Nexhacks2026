"use client"

import { useEffect, useRef, useState } from "react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

type CloudglueTimestamp = {
  start_time: number
  end_time: number
}

type CloudglueItem = {
  label: string
  description: string
  timestamps: CloudglueTimestamp[]
}

type CloudglueResponse = {
  target_description: string
  items: CloudglueItem[]
}

export default function EditPage() {
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [localVideoUrl, setLocalVideoUrl] = useState<string | null>(null)
  const [videoDuration, setVideoDuration] = useState<number | null>(null)
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(1)
  const [clipStart, setClipStart] = useState(0)
  const [clipEnd, setClipEnd] = useState<number | null>(null)
  const [cloudglueOutput, setCloudglueOutput] = useState<CloudglueResponse | null>(null)
  const [selectedItems, setSelectedItems] = useState<Record<string, boolean>>({})
  const [flowStep, setFlowStep] = useState<"edit" | "select">("edit")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const manualVideoRef = useRef<HTMLVideoElement | null>(null)
  const timelineRef = useRef<HTMLDivElement | null>(null)
  const [draggingHandle, setDraggingHandle] = useState<"start" | "end" | null>(null)
  const selectionRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
      if (localVideoUrl) URL.revokeObjectURL(localVideoUrl)
    }
  }, [previewUrl, localVideoUrl])

  useEffect(() => {
    if (!cloudglueOutput) return
    const initial: Record<string, boolean> = {}
    cloudglueOutput.items.forEach((item, index) => {
      initial[`${item.label}-${index}`] = true
    })
    setSelectedItems(initial)
  }, [cloudglueOutput])

  const handleVideoChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setVideoFile(file)
    setPreviewUrl(null)
    setError(null)
    setVideoDuration(null)
    setCurrentTime(0)
    setIsPlaying(false)
    setClipStart(0)
    setClipEnd(null)
    setCloudglueOutput(null)
    setFlowStep("edit")
    if (localVideoUrl) URL.revokeObjectURL(localVideoUrl)
    setLocalVideoUrl(file ? URL.createObjectURL(file) : null)
  }

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    setImageFile(file)
  }

  const trimVideo = async (file: File, startTime: number, endTime: number) => {
    const duration = endTime - startTime
    if (duration < 2) {
      throw new Error(`Trim duration too short: ${duration}s (minimum 2s required)`)
    }
    if (endTime <= startTime) {
      throw new Error("Invalid trim range.")
    }

    const video = document.createElement("video")
    const objectUrl = URL.createObjectURL(file)
    video.src = objectUrl
    video.muted = true
    video.playsInline = true

    await new Promise<void>((resolve, reject) => {
      video.onloadedmetadata = () => resolve()
      video.onerror = () => reject(new Error("Failed to load video metadata."))
    })

    const videoDuration = video.duration
    const safeStart = Math.max(0, Math.min(startTime, videoDuration))
    const safeEnd = Math.max(safeStart + 2, Math.min(endTime, videoDuration))

    video.currentTime = safeStart
    await new Promise<void>((resolve, reject) => {
      video.onseeked = () => resolve()
      video.onerror = () => reject(new Error("Failed to seek video."))
    })

    const stream = video.captureStream()
    const chunks: Blob[] = []
    const recorder = new MediaRecorder(stream, { mimeType: "video/webm" })

    const result = await new Promise<Blob>((resolve, reject) => {
      recorder.ondataavailable = (event) => {
        if (event.data.size) chunks.push(event.data)
      }
      recorder.onerror = () => reject(new Error("Recording failed."))
      recorder.onstop = () => resolve(new Blob(chunks, { type: "video/webm" }))

      recorder.start(100)
      video.play().catch(() => {})

      const interval = window.setInterval(() => {
        if (video.currentTime >= safeEnd) {
          recorder.stop()
          video.pause()
          window.clearInterval(interval)
        }
      }, 50)
    })

    stream.getTracks().forEach((track) => track.stop())
    URL.revokeObjectURL(objectUrl)

    return result
  }

  const formatTimestamp = (seconds: number) => {
    if (!Number.isFinite(seconds)) return "00:00"
    const totalSeconds = Math.max(0, Math.floor(seconds))
    const minutes = Math.floor(totalSeconds / 60)
    const remaining = totalSeconds % 60
    return `${String(minutes).padStart(2, "0")}:${String(remaining).padStart(2, "0")}`
  }

  const clampRangeToDuration = (start: number, end: number, duration: number | null) => {
    if (!Number.isFinite(start) || !Number.isFinite(end)) return null
    const safeDuration = duration ?? end
    const clampedStart = Math.max(0, Math.min(start, safeDuration))
    const clampedEnd = Math.max(clampedStart, Math.min(end, safeDuration))
    return { start: clampedStart, end: clampedEnd }
  }

  const handleSubmit = async () => {
    if (!videoFile) {
      setError("Please upload a video before processing.")
      return
    }
    if (!imageFile) {
      setError("Please upload an image before processing.")
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const formData = new FormData()

      let videoToSend: Blob | File = videoFile

      formData.append("video", videoToSend, videoFile.name)
      if (imageFile) {
        formData.append("image", imageFile)
      }

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        throw new Error(payload?.error ?? "Processing failed.")
      }

      if ((response.headers.get("content-type") ?? "").includes("application/json")) {
        const payload = (await response.json()) as CloudglueResponse
        if (payload?.items) {
          setCloudglueOutput(payload)
          setFlowStep("select")
          requestAnimationFrame(() => {
            selectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
          })
          return
        }
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
  const startPercent = videoDuration ? Math.min(100, (clipStart / videoDuration) * 100) : 0
  const endPercent = videoDuration && clipEnd != null ? Math.min(100, (clipEnd / videoDuration) * 100) : 100

  const getTimeFromPointer = (clientX: number) => {
    if (!timelineRef.current || !videoDuration) return null
    const rect = timelineRef.current.getBoundingClientRect()
    const clamped = Math.min(rect.right, Math.max(rect.left, clientX))
    const percent = (clamped - rect.left) / rect.width
    return percent * videoDuration
  }

  const clampToClip = (time: number) => {
    if (clipEnd == null) return Math.max(clipStart, time)
    return Math.min(Math.max(time, clipStart), clipEnd)
  }

  const handleGenerateSelected = async () => {
    if (!videoFile || !cloudglueOutput) return
    if (!imageFile) {
      setError("Please upload an image before generating.")
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append("video", videoFile, videoFile.name)
      formData.append("image", imageFile)
      const selectedTargets = cloudglueOutput.items.filter((item, index) => {
        const key = `${item.label}-${index}`
        return selectedItems[key]
      })
      formData.append("targets", JSON.stringify(selectedTargets))

      const response = await fetch(`${API_BASE_URL}/generate`, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const payload = await response.json().catch(() => null)
        throw new Error(payload?.error ?? "Generate failed.")
      }

      const blob = await response.blob()
      const nextUrl = URL.createObjectURL(blob)
      setPreviewUrl(nextUrl)
    } catch (fetchError) {
      const message = fetchError instanceof Error ? fetchError.message : "Generate failed."
      setError(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="relative h-[calc(100vh-140px)] overflow-y-auto bg-[#0b0b0f] text-base text-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 left-1/2 h-[520px] w-[520px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,rgba(31,212,212,0.35),rgba(10,10,14,0))]" />
        <div className="absolute -left-36 top-1/3 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(88,101,242,0.25),rgba(10,10,14,0))]" />
        <div className="absolute bottom-0 right-0 h-[480px] w-[480px] rounded-full bg-[radial-gradient(circle,rgba(236,72,153,0.2),rgba(10,10,14,0))]" />
        <div className="absolute -bottom-32 left-1/4 h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(16,185,129,0.18),rgba(10,10,14,0))]" />
      </div>
      <div className="relative isolate flex h-full flex-col overflow-hidden">
        <div className="relative z-10 flex h-full w-full flex-col">
          <div className="w-full px-4 pt-6 lg:px-10">
            <div className="mx-auto flex w-full max-w-[96rem] flex-col gap-4 rounded-2xl border border-[#2f2f2f] bg-[#15151a]/90 px-4 py-4 shadow-[0_20px_40px_-30px_rgba(0,0,0,0.7)] sm:flex-row sm:items-center sm:justify-between">
              <div className="grid w-full grid-cols-1 gap-3 sm:grid-cols-3">
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
                  {isSubmitting ? "Processing..." : "Process items"}
              </button>
              </div>
            </div>
          </div>

          <div className="mx-auto flex h-full w-full max-w-[96rem] flex-1 flex-col px-6 py-4 lg:px-10">
            <div className="relative flex flex-1 flex-col fade-up fade-up-delay-1">
              <section className="flex min-h-0 flex-1 flex-col pb-[230px]">
                <div className="relative flex h-full max-h-[calc(100vh-520px)] flex-1 items-center justify-center overflow-hidden rounded-3xl border border-[#3a3a3a] bg-[#2a2a2a] p-4 md:p-6">
                {previewUrl || localVideoUrl ? (
                  <video
                    key={previewUrl ?? localVideoUrl ?? "preview"}
                      ref={manualVideoRef}
                      onLoadedMetadata={(event) => {
                        const duration = event.currentTarget.duration
                        setVideoDuration(duration)
                        setCurrentTime(0)
                        setClipStart(0)
                        setClipEnd(duration)
                        event.currentTarget.volume = volume
                      }}
                      onTimeUpdate={(event) => {
                        const nextTime = event.currentTarget.currentTime
                        setCurrentTime(nextTime)
                        if (nextTime < clipStart) {
                          event.currentTarget.currentTime = clipStart
                          setCurrentTime(clipStart)
                        } else if (clipEnd != null && nextTime >= clipEnd) {
                          event.currentTarget.pause()
                          event.currentTarget.currentTime = clipStart
                          setCurrentTime(clipStart)
                        }
                      }}
                      onPlay={() => setIsPlaying(true)}
                      onPause={() => setIsPlaying(false)}
                      className="max-h-full max-w-full rounded-2xl bg-black object-contain"
                  >
                    <source src={previewUrl ?? localVideoUrl ?? undefined} />
                  </video>
                ) : (
                    <label className="flex h-full w-full cursor-pointer items-center justify-center rounded-2xl border border-dashed border-white/10 bg-black/40 text-center transition hover:border-white/30">
                      <div className="flex flex-col items-center gap-3 text-white/80">
                        <span className="text-sm uppercase tracking-[0.35em] text-white/70">Upload video</span>
                        <span className="text-2xl font-semibold text-white">Click to add footage</span>
                      </div>
                      <input type="file" accept="video/*" className="sr-only" onChange={handleVideoChange} />
                    </label>
                  )}
                  {cloudglueOutput ? null : null}
                </div>
              </section>
              <section className="fixed bottom-24 left-0 right-0 z-20">
                <div className="mx-auto flex h-[120px] w-full max-w-[96rem] px-6 lg:px-10">
                  <div className="flex h-full w-full flex-col p-0">
                    <div className="p-0">
                      {videoDuration ? (
                        <div className="flex flex-col gap-3">
                          <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-white/50">
                            <span>Timeline</span>
                            <span>00:00 → {Math.ceil(videoDuration)}s</span>
                          </div>
                          <div
                            ref={timelineRef}
                            className="relative h-16 overflow-hidden rounded-xl border border-white/10 bg-gradient-to-r from-[#1a1a24] via-[#2a2a2f] to-[#1a1a24]"
                            onPointerMove={(event) => {
                              if (!videoDuration || !draggingHandle) return
                              const next = getTimeFromPointer(event.clientX)
                              if (next == null) return
                              if (draggingHandle === "start") {
                                const maxStart = Math.max(0, (clipEnd ?? videoDuration) - 2)
                                const bounded = Math.min(next, maxStart)
                                setClipStart(bounded)
                                setCurrentTime(bounded)
                                if (manualVideoRef.current) {
                                  manualVideoRef.current.currentTime = bounded
                                }
                              } else {
                                const minEnd = clipStart + 2
                                const bounded = Math.max(next, minEnd)
                                setClipEnd(bounded)
                                if (manualVideoRef.current && currentTime > bounded) {
                                  manualVideoRef.current.currentTime = bounded
                                  setCurrentTime(bounded)
                                }
                              }
                            }}
                            onPointerUp={() => setDraggingHandle(null)}
                            onPointerLeave={() => setDraggingHandle(null)}
                          >
                            <div className="absolute inset-y-0 left-0 bg-teal-300/20" style={{ width: `${timelineProgress}%` }} />
                            <div
                              className="absolute inset-y-0 w-[2px] bg-teal-300"
                              style={{ left: `${timelineProgress}%` }}
                            />
                            <div
                              className="absolute inset-y-0 bg-white/10"
                              style={{ left: `${startPercent}%`, width: `${Math.max(0, endPercent - startPercent)}%` }}
                            />
                            <div
                              className="absolute inset-y-0 w-[2px] bg-white/70"
                              style={{ left: `${startPercent}%` }}
                            />
                            <div
                              className="absolute inset-y-0 w-[2px] bg-white/70"
                              style={{ left: `${endPercent}%` }}
                            />
                            <button
                              type="button"
                              aria-label="Clip start handle"
                              disabled={!videoDuration}
                              onPointerDown={(event) => {
                                event.stopPropagation()
                                event.currentTarget.setPointerCapture(event.pointerId)
                                setDraggingHandle("start")
                                if (manualVideoRef.current) {
                                  manualVideoRef.current.currentTime = clipStart
                                  setCurrentTime(clipStart)
                                }
                              }}
                              className="absolute top-1/2 z-20 h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/80 bg-white shadow"
                              style={{ left: `${startPercent}%` }}
                            />
                            <button
                              type="button"
                              aria-label="Clip end handle"
                              disabled={!videoDuration}
                              onPointerDown={(event) => {
                                event.stopPropagation()
                                event.currentTarget.setPointerCapture(event.pointerId)
                                setDraggingHandle("end")
                              }}
                              className="absolute top-1/2 z-20 h-5 w-5 -translate-x-1/2 -translate-y-1/2 rounded-full border border-white/80 bg-white shadow"
                              style={{ left: `${endPercent}%` }}
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
                                  if (clipEnd != null && (video.currentTime < clipStart || video.currentTime > clipEnd)) {
                                    video.currentTime = clipStart
                                  }
                                  video.play().catch(() => {})
                                } else {
                                  video.pause()
                                }
                              }}
                              disabled={!videoDuration}
                            >
                              {isPlaying ? "Pause" : "Play"}
                            </button>
                            <div className="rounded-full border border-white/10 bg-black/40 px-3 py-1">
                              {new Date(currentTime * 1000).toISOString().slice(14, 19)} /{" "}
                              {new Date((videoDuration ?? 0) * 1000).toISOString().slice(14, 19)}
                            </div>
                            <div className="rounded-full border border-white/10 bg-black/40 px-3 py-1">
                              In {new Date(clipStart * 1000).toISOString().slice(14, 19)} / Out{" "}
                              {new Date((clipEnd ?? 0) * 1000).toISOString().slice(14, 19)}
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
          {flowStep === "select" && cloudglueOutput ? (
            <div ref={selectionRef} className="mx-auto w-full max-w-[96rem] px-6 pb-20 pt-10 lg:px-10">
              <div className="rounded-3xl border border-white/10 bg-black/40 p-8 backdrop-blur">
                <p className="text-xs uppercase tracking-[0.35em] text-teal-300">Next step</p>
                <h2 className="mt-4 text-2xl font-semibold text-white">Select the targets to replace</h2>
                <p className="mt-3 max-w-2xl text-sm text-white/70">
                  Review the detected items and choose which ones you want to update with the uploaded image.
                </p>
                <div className="mt-8 grid gap-6 lg:grid-cols-[360px_1fr]">
                  <div className="rounded-2xl border border-white/10 bg-black/50 p-4">
                    <p className="text-xs uppercase tracking-[0.3em] text-white/60">Checklist</p>
                    <p className="mt-2 text-sm text-white/70">{cloudglueOutput.target_description}</p>
                    <div className="mt-4 max-h-[420px] overflow-y-auto pr-2">
                      <div className="flex flex-col gap-3">
                      {cloudglueOutput.items.map((item, index) => {
                        const key = `${item.label}-${index}`
                        const checked = selectedItems[key] ?? false
                        return (
                          <label key={key} className="flex flex-col gap-2 rounded-xl border border-white/10 bg-white/5 p-3">
                            <div className="flex items-center gap-3">
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={(event) =>
                                  setSelectedItems((prev) => ({ ...prev, [key]: event.target.checked }))
                                }
                                className="h-4 w-4 accent-teal-300"
                              />
                              <span className="text-sm font-semibold text-white">{item.label}</span>
                            </div>
                            <p className="text-xs text-white/60">{item.description}</p>
                            <div className="flex flex-wrap gap-2 text-[11px] text-white/60">
                              {item.timestamps
                                ?.map((range) =>
                                  clampRangeToDuration(range.start_time, range.end_time, videoDuration)
                                )
                                .filter((range) => range && range.end > range.start)
                                .map((range, rangeIndex) => (
                                  <span
                                    key={`${key}-${rangeIndex}`}
                                    className="rounded-full border border-white/10 bg-black/40 px-2 py-1"
                                  >
                                    {formatTimestamp(range.start)}–{formatTimestamp(range.end)}
                                  </span>
                                ))}
                            </div>
                          </label>
                        )
                      })}
                      </div>
                    </div>
                  </div>
                  <div className="rounded-2xl border border-white/10 bg-black/50 p-4">
                    <p className="text-xs uppercase tracking-[0.3em] text-white/60">Preview</p>
                    <div className="mt-4 flex h-[360px] items-center justify-center overflow-hidden rounded-2xl border border-white/10 bg-black">
                      {previewUrl || localVideoUrl ? (
                        <video
                          key={`selection-${previewUrl ?? localVideoUrl ?? "preview"}`}
                          controls
                          className="h-full w-full object-contain"
                        >
                          <source src={previewUrl ?? localVideoUrl ?? undefined} />
                        </video>
                      ) : (
                        <div className="text-sm text-white/60">Upload a video to preview.</div>
                      )}
                    </div>
                  </div>
                </div>
                <div className="mt-8 flex justify-end">
                  <button
                    type="button"
                    onClick={handleGenerateSelected}
                    disabled={isSubmitting}
                    className="rounded-xl bg-teal-300/20 px-6 py-3 text-sm font-semibold text-teal-200 transition hover:bg-teal-300/30 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? "Generating..." : "Generate"}
                  </button>
                </div>
              </div>
            </div>
          ) : null}
          </div>
        </div>
      </div>
    </main>
  )
}
