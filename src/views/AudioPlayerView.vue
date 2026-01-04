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
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Audio Upload -->
          <div
            class="glass rounded-2xl p-8 text-center shadow-xl border-2 border-dashed border-white/30 hover:border-indigo-400 transition-all duration-300 cursor-pointer card-hover"
            @drop.prevent="handleAudioDrop" @dragover.prevent>
            <input ref="audioInput" type="file" accept="audio/*" @change="handleAudioSelect" class="hidden" />
            <div v-if="!selectedAudio" class="upload-placeholder">
              <div class="text-5xl mb-4">🎵</div>
              <p class="mb-4 text-lg font-semibold text-gray-700">拖拽音频文件到此处或点击选择</p>
              <button @click="$refs.audioInput.click()"
                class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
                选择音频文件
              </button>
            </div>
            <div v-else class="flex flex-col items-center gap-3">
              <div class="text-4xl">✅</div>
              <div class="text-center">
                <p class="text-lg font-semibold text-gray-800 mb-1">
                  已选择音频: <span class="text-indigo-600">{{ selectedAudio.name }}</span>
                </p>
                <p class="text-gray-600 text-sm font-medium">大小: {{ formatFileSize(selectedAudio.size) }}</p>
              </div>
              <button @click="clearAudio"
                class="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl text-sm">
                清除
              </button>
            </div>
          </div>

          <!-- SRT Upload -->
          <div
            class="glass rounded-2xl p-8 text-center shadow-xl border-2 border-dashed border-white/30 hover:border-indigo-400 transition-all duration-300 cursor-pointer card-hover"
            @drop.prevent="handleSrtDrop" @dragover.prevent>
            <input ref="srtInput" type="file" accept=".srt" @change="handleSrtSelect" class="hidden" />
            <div v-if="!selectedSrt" class="upload-placeholder">
              <div class="text-5xl mb-4">📄</div>
              <p class="mb-4 text-lg font-semibold text-gray-700">拖拽SRT字幕文件到此处或点击选择</p>
              <button @click="$refs.srtInput.click()"
                class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
                选择SRT文件
              </button>
            </div>
            <div v-else class="flex flex-col items-center gap-3">
              <div class="text-4xl">✅</div>
              <div class="text-center">
                <p class="text-lg font-semibold text-gray-800 mb-1">
                  已选择字幕: <span class="text-indigo-600">{{ selectedSrt.name }}</span>
                </p>
                <p class="text-gray-600 text-sm font-medium">大小: {{ formatFileSize(selectedSrt.size) }}</p>
              </div>
              <button @click="clearSrt"
                class="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl text-sm">
                清除
              </button>
            </div>
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
  </main>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import { audioAPI } from '../services/api'

const audioInput = ref(null)
const srtInput = ref(null)
const audioPlayer = ref(null)
const selectedAudio = ref(null)
const selectedSrt = ref(null)
const error = ref(null)
const audioUrl = ref(null)
const captions = ref([])
const currentCaption = ref('')
const currentTime = ref(0)
const captionListContainer = ref(null)
const captionRefs = ref([])
const currentCaptionIndex = ref(-1)
const lastValidCaption = ref('') // 存储上一个有效的字幕内容

const handleAudioSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedAudio.value = file
    audioUrl.value = URL.createObjectURL(file)
    captions.value = []
    currentCaption.value = ''
    currentCaptionIndex.value = -1
    lastValidCaption.value = ''
  }
}

const handleAudioDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('audio/')) {
    selectedAudio.value = file
    audioUrl.value = URL.createObjectURL(file)
    captions.value = []
    currentCaption.value = ''
    currentCaptionIndex.value = -1
    lastValidCaption.value = ''
  } else {
    error.value = '请选择音频文件'
  }
}

const handleSrtSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedSrt.value = file
    parseSrtFile(file)
  }
}

const handleSrtDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.name.endsWith('.srt')) {
    selectedSrt.value = file
    parseSrtFile(file)
  } else {
    error.value = '请选择SRT文件'
  }
}

const clearAudio = () => {
  selectedAudio.value = null
  audioUrl.value = null
  captions.value = []
  currentCaption.value = ''
  currentCaptionIndex.value = -1
  lastValidCaption.value = ''
  if (audioInput.value) {
    audioInput.value.value = ''
  }
}

const clearSrt = () => {
  selectedSrt.value = null
  captions.value = []
  currentCaption.value = ''
  currentCaptionIndex.value = -1
  lastValidCaption.value = ''
  if (srtInput.value) {
    srtInput.value.value = ''
  }
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
</script>
