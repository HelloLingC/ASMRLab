<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-5xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-white mb-4 drop-shadow-lg">AI 音频处理</h1>
        <p class="text-xl text-white/90 font-medium">上传音频文件进行转录和处理</p>
      </div>

      <!-- Upload Section -->
      <div class="mb-8">
        <div
          class="glass rounded-2xl p-12 text-center shadow-xl border-2 border-dashed border-white/30 hover:border-indigo-400 transition-all duration-300 cursor-pointer card-hover"
          @drop.prevent="handleDrop" @dragover.prevent>
          <input ref="fileInput" type="file" accept="audio/*" @change="handleFileSelect" class="hidden" />
          <div v-if="!selectedFile" class="upload-placeholder">
            <div class="text-6xl mb-6">🎵</div>
            <p class="mb-6 text-xl font-semibold text-gray-700">拖拽音频文件到此处或点击选择</p>
            <button @click="$refs.fileInput.click()"
              class="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
              选择文件
            </button>
          </div>
          <div v-else class="flex flex-col items-center gap-4">
            <div class="text-5xl">✅</div>
            <div class="text-center">
              <p class="text-xl font-semibold text-gray-800 mb-2">
                已选择: <span class="text-indigo-600">{{ selectedFile.name }}</span>
              </p>
              <p class="text-gray-600 font-medium">大小: {{ formatFileSize(selectedFile.size) }}</p>
            </div>
            <button @click="clearFile"
              class="px-6 py-3 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl">
              清除文件
            </button>
          </div>
        </div>
      </div>

      <!-- Operations Section -->
      <div class="mb-8" v-if="selectedFile">
        <div class="glass rounded-2xl p-6 shadow-xl border border-white/20">
          <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
            <span>⚙️</span>
            <span>处理操作</span>
          </h3>
          <div class="flex gap-4 justify-center flex-wrap">
            <button @click="processAudio('analyze')" :disabled="processing"
              class="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-lg hover:from-blue-600 hover:to-cyan-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none">
              🔍 分析音频
            </button>
            <button @click="processAudio('noise_reduction')" :disabled="processing"
              class="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-lg hover:from-purple-600 hover:to-pink-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none">
              🎚️ 降噪
            </button>
            <button @click="processAudio('format_convert')" :disabled="processing"
              class="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none">
              🔄 格式转换
            </button>
            <button @click="separateVoice" :disabled="processing || separating"
              class="px-8 py-4 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-lg hover:from-orange-600 hover:to-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none">
              {{ separating ? '⏳ 分离中...' : '🎤 分离人声 (Demucs)' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Transcription Section -->
      <div class="mb-8" v-if="selectedFile">
        <div class="glass rounded-2xl p-8 shadow-xl border border-white/20">
          <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
            <span>🎤</span>
            <span>Whisper 语音转录</span>
          </h3>
          <div class="grid md:grid-cols-2 gap-6 mb-6">
            <div class="flex flex-col gap-2">
              <label for="model-name" class="font-semibold text-gray-700 flex items-center gap-2">
                <span>🤖</span>
                <span>模型名称:</span>
              </label>
              <input id="model-name" v-model="whisperModelName" :disabled="processing" list="model-suggestions"
                placeholder="输入模型名称，如: base, openai/whisper-large-v3"
                class="p-4 border-2 border-gray-300 rounded-lg bg-white disabled:bg-gray-100 disabled:cursor-not-allowed text-base focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200" />
              <datalist id="model-suggestions">
                <option v-for="(model, modelName) in downloadedModels" :key="modelName" :value="modelName">
                  {{ model.name }} ({{ model.speed }}, {{ model.accuracy }})
                </option>
              </datalist>
            </div>
            <div class="flex flex-col gap-2">
              <label for="language" class="font-semibold text-gray-700 flex items-center gap-2">
                <span>🌐</span>
                <span>语言 (可选):</span>
              </label>
              <select id="language" v-model="whisperLanguage" :disabled="processing"
                class="p-4 border-2 border-gray-300 rounded-lg bg-white disabled:bg-gray-100 disabled:cursor-not-allowed text-base focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                <option value="">自动检测</option>
                <option value="zh">中文</option>
                <option value="en">English</option>
                <option value="ja">日本語</option>
                <option value="ko">한국어</option>
              </select>
            </div>
          </div>
          <button @click="transcribeAudio" :disabled="processing"
            class="w-full px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none">
            {{ transcribing ? '⏳ 转录中...' : '🚀 开始转录' }}
          </button>
        </div>
      </div>

      <!-- Transcription Result -->
      <div class="mb-8 glass rounded-2xl p-8 shadow-xl border border-white/20" v-if="transcriptionResult">
        <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
          <span>📝</span>
          <span>转录结果</span>
        </h3>
        <div class="flex gap-6 mb-6 pb-6 border-b-2 border-gray-200 flex-wrap">
          <div class="px-4 py-2 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border border-blue-200">
            <p class="text-sm font-medium text-gray-600">检测语言:</p>
            <p class="text-lg font-bold text-blue-700">{{ transcriptionResult.language || '未知' }}</p>
          </div>
          <div class="px-4 py-2 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
            <p class="text-sm font-medium text-gray-600">使用模型:</p>
            <p class="text-lg font-bold text-purple-700">{{ transcriptionResult.model_name }}</p>
          </div>
        </div>
        <div
          class="bg-gradient-to-br from-gray-50 to-white p-6 rounded-xl mb-6 text-lg leading-relaxed whitespace-pre-wrap break-words text-gray-800 border-2 border-gray-200 shadow-inner">
          <p class="m-0">{{ transcriptionResult.text }}</p>
        </div>
        <div class="mt-6" v-if="transcriptionResult.segments && transcriptionResult.segments.length > 0">
          <h4 class="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span>📋</span>
            <span>分段详情</span>
          </h4>
          <div
            class="max-h-96 overflow-y-auto bg-gradient-to-br from-gray-50 to-white p-6 rounded-xl border-2 border-gray-200">
            <div v-for="(segment, index) in transcriptionResult.segments" :key="index"
              class="mb-4 pb-4 border-b-2 border-gray-200 last:mb-0 last:pb-0 last:border-b-0">
              <div class="text-sm text-gray-600 mb-2 font-semibold bg-indigo-50 px-3 py-1 rounded-lg inline-block">
                {{ formatTime(segment.start) }} - {{ formatTime(segment.end) }}
              </div>
              <div class="text-gray-800 leading-relaxed mt-2">{{ segment.text }}</div>
            </div>
          </div>
        </div>
        <div class="flex gap-4 mt-6">
          <button @click="copyTranscription"
            class="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
            📋 复制文本
          </button>
          <button @click="downloadSRT" :disabled="downloadingSRT"
            class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none">
            {{ downloadingSRT ? '⏳ 下载中...' : '💾 下载SRT字幕' }}
          </button>
        </div>
      </div>


      <!-- Result Section -->
      <div class="mb-8 glass rounded-2xl p-6 shadow-xl border border-white/20" v-if="result">
        <h3 class="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-3">
          <span>📊</span>
          <span>处理结果</span>
        </h3>
        <div class="bg-gradient-to-br from-gray-50 to-white p-6 rounded-xl overflow-x-auto border-2 border-gray-200">
          <pre class="m-0 text-sm text-gray-800 font-mono">{{ JSON.stringify(result, null, 2) }}</pre>
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

      <!-- Loading State -->
      <div class="glass rounded-2xl p-12 text-center shadow-xl" v-if="processing && !transcribing && !separating">
        <div
          class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent mb-6">
        </div>
        <p class="text-xl font-semibold text-gray-700">处理中...</p>
      </div>

      <!-- Voice Separation Loading State -->
      <div class="glass rounded-2xl p-12 text-center shadow-xl" v-if="separating">
        <div
          class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-orange-500 border-t-transparent mb-6">
        </div>
        <p class="text-xl font-semibold text-gray-700">正在分离音频，这可能需要几分钟...</p>
        <p class="text-sm text-gray-600 mt-2">使用 Demucs 模型分离人声、鼓、贝斯和其他乐器</p>
      </div>
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
const separating = ref(false)
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

const separateVoice = async () => {
  if (!selectedFile.value) {
    error.value = '请先选择音频文件'
    return
  }

  separating.value = true
  processing.value = true
  error.value = null

  try {
    const response = await audioAPI.separateVoice(selectedFile.value, 'htdemucs', 'vocals,drums,bass,other')

    // 获取文件名
    const contentDisposition = response.headers['content-disposition']
    let filename = selectedFile.value.name.replace(/\.[^/.]+$/, '') + '_separated'

    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }

    // 确定文件扩展名（ZIP或WAV）
    const contentType = response.headers['content-type'] || ''
    const isZip = contentType.includes('zip') || filename.endsWith('.zip')
    if (!filename.includes('.')) {
      filename += isZip ? '.zip' : '.wav'
    }

    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)

    alert(`音频分离完成！已下载: ${filename}`)
  } catch (err) {
    error.value = err.message || '音频分离失败'
  } finally {
    separating.value = false
    processing.value = false
  }
}

</script>
