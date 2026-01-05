<template>
  <main class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold mb-4">音频播放器</h1>
        <p class="text-xl text-muted-foreground font-medium">播放音频并同步显示字幕</p>
      </div>

      <!-- Upload Section -->
      <div class="mb-8">
        <Card
          class="p-8 text-center border-2 border-dashed hover:border-primary transition-all duration-300 cursor-pointer"
          @drop.prevent="handleFileDrop" @dragover.prevent>
          <input ref="fileInput" type="file" accept="audio/*,.srt" @change="handleFileSelect" class="hidden" multiple />
          <CardContent v-if="!selectedAudio && !selectedSrt" class="pt-6">
            <div class="text-5xl mb-4">📁</div>
            <p class="mb-4 text-lg font-semibold">拖拽音频文件或SRT字幕文件到此处或点击选择</p>
            <p class="mb-4 text-sm text-muted-foreground">支持音频文件（mp3, wav, ogg等）和SRT字幕文件</p>
            <Button @click="$refs.fileInput.click()" size="lg">
              选择文件
            </Button>
          </CardContent>
          <CardContent v-else class="pt-6">
            <div class="flex flex-col items-center gap-4">
              <!-- Audio File Display -->
              <Card v-if="selectedAudio" class="w-full p-4 border-primary/20 bg-primary/5">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3 flex-1">
                    <div class="text-3xl">🎵</div>
                    <div class="text-left flex-1">
                      <p class="text-lg font-semibold mb-1">
                        音频文件: <span class="text-primary">{{ selectedAudio.name }}</span>
                      </p>
                      <p class="text-muted-foreground text-sm font-medium">大小: {{ formatFileSize(selectedAudio.size) }}
                      </p>
                    </div>
                  </div>
                  <Button @click="clearAudio" variant="destructive" size="sm">
                    清除
                  </Button>
                </div>
              </Card>

              <!-- SRT File Display -->
              <Card v-if="selectedSrt" class="w-full p-4 border-purple-200 bg-purple-50/50">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3 flex-1">
                    <div class="text-3xl">📄</div>
                    <div class="text-left flex-1">
                      <p class="text-lg font-semibold mb-1">
                        字幕文件: <span class="text-purple-600">{{ selectedSrt.name }}</span>
                      </p>
                      <p class="text-muted-foreground text-sm font-medium">大小: {{ formatFileSize(selectedSrt.size) }}
                      </p>
                    </div>
                  </div>
                  <Button @click="clearSrt" variant="destructive" size="sm">
                    清除
                  </Button>
                </div>
              </Card>

              <!-- Add More Files Button -->
              <Button @click="$refs.fileInput.click()" size="sm">
                添加更多文件
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Player Section -->
      <div class="mb-8" v-if="audioUrl">
        <Card class="p-8">
          <CardHeader>
            <CardTitle class="flex items-center gap-3">
              <span>🎧</span>
              <span>播放器</span>
            </CardTitle>
          </CardHeader>
          <CardContent>

            <!-- Custom Music Player UI -->
            <div class="mb-6">
              <audio ref="audioPlayer" :src="audioUrl" @timeupdate="updateCaption" @loadedmetadata="onAudioLoaded"
                @play="isPlaying = true" @pause="isPlaying = false" @ended="isPlaying = false" class="hidden"></audio>

              <div
                class="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 rounded-xl p-6 border-2 border-indigo-200 shadow-lg">
                <!-- Track Info -->
                <div class="mb-4">
                  <h4 class="text-lg font-bold text-gray-800 mb-1">{{ selectedAudio?.name || '未知音频' }}</h4>
                  <p class="text-sm text-gray-600">{{ formatFileSize(selectedAudio?.size || 0) }}</p>
                </div>

                <!-- Progress Bar -->
                <div class="mb-4">
                  <div class="relative h-2 bg-gray-200 rounded-full overflow-hidden cursor-pointer group"
                    @click="seekToPosition" ref="progressBarContainer">
                    <div
                      class="absolute inset-0 bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 rounded-full transition-all duration-300"
                      :style="{ width: progressPercentage + '%' }"></div>
                    <div
                      class="absolute h-full w-1 bg-white rounded-full shadow-lg transition-all duration-300 opacity-0 group-hover:opacity-100"
                      :style="{ left: progressPercentage + '%', transform: 'translateX(-50%)' }"></div>
                  </div>
                  <div class="flex justify-between items-center mt-2 text-sm text-gray-600 font-medium">
                    <span>{{ formatTimeDisplay(currentTime) }}</span>
                    <span>{{ formatTimeDisplay(duration) }}</span>
                  </div>
                </div>

                <!-- Main Controls -->
                <div class="flex items-center justify-center gap-6 mb-4">
                  <!-- Playback Speed -->
                  <Button @click="togglePlaybackSpeed" variant="outline" size="sm">
                    {{ playbackRate }}x
                  </Button>

                  <!-- Play/Pause Button -->
                  <Button @click="togglePlayPause" size="icon" class="w-16 h-16 rounded-full">
                    <svg v-if="!isPlaying" class="w-8 h-8 ml-1" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                    <svg v-else class="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z" />
                    </svg>
                  </Button>

                  <!-- Volume Control -->
                  <div class="flex items-center gap-2 flex-shrink-0">
                    <Button @click="toggleMute" variant="outline" size="sm">
                      <svg v-if="!isMuted && volume > 0.5" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
                      </svg>
                      <svg v-else-if="!isMuted && volume > 0" class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z" />
                      </svg>
                      <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path
                          d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z" />
                      </svg>
                    </Button>
                    <div class="flex items-center gap-2 w-24 relative">
                      <div class="absolute h-2 w-full bg-gray-200 rounded-lg pointer-events-none">
                        <div
                          class="h-full bg-gradient-to-r from-indigo-400 to-purple-500 rounded-lg transition-all duration-200"
                          :style="{ width: (volume * 100) + '%' }"></div>
                      </div>
                      <input type="range" min="0" max="1" step="0.01" v-model.number="volume" @input="updateVolume"
                        class="relative flex-1 h-2 appearance-none cursor-pointer volume-slider bg-transparent">
                    </div>
                  </div>
                </div>

                <!-- Additional Controls Row -->
                <div class="flex items-center justify-center gap-4">
                  <Button @click="skipBackward" variant="outline" size="sm" class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M11.99 5V1l-5 5 5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6h-2c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z" />
                    </svg>
                    <span>10秒</span>
                  </Button>
                  <Button @click="skipForward" variant="outline" size="sm" class="flex items-center gap-2">
                    <span>10秒</span>
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path
                        d="M12 5V1l5 5-5 5V7c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6h2c0 4.42-3.58 8-8 8s-8-3.58-8-8 3.58-8 8-8z" />
                    </svg>
                  </Button>
                </div>

                <!-- Voice Separation Control -->
                <div class="mt-6 flex justify-center">
                  <Button @click="handleSeparateVoice" variant="outline" size="sm"
                    :disabled="!selectedAudio || isSeparating" class="flex items-center gap-2">
                    <span v-if="!isSeparating">使用 Demucs 分离人声</span>
                    <span v-else>正在分离中，请稍候...</span>
                  </Button>
                </div>
              </div>
            </div>

            <!-- Current Caption Display -->
            <div class="mb-6">
              <div class="flex justify-between items-center mb-3">
                <h4 class="text-lg font-semibold">当前字幕</h4>
                <Button v-if="currentCaption || lastValidCaption" @click="toggleFullscreen" size="sm"
                  class="flex items-center gap-2">
                  <span>{{ isFullscreen ? '退出全屏' : '全屏显示' }}</span>
                  <span>{{ isFullscreen ? '⤓' : '⤢' }}</span>
                </Button>
              </div>
              <div
                class="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-8 rounded-xl text-center min-h-[120px] flex items-center justify-center border-2 border-indigo-200 shadow-inner">
                <p v-if="currentCaption" class="text-2xl font-semibold text-gray-800 leading-relaxed">
                  {{ currentCaption }}
                </p>
                <p v-else class="text-xl text-gray-500 font-medium">字幕将在这里显示</p>
              </div>
            </div>

            <!-- Caption List -->
            <div class="mt-6" v-if="captions.length > 0">
              <h4 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <span>📋</span>
                <span>字幕列表</span>
              </h4>
              <div ref="captionListContainer"
                class="max-h-96 overflow-y-auto bg-gradient-to-br from-gray-50 to-white p-6 rounded-xl border-2 border-gray-200">
                <div v-for="(caption, index) in captions" :key="index" :ref="el => setCaptionRef(el, index)"
                  class="mb-4 pb-4 border-b-2 border-gray-200 last:mb-0 last:pb-0 last:border-b-0 transition-all duration-200 rounded-lg p-3"
                  :class="{ 'bg-gradient-to-r from-yellow-100 to-amber-100 border-yellow-300 shadow-md': isCurrentCaption(index) }">
                  <div class="text-sm text-gray-600 mb-2 font-semibold bg-indigo-50 px-3 py-1 rounded-lg inline-block">
                    {{ formatTime(caption.start) }} - {{ formatTime(caption.end) }}
                  </div>
                  <div class="text-gray-800 leading-relaxed mt-2 text-lg"
                    :class="{ 'font-semibold': isCurrentCaption(index) }">
                    {{ caption.text }}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Error Section -->
      <div class="mb-8" v-if="error">
        <Alert variant="destructive">
          <AlertTitle class="flex items-center gap-2">
            <span>⚠️</span>
            <span>错误</span>
          </AlertTitle>
          <AlertDescription class="flex justify-between items-center">
            <span>{{ error }}</span>
            <Button variant="ghost" size="sm" @click="error = null">关闭</Button>
          </AlertDescription>
        </Alert>
      </div>
    </div>

    <!-- Fullscreen Subtitle Overlay -->
    <FullscreenSubtitle v-model="isFullscreen" :current-caption="currentCaption" :last-valid-caption="lastValidCaption"
      :progress-percentage="progressPercentage" @close="exitFullscreen" />
  </main>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { audioAPI } from '../services/api'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert'
