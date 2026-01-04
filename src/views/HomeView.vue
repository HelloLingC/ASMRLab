<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { audioAPI } from '../services/api'

const models = ref({})
const modelStatuses = ref({})
const loading = ref(false)
const error = ref(null)
const statusInterval = ref(null)

// 获取模型列表
const fetchModels = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await audioAPI.getModels()
    models.value = response.models
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// 获取所有模型状态
const fetchModelStatuses = async () => {
  if (Object.keys(models.value).length === 0) return

  try {
    const statuses = {}
    for (const modelSize of Object.keys(models.value)) {
      try {
        const response = await audioAPI.getModelStatus(modelSize)
        statuses[modelSize] = response
      } catch (err) {
        statuses[modelSize] = {
          status: 'error',
          message: err.message,
          model_size: modelSize,
        }
      }
    }
    modelStatuses.value = statuses
  } catch (err) {
    console.error('获取模型状态失败:', err)
  }
}

// 下载模型
const downloadModel = async (modelSize) => {
  try {
    error.value = null
    const response = await audioAPI.downloadModel(modelSize)

    // 立即更新状态
    modelStatuses.value[modelSize] = {
      status: 'downloading',
      model_size: modelSize,
      message: '开始下载...',
    }

    // 几秒后刷新状态
    setTimeout(fetchModelStatuses, 2000)
  } catch (err) {
    error.value = err.message
  }
}

// 删除模型
const deleteModel = async (modelSize) => {
  if (
    !confirm(
      `确定要删除模型 "${models.value[modelSize]?.name}" 吗？\n\n这将从磁盘中永久删除模型文件。`,
    )
  ) {
    return
  }

  try {
    error.value = null
    const response = await audioAPI.deleteModel(modelSize)

    // 更新状态为未下载
    modelStatuses.value[modelSize] = {
      status: 'not_downloaded',
      model_size: modelSize,
      message: '模型已删除',
    }

    // 显示成功消息
    alert(response.message)
  } catch (err) {
    error.value = err.message
  }
}

// 获取状态图标
const getStatusIcon = (status) => {
  switch (status) {
    case 'loaded':
      return '✅'
    case 'downloading':
      return '⏳'
    case 'not_downloaded':
      return '⬇️'
    case 'error':
      return '❌'
    default:
      return '❓'
  }
}

// 获取状态文本
const getStatusText = (status) => {
  switch (status) {
    case 'loaded':
      return '已加载'
    case 'downloading':
      return '下载中'
    case 'not_downloaded':
      return '未下载'
    case 'error':
      return '错误'
    default:
      return '未知'
  }
}

// 获取状态颜色
const getStatusColor = (status) => {
  switch (status) {
    case 'loaded':
      return 'bg-green-100 text-green-700 border-green-300'
    case 'downloading':
      return 'bg-blue-100 text-blue-700 border-blue-300'
    case 'not_downloaded':
      return 'bg-gray-100 text-gray-700 border-gray-300'
    case 'error':
      return 'bg-red-100 text-red-700 border-red-300'
    default:
      return 'bg-gray-100 text-gray-700 border-gray-300'
  }
}

// 组件挂载时获取数据
onMounted(async () => {
  await fetchModels()
  await fetchModelStatuses()

  // 每5秒更新一次状态
  statusInterval.value = setInterval(fetchModelStatuses, 5000)
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (statusInterval.value) {
    clearInterval(statusInterval.value)
  }
})
</script>

