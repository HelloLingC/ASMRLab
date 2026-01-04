<template>
  <div class="max-w-4xl mx-auto p-8">
    <h1 class="text-center text-3xl font-bold text-gray-800 mb-8">AI音频处理</h1>

    <!-- Upload Section -->
    <div class="mb-8">
      <div
        class="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center bg-gray-50 hover:border-primary hover:bg-primary-light transition-all duration-300 cursor-pointer"
        @drop.prevent="handleDrop"
        @dragover.prevent
      >
        <input
          ref="fileInput"
          type="file"
          accept="audio/*"
          @change="handleFileSelect"
          class="hidden"
        />
        <div v-if="!selectedFile" class="upload-placeholder">
          <p class="mb-4 text-gray-600">拖拽音频文件到此处或点击选择</p>
          <button
            @click="$refs.fileInput.click()"
            class="px-6 py-3 bg-primary text-white rounded hover:bg-primary-hover transition-colors duration-300 font-medium"
          >
            选择文件
          </button>
        </div>
        <div v-else class="flex flex-col items-center gap-2">
          <p class="text-gray-700">
            已选择: <span class="font-medium">{{ selectedFile.name }}</span>
          </p>
          <p class="text-gray-600">大小: {{ formatFileSize(selectedFile.size) }}</p>
          <button
            @click="clearFile"
            class="mt-2 px-6 py-3 bg-destructive text-white rounded hover:bg-destructive-hover transition-colors duration-300 font-medium"
          >
            清除
          </button>
        </div>
      </div>
    </div>

    <!-- Operations Section -->
    <div class="mb-8" v-if="selectedFile">
      <h3 class="text-xl font-semibold text-gray-800 mb-4">处理操作</h3>
      <div class="flex gap-4 justify-center flex-wrap">
        <button
          @click="processAudio('analyze')"
          :disabled="processing"
          class="px-6 py-3 bg-primary text-white rounded hover:bg-primary-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300 font-medium"
        >
          分析音频
        </button>
        <button
          @click="processAudio('noise_reduction')"
          :disabled="processing"
          class="px-6 py-3 bg-primary text-white rounded hover:bg-primary-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300 font-medium"
        >
          降噪
        </button>
        <button
          @click="processAudio('format_convert')"
          :disabled="processing"
          class="px-6 py-3 bg-primary text-white rounded hover:bg-primary-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300 font-medium"
        >
          格式转换
        </button>
      </div>
    </div>

    <!-- Transcription Section -->
    <div class="mb-8 p-6 bg-gray-50 rounded-lg" v-if="selectedFile">
      <h3 class="text-xl font-semibold text-gray-800 mb-4">Whisper 语音转录</h3>
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
        @click="transcribeAudio"
        :disabled="processing"
        class="px-8 py-3 bg-transcription text-white rounded w-full max-w-xs hover:bg-transcription-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300 font-medium text-base"
      >
        {{ transcribing ? '转录中...' : '开始转录' }}
      </button>
    </div>

    <!-- Transcription Result -->
    <div
      class="mb-8 p-6 bg-transcription-light rounded-lg border border-transcription-border"
      v-if="transcriptionResult"
    >
      <h3 class="text-xl font-semibold text-gray-800 mb-4">转录结果</h3>
      <div class="flex gap-8 mb-4 pb-4 border-b border-transcription-border flex-wrap">
        <p class="text-gray-600 m-0">
          <strong class="text-gray-700">检测语言:</strong>
          {{ transcriptionResult.language || '未知' }}
        </p>
        <p class="text-gray-600 m-0">
          <strong class="text-gray-700">使用模型:</strong> {{ transcriptionResult.model_name }}
        </p>
      </div>
      <div
        class="bg-white p-6 rounded mb-4 text-lg leading-relaxed whitespace-pre-wrap break-words text-gray-800"
      >
        <p class="m-0">{{ transcriptionResult.text }}</p>
      </div>
      <div
        class="mt-6"
        v-if="transcriptionResult.segments && transcriptionResult.segments.length > 0"
      >
        <h4 class="text-lg font-semibold text-gray-800 mb-4">分段详情</h4>
        <div class="max-h-96 overflow-y-auto bg-white p-4 rounded">
          <div
            v-for="(segment, index) in transcriptionResult.segments"
            :key="index"
            class="mb-4 pb-4 border-b border-gray-200 last:mb-0 last:pb-0 last:border-b-0"
          >
            <div class="text-sm text-gray-600 mb-2 font-medium">
              {{ formatTime(segment.start) }} - {{ formatTime(segment.end) }}
            </div>
            <div class="text-gray-800 leading-relaxed">{{ segment.text }}</div>
          </div>
        </div>
      </div>
      <div class="flex gap-4 mt-6">
        <button
          @click="copyTranscription"
          class="px-6 py-2 bg-success text-white rounded hover:bg-success-hover transition-colors duration-300 text-sm font-medium"
        >
          复制文本
        </button>
        <button
          @click="downloadSRT"
          :disabled="downloadingSRT"
          class="px-6 py-2 bg-primary text-white rounded hover:bg-primary-hover disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-300 text-sm font-medium"
        >
          {{ downloadingSRT ? '下载中...' : '下载SRT字幕' }}
        </button>
      </div>
    </div>

    <!-- Result Section -->
    <div class="mb-8 p-4 bg-gray-100 rounded-lg" v-if="result">
      <h3 class="text-xl font-semibold text-gray-800 mb-4">处理结果</h3>
      <div class="bg-white p-4 rounded overflow-x-auto">
        <pre class="m-0 text-sm text-gray-800">{{ JSON.stringify(result, null, 2) }}</pre>
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

    <!-- Loading State -->
    <div class="text-center p-8 text-gray-600" v-if="processing">
      <p class="text-lg font-medium">处理中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { audioAPI } from '../services/api'