import FullscreenSubtitle from '@/components/FullscreenSubtitle.vue'

const fileInput = ref(null)
const audioPlayer = ref(null)
const selectedAudio = ref(null)
const selectedSrt = ref(null)
const error = ref(null)
const audioUrl = ref(null)
const captions = ref([])
const currentCaption = ref('')
const currentTime = ref(0)
const duration = ref(0)
const captionListContainer = ref(null)
const captionRefs = ref([])
const currentCaptionIndex = ref(-1)
const lastValidCaption = ref('') // 存储上一个有效的字幕内容
const isFullscreen = ref(false)
const isPlaying = ref(false)
const volume = ref(1)
const isMuted = ref(false)
const playbackRate = ref(1)
const progressBarContainer = ref(null)
const isSeparating = ref(false)

// Smart file type detection
const detectFileType = (file) => {
  // Check by extension first (more reliable for SRT)
  if (file.name.toLowerCase().endsWith('.srt')) {
    return 'srt'
  }
  // Check by MIME type for audio files
  if (file.type.startsWith('audio/')) {
    return 'audio'
  }
  // Fallback: check common audio extensions
  const audioExtensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.wma', '.opus']
  const lowerName = file.name.toLowerCase()
  if (audioExtensions.some(ext => lowerName.endsWith(ext))) {
    return 'audio'
  }
  return null
}

