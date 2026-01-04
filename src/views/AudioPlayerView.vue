<template>
  <main class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-white mb-4 drop-shadow-lg">音频播放器</h1>
        <p class="text-xl text-white/90 font-medium">播放音频并同步显示字幕</p>
      </div>

      <!-- Upload Section -->
      <div class="mb-8">
        <div
          class="glass rounded-2xl p-8 text-center shadow-xl border-2 border-dashed border-white/30 hover:border-indigo-400 transition-all duration-300 cursor-pointer card-hover"
          @drop.prevent="handleFileDrop" @dragover.prevent>
          <input ref="fileInput" type="file" accept="audio/*,.srt" @change="handleFileSelect" class="hidden" multiple />
          <div v-if="!selectedAudio && !selectedSrt" class="upload-placeholder">
            <div class="text-5xl mb-4">📁</div>
            <p class="mb-4 text-lg font-semibold text-gray-700">拖拽音频文件或SRT字幕文件到此处或点击选择</p>
            <p class="mb-4 text-sm text-gray-600">支持音频文件（mp3, wav, ogg等）和SRT字幕文件</p>
            <button @click="$refs.fileInput.click()"
              class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
              选择文件
            </button>
          </div>
          <div v-else class="flex flex-col items-center gap-4">
            <!-- Audio File Display -->
            <div v-if="selectedAudio"
              class="w-full bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4 border-2 border-indigo-200">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3 flex-1">
                  <div class="text-3xl">🎵</div>
                  <div class="text-left flex-1">
                    <p class="text-lg font-semibold text-gray-800 mb-1">
                      音频文件: <span class="text-indigo-600">{{ selectedAudio.name }}</span>
                    </p>
                    <p class="text-gray-600 text-sm font-medium">大小: {{ formatFileSize(selectedAudio.size) }}</p>
                  </div>
                </div>
                <button @click="clearAudio"
                  class="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl text-sm">
                  清除
                </button>
              </div>
            </div>

            <!-- SRT File Display -->
            <div v-if="selectedSrt"
              class="w-full bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 border-2 border-purple-200">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3 flex-1">
                  <div class="text-3xl">📄</div>
                  <div class="text-left flex-1">
                    <p class="text-lg font-semibold text-gray-800 mb-1">
                      字幕文件: <span class="text-purple-600">{{ selectedSrt.name }}</span>
                    </p>
                    <p class="text-gray-600 text-sm font-medium">大小: {{ formatFileSize(selectedSrt.size) }}</p>
                  </div>
                </div>
                <button @click="clearSrt"
                  class="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl text-sm">
                  清除
                </button>
              </div>
            </div>

            <!-- Add More Files Button -->
            <button @click="$refs.fileInput.click()"
              class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl text-sm">
              添加更多文件
            </button>
          </div>
        </div>
      </div>

      <!-- Player Section -->
      <div class="mb-8" v-if="audioUrl">
        <div class="glass rounded-2xl p-8 shadow-xl border border-white/20">
          <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
            <span>🎧</span>
            <span>播放器</span>
          </h3>

          <!-- Audio Player -->
          <div class="mb-6">
            <audio ref="audioPlayer" :src="audioUrl" controls @timeupdate="updateCaption"
              @loadedmetadata="onAudioLoaded" class="w-full rounded-lg shadow-lg"></audio>
          </div>

          <!-- Current Caption Display -->
          <div class="mb-6">
            <div class="flex justify-between items-center mb-3">
              <h4 class="text-lg font-semibold text-gray-800">当前字幕</h4>
              <button v-if="currentCaption || lastValidCaption" @click="toggleFullscreen"
                class="px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl text-sm flex items-center gap-2">
                <span>{{ isFullscreen ? '退出全屏' : '全屏显示' }}</span>
                <span>{{ isFullscreen ? '⤓' : '⤢' }}</span>
              </button>
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
        </div>
      </div>

      <!-- Error Section -->
      <div class="mb-8" v-if="error">
        <div class="glass rounded-2xl p-6 border-l-4 border-red-500 shadow-xl">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-3">
              <span class="text-3xl">⚠️</span>
              <p class="font-semibold text-red-700 text-lg">{{ error }}</p>
            </div>
            <button @click="error = null"
              class="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 font-semibold shadow-lg">
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Fullscreen Subtitle Overlay -->
    <Transition name="fade">
      <div v-if="isFullscreen"
        class="fixed inset-0 z-50 bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 flex flex-col items-center justify-center p-8"
        tabindex="-1">
        <div class="absolute top-4 right-4 z-10">
          <button @click="exitFullscreen"
            class="px-6 py-3 bg-black/30 hover:bg-black/50 backdrop-blur-md text-white rounded-lg transition-all duration-200 font-semibold shadow-lg hover:shadow-xl flex items-center gap-2 border border-white/20">
            <span>退出全屏</span>
            <span>⤓</span>
          </button>
        </div>
        <div class="text-center max-w-7xl w-full px-8 flex-1 flex items-center justify-center">
          <p v-if="currentCaption || lastValidCaption"
            class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-light text-white leading-relaxed drop-shadow-2xl animate-fade-in">
            {{ currentCaption || lastValidCaption }}
          </p>
          <p v-else class="text-4xl md:text-5xl text-white/40 font-light">
            字幕将在这里显示
          </p>
        </div>
        <!-- Progress Bar -->
        <div class="absolute bottom-0 left-0 right-0 w-full h-1 bg-black/20">
          <div
            class="h-full bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 transition-all duration-300 ease-out"
            :style="{ width: progressPercentage + '%' }">
          </div>
        </div>
      </div>
    </Transition>
  </main>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, onUnmounted } from 'vue'
import { audioAPI } from '../services/api'

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
    selectedAudio.value = file
    audioUrl.value = URL.createObjectURL(file)
    captions.value = []
    currentCaption.value = ''
    currentCaptionIndex.value = -1
    lastValidCaption.value = ''
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
  if (audioUrl.value) {
    URL.revokeObjectURL(audioUrl.value)
  }
  selectedAudio.value = null
  audioUrl.value = null
  captions.value = []
  currentCaption.value = ''
  currentCaptionIndex.value = -1
  lastValidCaption.value = ''
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
  if (isFullscreen.value) {
    // Prevent body scroll when in fullscreen
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
}

const exitFullscreen = () => {
  isFullscreen.value = false
  document.body.style.overflow = ''
}

const handleKeyDown = (event) => {
  if (event.key === 'Escape' && isFullscreen.value) {
    exitFullscreen()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  document.body.style.overflow = ''
})
</script>
