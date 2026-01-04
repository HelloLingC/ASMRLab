<template>
  <div class="max-w-4xl mx-auto p-8">
    <h1 class="text-center text-3xl font-bold text-gray-800 mb-8">音频播放器</h1>

    <!-- Upload Section -->
    <div class="mb-8">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Audio Upload -->
        <div
          class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50 hover:border-primary hover:bg-primary-light transition-all duration-300 cursor-pointer"
          @drop.prevent="handleAudioDrop"
          @dragover.prevent
        >
          <input
            ref="audioInput"
            type="file"
            accept="audio/*"
            @change="handleAudioSelect"
            class="hidden"
          />
          <div v-if="!selectedAudio" class="upload-placeholder">
            <p class="mb-4 text-gray-600">拖拽音频文件到此处或点击选择</p>
            <button
              @click="$refs.audioInput.click()"
              class="px-6 py-3 bg-primary text-white rounded hover:bg-primary-hover transition-colors duration-300 font-medium"
            >
              选择音频文件
            </button>
          </div>
          <div v-else class="flex flex-col items-center gap-2">
            <p class="text-gray-700">
              已选择音频: <span class="font-medium">{{ selectedAudio.name }}</span>
            </p>
            <p class="text-gray-600">大小: {{ formatFileSize(selectedAudio.size) }}</p>
            <button
              @click="clearAudio"
              class="mt-2 px-6 py-3 bg-destructive text-white rounded hover:bg-destructive-hover transition-colors duration-300 font-medium"
            >
              清除
            </button>
          </div>
        </div>

        <!-- SRT Upload -->
        <div
          class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50 hover:border-primary hover:bg-primary-light transition-all duration-300 cursor-pointer"
          @drop.prevent="handleSrtDrop"
          @dragover.prevent
        >
          <input
            ref="srtInput"
            type="file"
            accept=".srt"
            @change="handleSrtSelect"
            class="hidden"
          />
          <div v-if="!selectedSrt" class="upload-placeholder">
            <p class="mb-4 text-gray-600">拖拽SRT字幕文件到此处或点击选择</p>
            <p class="text-sm text-gray-500 mb-4">可选，如果不上传将自动生成</p>
            <button
              @click="$refs.srtInput.click()"
              class="px-6 py-3 bg-primary text-white rounded hover:bg-primary-hover transition-colors duration-300 font-medium"
            >
              选择SRT文件
            </button>
          </div>
          <div v-else class="flex flex-col items-center gap-2">
            <p class="text-gray-700">
              已选择字幕: <span class="font-medium">{{ selectedSrt.name }}</span>
            </p>
            <p class="text-gray-600">大小: {{ formatFileSize(selectedSrt.size) }}</p>
            <button
              @click="clearSrt"
              class="mt-2 px-6 py-3 bg-destructive text-white rounded hover:bg-destructive-hover transition-colors duration-300 font-medium"
            >
              清除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Transcription Section (if no SRT uploaded) -->
    <div class="mb-8 p-6 bg-gray-50 rounded-lg" v-if="selectedAudio && !selectedSrt">
      <h3 class="text-xl font-semibold text-gray-800 mb-4">生成字幕</h3>
      <div class="flex gap-6 mb-4 flex-wrap">
        <div class="flex flex-col gap-2 flex-1 min-w-[200px]">
          <label for="model-name" class="font-medium text-gray-700">模型名称:</label>
          <input
            id="model-name"
            v-model="whisperModelName"
            :disabled="processing"
            list="model-suggestions"
            placeholder="输入模型名称，如: base, openai/whisper-large-v3"
            class="p-2 border border-gray-300 rounded bg-white disabled:bg-gray-100 disabled:cursor-not-allowed text-base focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
          <datalist id="model-suggestions">
            <option
              v-for="(model, modelName) in downloadedModels"
              :key="modelName"
              :value="modelName"
            >
              {{ model.name }} ({{ model.speed }}, {{ model.accuracy }})
            </option>
          </datalist>
        </div>
        <div class="flex flex-col gap-2 flex-1 min-w-[200px]">
          <label for="language" class="font-medium text-gray-700">语言 (可选):</label>
          <select
            id="language"
            v-model="whisperLanguage"
            :disabled="processing"
            class="p-2 border border-gray-300 rounded bg-white disabled:bg-gray-100 disabled:cursor-not-allowed text-base focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="">自动检测</option>
            <option value="zh">中文</option>
            <option value="en">English</option>
            <option value="ja">日本語</option>
            <option value="ko">한국어</option>
          </select>
        </div>
      </div>
      <button
        @click="generateCaptions"
        :disabled="processing"
        class="px-8 py-3 bg-transcription text-white rounded w-full max-w-xs hover:bg-transcription-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300 font-medium text-base"
      >
        {{ processing ? '生成中...' : '生成字幕' }}
      </button>
    </div>

    <!-- Player Section -->
    <div class="mb-8" v-if="audioUrl">
      <h3 class="text-xl font-semibold text-gray-800 mb-4">播放器</h3>
      <div class="bg-white p-6 rounded-lg shadow">
        <audio
          ref="audioPlayer"
          :src="audioUrl"
          controls
          @timeupdate="updateCaption"
          @loadedmetadata="onAudioLoaded"
          class="w-full mb-4"
        ></audio>

        <!-- Current Caption -->
        <div
          class="bg-gray-100 p-4 rounded text-center text-lg text-gray-800 min-h-[60px] flex items-center justify-center"
        >
          <p v-if="currentCaption">{{ currentCaption }}</p>
          <p v-else class="text-gray-500">字幕将在这里显示</p>
        </div>

        <!-- Caption List -->
        <div class="mt-6" v-if="captions.length > 0">
          <h4 class="text-lg font-semibold text-gray-800 mb-4">字幕列表</h4>
          <div class="max-h-96 overflow-y-auto bg-gray-50 p-4 rounded">
            <div
              v-for="(caption, index) in captions"
              :key="index"
              class="mb-4 pb-4 border-b border-gray-200 last:mb-0 last:pb-0 last:border-b-0"
              :class="{ 'bg-yellow-100': isCurrentCaption(index) }"
            >
              <div class="text-sm text-gray-600 mb-2 font-medium">
                {{ formatTime(caption.start) }} - {{ formatTime(caption.end) }}
              </div>
              <div class="text-gray-800 leading-relaxed">{{ caption.text }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Section -->
    <div class="mb-8" v-if="error">
      <div
        class="p-4 bg-red-50 border border-red-200 rounded text-red-700 flex justify-between items-center"
      >
        <p class="m-0 font-medium">错误: {{ error }}</p>
        <button
          @click="error = null"
          class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors duration-300 text-sm font-medium"
        >
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { audioAPI } from '../services/api'

const audioInput = ref(null)
const srtInput = ref(null)
const audioPlayer = ref(null)
const selectedAudio = ref(null)
const selectedSrt = ref(null)
const processing = ref(false)
const error = ref(null)
const whisperModelName = ref('base')
const whisperLanguage = ref('')
const availableModels = ref({})
const modelStatuses = ref({})
const audioUrl = ref(null)
const captions = ref([])
const currentCaption = ref('')
const currentTime = ref(0)

// 计算已下载的模型
const downloadedModels = computed(() => {
  return Object.keys(availableModels.value).reduce((acc, modelName) => {
    const status = modelStatuses.value[modelName]?.status
    if (status === 'loaded' || status === 'downloaded') {
      acc[modelName] = availableModels.value[modelName]
    }
    return acc
  }, {})
})

// 获取可用模型信息
const fetchModels = async () => {
  try {
    const response = await audioAPI.getModels()
    availableModels.value = response.models

    // 获取所有模型状态
    const statuses = {}
    for (const modelName of Object.keys(availableModels.value)) {
      try {
        const statusResponse = await audioAPI.getModelStatus(modelName)
        statuses[modelName] = statusResponse
      } catch (err) {
        statuses[modelName] = { status: 'error', message: err.message }
      }
    }
    modelStatuses.value = statuses
  } catch (err) {
    console.error('获取模型信息失败:', err)
  }
}

// 检查模型是否可用
const isModelAvailable = (modelName) => {
  const status = modelStatuses.value[modelName]
  return status && (status.status === 'loaded' || status.status === 'downloaded')
}

onMounted(() => {
  fetchModels()
})

const handleAudioSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedAudio.value = file
    audioUrl.value = URL.createObjectURL(file)
    captions.value = []
    currentCaption.value = ''
  }
}

const handleAudioDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('audio/')) {
    selectedAudio.value = file
    audioUrl.value = URL.createObjectURL(file)
    captions.value = []
    currentCaption.value = ''
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
  if (audioInput.value) {
    audioInput.value.value = ''
  }
}

const clearSrt = () => {
  selectedSrt.value = null
  captions.value = []
  currentCaption.value = ''
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

const generateCaptions = async () => {
  if (!selectedAudio.value) {
    error.value = '请先选择音频文件'
    return
  }

  // 检查模型是否可用
  if (!isModelAvailable(whisperModelName.value)) {
    const status = modelStatuses.value[whisperModelName.value]
    if (status?.status === 'not_downloaded') {
      error.value = `模型 "${whisperModelName.value}" 未下载。请先在模型管理页面下载该模型。`
    } else if (status?.status === 'downloading') {
      error.value = `模型 "${whisperModelName.value}" 正在下载中，请稍后再试。`
    } else {
      error.value = `模型 "${whisperModelName.value}" 不可用: ${status?.message || '未知错误'}`
    }
    return
  }

  processing.value = true
  error.value = null

  try {
    const language = whisperLanguage.value || null
    const response = await audioAPI.transcribeAudio(
      selectedAudio.value,
      whisperModelName.value,
      language,
    )
    captions.value = response.segments.map((segment) => ({
      start: segment.start,
      end: segment.end,
      text: segment.text.trim(),
    }))
  } catch (err) {
    error.value = err.message || '生成字幕失败'
  } finally {
    processing.value = false
  }
}

const parseSrtFile = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const srtContent = e.target.result
    captions.value = parseSrt(srtContent)
  }
  reader.readAsText(file)
}

