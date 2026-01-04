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
      return 'text-green-600'
    case 'downloading':
      return 'text-blue-600'
    case 'not_downloaded':
      return 'text-gray-600'
    case 'error':
      return 'text-red-600'
    default:
      return 'text-gray-600'
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
  <main class="min-h-screen p-8 bg-gray-50">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-800 mb-4">Whisper 模型管理器</h1>
        <p class="text-lg text-gray-600">管理您的 AI 语音转录模型</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
        <p class="font-medium">错误: {{ error }}</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="text-center p-8">
        <p class="text-lg text-gray-600">加载模型列表中...</p>
      </div>

      <!-- 模型列表 -->
      <div
        v-else-if="Object.keys(models).length > 0"
        class="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
      >
        <div
          v-for="(model, modelSize) in models"
          :key="modelSize"
          class="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow duration-300"
        >
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="text-xl font-semibold text-gray-800">{{ model.name }}</h3>
              <p class="text-sm text-gray-600 mt-1">{{ model.description }}</p>
            </div>
            <div class="text-2xl">
              <span :class="getStatusColor(modelStatuses[modelSize]?.status)">
                {{ getStatusIcon(modelStatuses[modelSize]?.status) }}
              </span>
            </div>
          </div>

          <div class="space-y-2 mb-4">
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">大小:</span>
              <span class="font-medium">{{ model.size_mb }} MB</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">速度:</span>
              <span class="font-medium">{{ model.speed }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">精度:</span>
              <span class="font-medium">{{ model.accuracy }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-600">状态:</span>
              <span :class="getStatusColor(modelStatuses[modelSize]?.status)" class="font-medium">
                {{ getStatusText(modelStatuses[modelSize]?.status) }}
              </span>
            </div>
          </div>

          <!-- 状态消息 -->
          <div
            v-if="modelStatuses[modelSize]?.message"
            class="mb-4 p-2 bg-gray-50 rounded text-sm text-gray-700"
          >
            {{ modelStatuses[modelSize].message }}
          </div>

          <!-- 下载进度 -->
          <div v-if="modelStatuses[modelSize]?.status === 'downloading'" class="mb-4">
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${modelStatuses[modelSize]?.progress || 0}%` }"
              ></div>
            </div>
            <p class="text-xs text-gray-600 mt-1 text-center">
              {{ modelStatuses[modelSize]?.progress || 0 }}% 完成
            </p>
          </div>

          <!-- 操作按钮 -->
          <div class="flex gap-2">
            <button
              v-if="modelStatuses[modelSize]?.status === 'not_downloaded'"
              @click="downloadModel(modelSize)"
              class="flex-1 px-4 py-2 bg-primary text-white rounded hover:bg-primary-hover transition-colors duration-300 text-sm font-medium"
            >
              下载模型
            </button>
            <button
              v-else-if="modelStatuses[modelSize]?.status === 'downloading'"
              disabled
              class="flex-1 px-4 py-2 bg-gray-400 text-white rounded cursor-not-allowed text-sm font-medium"
            >
              下载中...
            </button>
            <div
              v-else-if="modelStatuses[modelSize]?.status === 'loaded'"
              class="flex gap-2 flex-1"
            >
              <button
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors duration-300 text-sm font-medium"
              >
                ✓ 已就绪
              </button>
              <button
                @click="deleteModel(modelSize)"
                class="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors duration-300 text-sm font-medium"
                title="删除模型"
              >
                🗑️
              </button>
            </div>
            <button
              v-else-if="modelStatuses[modelSize]?.status === 'error'"
              @click="downloadModel(modelSize)"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors duration-300 text-sm font-medium"
            >
              重试下载
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="text-center p-12 bg-white rounded-lg shadow-md">
        <p class="text-lg text-gray-600">无法加载模型列表</p>
        <button
          @click="fetchModels"
          class="mt-4 px-6 py-3 bg-primary text-white rounded hover:bg-primary-hover transition-colors duration-300 font-medium"
        >
          重试
        </button>
      </div>

      <!-- 使用说明 -->
      <div class="mt-12 bg-white rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-semibold text-gray-800 mb-4">使用说明</h2>
        <div class="space-y-3 text-gray-700">
          <p>
            • <strong>模型选择:</strong> 根据您的需求选择合适的模型。Tiny
            模型最小最快，但精度较低；Large 模型精度最高，但需要更多存储空间和处理时间。
          </p>
          <p>
            •
            <strong>首次使用:</strong>
            使用转录功能前，请先下载所需的模型。下载完成后，模型会自动加载到内存中。
          </p>
          <p>
            • <strong>存储空间:</strong> 确保有足够的磁盘空间存储模型文件。模型文件保存在服务器的
            models 目录中。
          </p>
          <p>
            • <strong>性能考虑:</strong> 较大的模型需要更多 RAM 和处理时间，但提供更好的转录精度。
          </p>
        </div>
      </div>
    </div>
  </main>
</template>