const fileInput = ref(null)
const selectedFile = ref(null)
const processing = ref(false)
const transcribing = ref(false)
const downloadingSRT = ref(false)
const result = ref(null)
const transcriptionResult = ref(null)
const error = ref(null)
const whisperModelName = ref('base')
const whisperLanguage = ref('')
const availableModels = ref({})
const modelStatuses = ref({})

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

// 获取模型显示名称
const getModelDisplayName = (modelName) => {
  const model = availableModels.value[modelName]
  return model ? `${model.name} (${model.speed}, ${model.accuracy})` : modelName
}

onMounted(() => {
  fetchModels()
})

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('audio/')) {
    selectedFile.value = file
  } else {
    error.value = '请选择音频文件'
  }
}

const clearFile = () => {
  selectedFile.value = null
  result.value = null
  transcriptionResult.value = null
  error.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const processAudio = async (operation) => {
  if (!selectedFile.value) {
    error.value = '请先选择音频文件'
    return
  }

  processing.value = true
  error.value = null
  result.value = null

  try {
    const response = await audioAPI.processAudio(selectedFile.value, operation)
    result.value = response
  } catch (err) {
    error.value = err.message
  } finally {
    processing.value = false
  }
}

const transcribeAudio = async () => {
  if (!selectedFile.value) {
    error.value = '请先选择音频文件'
    return
  }

  // 检查模型是否可用
  if (!isModelAvailable(whisperModelName.value)) {
    const status = modelStatuses.value[whisperModelName.value]
    if (status?.status === 'not_downloaded') {
      error.value = `模型 "${getModelDisplayName(whisperModelName.value)}" 未下载。请先在模型管理页面下载该模型。`
    } else if (status?.status === 'downloading') {
      error.value = `模型 "${getModelDisplayName(whisperModelName.value)}" 正在下载中，请稍后再试。`
    } else {
      error.value = `模型 "${getModelDisplayName(whisperModelName.value)}" 不可用: ${status?.message || '未知错误'}`
    }
    return
  }

  transcribing.value = true
  processing.value = true
  error.value = null
  transcriptionResult.value = null

  try {
    const language = whisperLanguage.value || null
    const response = await audioAPI.transcribeAudio(
      selectedFile.value,
      whisperModelName.value,
      language,
    )
    transcriptionResult.value = response
  } catch (err) {
    error.value = err.message || '转录失败'
  } finally {
    transcribing.value = false
    processing.value = false
  }
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

const copyTranscription = async () => {
  if (transcriptionResult.value && transcriptionResult.value.text) {
    try {
      await navigator.clipboard.writeText(transcriptionResult.value.text)
      alert('文本已复制到剪贴板')
    } catch (err) {
      error.value = '复制失败: ' + err.message
    }
  }
}

const downloadSRT = async () => {
  if (!selectedFile.value) {
    error.value = '请先选择音频文件'
    return
  }

  downloadingSRT.value = true
  error.value = null

  try {
    const language = whisperLanguage.value || null
    const response = await audioAPI.downloadSRT(
      selectedFile.value,
      whisperModelName.value,
      language,
    )

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    const filename = selectedFile.value.name.replace(/\.[^/.]+$/, '') + '.srt'
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    alert('SRT字幕文件下载成功')
  } catch (err) {
    error.value = err.message || '下载SRT失败'
  } finally {
    downloadingSRT.value = false
  }
}
</script>