const handleFile = (file) => {
  const fileType = detectFileType(file)

  if (fileType === 'audio') {
    // Stop and reset previous audio if any
    if (audioPlayer.value) {
      audioPlayer.value.pause()
      audioPlayer.value.currentTime = 0
    }
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value)
    }
    selectedAudio.value = file
    audioUrl.value = URL.createObjectURL(file)
    captions.value = []
    currentCaption.value = ''
    currentCaptionIndex.value = -1
    lastValidCaption.value = ''
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
    error.value = null
  } else if (fileType === 'srt') {
    selectedSrt.value = file
    parseSrtFile(file)
    error.value = null
  } else {
    error.value = '不支持的文件类型，请选择音频文件或SRT字幕文件'
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  files.forEach(file => {
    handleFile(file)
  })
  // Reset input to allow selecting the same file again
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleFileDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  files.forEach(file => {
    handleFile(file)
  })
}

const clearAudio = () => {
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value.currentTime = 0
  }
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  selectedAudio.value = null
  audioUrl.value = null
  captions.value = []
  currentCaption.value = ''
  currentCaptionIndex.value = -1
  lastValidCaption.value = ''
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
}

const clearSrt = () => {
  selectedSrt.value = null
  captions.value = []
  currentCaption.value = ''
  currentCaptionIndex.value = -1
  lastValidCaption.value = ''
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const parseSrtFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const srtContent = e.target.result
    captions.value = parseSrt(srtContent)
    // Reset caption refs and index when new captions are loaded
    captionRefs.value = []
    currentCaptionIndex.value = -1
    lastValidCaption.value = ''
    currentCaption.value = ''
  }
  reader.readAsText(file)
}