const parseSrt = (srtContent) => {
  const lines = srtContent.split('\n')
  const captions = []
  let currentCaption = null

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()

    if (!line) {
      if (currentCaption) {
        captions.push(currentCaption)
        currentCaption = null
      }
      continue
    }

    if (!currentCaption) {
      // Skip sequence number
      if (!isNaN(line)) continue
      currentCaption = { text: '' }
    } else if (line.includes('-->')) {
      // Time line
      const [start, end] = line.split(' --> ')
      currentCaption.start = timeToSeconds(start)
      currentCaption.end = timeToSeconds(end)
    } else {
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
  const [time, ms] = timeStr.split(',')
  const [hours, minutes, seconds] = time.split(':').map(Number)
  return hours * 3600 + minutes * 60 + seconds + (ms ? parseInt(ms) / 1000 : 0)
}

const onAudioLoaded = () => {
  // Audio loaded
}

const updateCaption = () => {
  if (!audioPlayer.value) return
  currentTime.value = audioPlayer.value.currentTime

  const current = captions.value.find(
    (caption) => currentTime.value >= caption.start && currentTime.value <= caption.end,
  )

  currentCaption.value = current ? current.text : ''
}

const isCurrentCaption = (index) => {
  const caption = captions.value[index]
  return currentTime.value >= caption.start && currentTime.value <= caption.end
}

const formatTime = (seconds) => {
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