<template>
  <main class="min-h-screen w-full py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header Section -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-white mb-4 drop-shadow-lg">
          Whisper 模型管理器
        </h1>
        <p class="text-xl text-white/90 font-medium">
          管理您的 AI 语音转录模型
        </p>
      </div>

      <!-- Error Alert -->
      <div v-if="error" class="mb-6 glass rounded-2xl p-4 border-l-4 border-red-500 shadow-lg">
        <div class="flex items-center gap-3">
          <span class="text-2xl">⚠️</span>
          <p class="font-semibold text-red-700">{{ error }}</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="glass rounded-2xl p-12 text-center shadow-xl">
        <div
          class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-indigo-500 border-t-transparent mb-4">
        </div>
        <p class="text-lg font-medium text-gray-700">加载模型列表中...</p>
      </div>

      <!-- Model Cards Grid -->
      <div v-else-if="Object.keys(models).length > 0" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-12">
        <div v-for="(model, modelSize) in models" :key="modelSize"
          class="glass rounded-2xl p-6 shadow-xl card-hover border border-white/20">
          <!-- Card Header -->
          <div class="flex items-start justify-between mb-6">
            <div class="flex-1">
              <h3 class="text-2xl font-bold text-gray-800 mb-2">{{ model.name }}</h3>
              <p class="text-sm text-gray-600 leading-relaxed">{{ model.description }}</p>
            </div>
            <div class="ml-4 text-3xl">
              <span>{{ getStatusIcon(modelStatuses[modelSize]?.status) }}</span>
            </div>
          </div>

          <!-- Model Info -->
          <div class="space-y-3 mb-6">
            <div class="flex justify-between items-center p-3 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg">
              <span class="text-sm font-medium text-gray-600">大小:</span>
              <span class="font-bold text-indigo-700">{{ model.size_mb }} MB</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg">
              <span class="text-sm font-medium text-gray-600">速度:</span>
              <span class="font-bold text-blue-700">{{ model.speed }}</span>
            </div>
            <div class="flex justify-between items-center p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg">
              <span class="text-sm font-medium text-gray-600">精度:</span>
              <span class="font-bold text-green-700">{{ model.accuracy }}</span>
            </div>
            <div class="flex justify-between items-center p-3 rounded-lg border-2"
              :class="getStatusColor(modelStatuses[modelSize]?.status)">
              <span class="text-sm font-medium">状态:</span>
              <span class="font-bold">
                {{ getStatusText(modelStatuses[modelSize]?.status) }}
              </span>
            </div>
          </div>

          <!-- Status Message -->
          <div v-if="modelStatuses[modelSize]?.message"
            class="mb-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-700 border border-gray-200">
            {{ modelStatuses[modelSize].message }}
          </div>

          <!-- Download Progress -->
          <div v-if="modelStatuses[modelSize]?.status === 'downloading'" class="mb-4">
            <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
              <div
                class="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all duration-500 shadow-lg"
                :style="{ width: `${modelStatuses[modelSize]?.progress || 0}%` }"></div>
            </div>
            <p class="text-xs text-gray-600 mt-2 text-center font-medium">
              {{ modelStatuses[modelSize]?.progress || 0 }}% 完成
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-2">
            <button v-if="modelStatuses[modelSize]?.status === 'not_downloaded'" @click="downloadModel(modelSize)"
              class="flex-1 px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 text-sm font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
              下载模型
            </button>
            <button v-else-if="modelStatuses[modelSize]?.status === 'downloading'" disabled
              class="flex-1 px-4 py-3 bg-gray-400 text-white rounded-lg cursor-not-allowed text-sm font-semibold">
              下载中...
            </button>
            <div v-else-if="modelStatuses[modelSize]?.status === 'loaded'" class="flex gap-2 flex-1">
              <button
                class="flex-1 px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all duration-200 text-sm font-semibold shadow-lg">
                ✓ 已就绪
              </button>
              <button @click="deleteModel(modelSize)"
                class="px-4 py-3 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 text-sm font-semibold shadow-lg hover:shadow-xl"
                title="删除模型">
                🗑️
              </button>
            </div>
            <button v-else-if="modelStatuses[modelSize]?.status === 'error'" @click="downloadModel(modelSize)"
              class="flex-1 px-4 py-3 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 text-sm font-semibold shadow-lg hover:shadow-xl">
              重试下载
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="glass rounded-2xl p-12 text-center shadow-xl">
        <div class="text-6xl mb-4">📦</div>
        <p class="text-xl font-semibold text-gray-700 mb-6">无法加载模型列表</p>
        <button @click="fetchModels"
          class="px-8 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
          重试
        </button>
      </div>

      <!-- Instructions Section -->
      <div class="glass rounded-2xl p-8 shadow-xl border border-white/20">
        <h2 class="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-3">
          <span>📚</span>
          <span>使用说明</span>
        </h2>
        <div class="grid md:grid-cols-2 gap-6">
          <div class="p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
            <h3 class="font-bold text-indigo-900 mb-2 flex items-center gap-2">
              <span>🎯</span>
              <span>模型选择</span>
            </h3>
            <p class="text-gray-700 text-sm leading-relaxed">
              根据您的需求选择合适的模型。Tiny 模型最小最快，但精度较低；Large 模型精度最高，但需要更多存储空间和处理时间。
            </p>
          </div>
          <div class="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-100">
            <h3 class="font-bold text-blue-900 mb-2 flex items-center gap-2">
              <span>🚀</span>
              <span>首次使用</span>
            </h3>
            <p class="text-gray-700 text-sm leading-relaxed">
              使用转录功能前，请先下载所需的模型。下载完成后，模型会自动加载到内存中。
            </p>
          </div>
          <div class="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-100">
            <h3 class="font-bold text-green-900 mb-2 flex items-center gap-2">
              <span>💾</span>
              <span>存储空间</span>
            </h3>
            <p class="text-gray-700 text-sm leading-relaxed">
              确保有足够的磁盘空间存储模型文件。模型文件保存在服务器的 models 目录中。
            </p>
          </div>
          <div class="p-4 bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl border border-orange-100">
            <h3 class="font-bold text-orange-900 mb-2 flex items-center gap-2">
              <span>⚡</span>
              <span>性能考虑</span>
            </h3>
            <p class="text-gray-700 text-sm leading-relaxed">
              较大的模型需要更多 RAM 和处理时间，但提供更好的转录精度。
            </p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>