const parseSrt = (srtContent) => {
  const lines = srtContent.split('\n')
  const captions = []
  let currentCaption = null

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()

    if (!line) continue

    if (line.includes('-->')) {
      // Time line - start new caption
      if (currentCaption) {
        captions.push(currentCaption)
      }
      const [start, end] = line.split(' --> ')
      currentCaption = {
        start: timeToSeconds(start),
        end: timeToSeconds(end),
        text: '',
      }
      // Set to 0 if invalid
      if (isNaN(currentCaption.start)) currentCaption.start = 0
      if (isNaN(currentCaption.end)) currentCaption.end = 0
    } else if (currentCaption && !isNaN(line)) {
      // Skip sequence number
      continue
    } else if (currentCaption) {
      // Text line
      currentCaption.text += (currentCaption.text ? ' ' : '') + line
    }
  }

  if (currentCaption) {
    captions.push(currentCaption)
  }

  return captions
}

const timeToSeconds = (timeStr) => {
  // Handle both comma and dot separators for milliseconds
  const separator = timeStr.includes(',') ? ',' : '.'
  const [time, ms] = timeStr.split(separator)
  const [hours, minutes, seconds] = time.split(':').map(Number)
  return hours * 3600 + minutes * 60 + seconds + (ms ? parseInt(ms) / 1000 : 0)
}

const onAudioLoaded = () => {
  // Audio loaded
  if (audioPlayer.value) {
    duration.value = audioPlayer.value.duration || 0
    // Set initial volume and playback rate
    audioPlayer.value.volume = volume.value
    audioPlayer.value.playbackRate = playbackRate.value
  }
}

const setCaptionRef = (el, index) => {
  if (el) {
    captionRefs.value[index] = el
  }
}

const scrollToCurrentCaption = async () => {
  await nextTick()
  const newIndex = captions.value.findIndex(
    (caption) => currentTime.value >= caption.start && currentTime.value <= caption.end,
  )

  // Only scroll if the caption index has changed
  if (newIndex !== currentCaptionIndex.value && newIndex !== -1) {
    currentCaptionIndex.value = newIndex

    if (captionRefs.value[newIndex] && captionListContainer.value) {
      const captionElement = captionRefs.value[newIndex]
      const container = captionListContainer.value

      // Calculate the position relative to the container
      const containerRect = container.getBoundingClientRect()
      const elementRect = captionElement.getBoundingClientRect()

      // Calculate the scroll position needed to center the element
      const elementTop = elementRect.top - containerRect.top + container.scrollTop
      const elementHeight = elementRect.height
      const containerHeight = container.clientHeight

      // Calculate target scroll position to center the element
      const targetScrollTop = elementTop - (containerHeight / 2) + (elementHeight / 2)

      // Smooth scroll within the container only
      container.scrollTo({
        top: targetScrollTop,
        behavior: 'smooth'
      })
    }
  } else if (newIndex === -1) {
    // Reset index when no caption is active
    currentCaptionIndex.value = -1
  }
}

const updateCaption = async () => {
  if (!audioPlayer.value) return
  currentTime.value = audioPlayer.value.currentTime
  if (audioPlayer.value.duration && !duration.value) {
    duration.value = audioPlayer.value.duration
  }

  const current = captions.value.find(
    (caption) => currentTime.value >= caption.start && currentTime.value <= caption.end,
  )

  // 如果找到匹配的字幕，更新当前字幕和上一个有效字幕
  if (current) {
    currentCaption.value = current.text
    lastValidCaption.value = current.text
  } else {
    // 如果找不到匹配的字幕（空白期间），保持上一个有效字幕
    // 只有在已经有上一个有效字幕的情况下才保持，否则清空
    if (lastValidCaption.value) {
      currentCaption.value = lastValidCaption.value
    } else {
      currentCaption.value = ''
    }
  }

  // Auto-scroll to current caption (only when caption changes)
  scrollToCurrentCaption()
}

const isCurrentCaption = (index) => {
  const caption = captions.value[index]
  return currentTime.value >= caption.start && currentTime.value <= caption.end
}

const formatTime = (seconds) => {
  if (isNaN(seconds) || seconds < 0) {
    return '00:00.000'
  }
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 1000)

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`
}

const progressPercentage = computed(() => {
  if (!duration.value || duration.value === 0) return 0
  return Math.min(100, (currentTime.value / duration.value) * 100)
})

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const exitFullscreen = () => {
  isFullscreen.value = false
}

const togglePlayPause = () => {
  if (!audioPlayer.value) return
  if (isPlaying.value) {
    audioPlayer.value.pause()
  } else {
    audioPlayer.value.play()
  }
}

const updateVolume = () => {
  if (!audioPlayer.value) return
  audioPlayer.value.volume = volume.value
  if (volume.value > 0 && isMuted.value) {
    isMuted.value = false
  }
}

const toggleMute = () => {
  if (!audioPlayer.value) return
  isMuted.value = !isMuted.value
  audioPlayer.value.muted = isMuted.value
}

const togglePlaybackSpeed = () => {
  const speeds = [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2]
  const currentIndex = speeds.indexOf(playbackRate.value)
  const nextIndex = (currentIndex + 1) % speeds.length
  playbackRate.value = speeds[nextIndex]
  if (audioPlayer.value) {
    audioPlayer.value.playbackRate = playbackRate.value
  }
}

const seekToPosition = (event) => {
  if (!audioPlayer.value || !progressBarContainer.value) return
  const rect = progressBarContainer.value.getBoundingClientRect()
  const clickX = event.clientX - rect.left
  const percentage = Math.max(0, Math.min(1, clickX / rect.width))
  const newTime = percentage * duration.value
  audioPlayer.value.currentTime = newTime
  currentTime.value = newTime
}

const skipBackward = () => {
  if (!audioPlayer.value) return
  audioPlayer.value.currentTime = Math.max(0, audioPlayer.value.currentTime - 10)
}

const skipForward = () => {
  if (!audioPlayer.value) return
  audioPlayer.value.currentTime = Math.min(duration.value, audioPlayer.value.currentTime + 10)
}

const handleSeparateVoice = async () => {
  if (!selectedAudio.value) {
    error.value = '请先选择音频文件'
    return
  }

  if (isSeparating.value) return

  isSeparating.value = true
  error.value = null

  try {
    const response = await audioAPI.separateVoice(selectedAudio.value)
    const blob = response?.data || response

    if (!blob) {
      throw new Error('后端未返回有效的音频数据')
    }

    // 尝试从响应头中解析文件名
    let filename = 'separated_audio'
    const disposition =
      response?.headers?.['content-disposition'] || response?.headers?.get?.('content-disposition')

    if (disposition) {
      const match = /filename="?([^"]+)"?/i.exec(disposition)
      if (match && match[1]) {
        filename = decodeURIComponent(match[1])
      }
    } else if (selectedAudio.value?.name) {
      filename = `${selectedAudio.value.name.replace(/\.[^/.]+$/, '')}_separated`
    }

    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error(e)
    error.value = e?.message || '语音分离失败，请稍后重试'
  } finally {
    isSeparating.value = false
  }
}

const formatTimeDisplay = (seconds) => {
  if (isNaN(seconds) || seconds < 0) {
    return '00:00'
  }
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

onUnmounted(() => {
  document.body.style.overflow = ''
  // Clean up audio URL
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
})
</script>
