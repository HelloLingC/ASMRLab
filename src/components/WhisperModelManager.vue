<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { audioAPI } from '../services/api'
import ModelCard from './ModelCard.vue'
import { Card, CardContent, Alert, AlertTitle, AlertDescription, Button } from './ui'

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

// 组件挂载时获取数据
onMounted(async () => {
  await fetchModels()
  await fetchModelStatuses()

  // 每5秒更新一次状态
  //statusInterval.value = setInterval(fetchModelStatuses, 5000)
})

// 组件卸载时清除定时器
onUnmounted(() => {
  if (statusInterval.value) {
    clearInterval(statusInterval.value)
  }
})
</script>

<template>
  <div>
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
    <Alert v-if="error" variant="destructive" class="mb-6">
      <AlertTitle>错误</AlertTitle>
      <AlertDescription>{{ error }}</AlertDescription>
    </Alert>

    <!-- Loading State -->
    <Card v-if="loading" class="p-12 text-center">
      <CardContent class="pt-6">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mb-4">
        </div>
        <p class="text-lg font-medium">加载模型列表中...</p>
      </CardContent>
    </Card>

    <!-- Model Cards Grid -->
    <div v-else-if="Object.keys(models).length > 0" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-12">
      <ModelCard v-for="(model, modelSize) in models" :key="modelSize" :model="model" :model-size="modelSize"
        :status="modelStatuses[modelSize]" @download="downloadModel" @delete="deleteModel" />
    </div>

    <!-- Empty State -->
    <Card v-else class="p-12 text-center">
      <CardContent class="pt-6">
        <div class="text-6xl mb-4">📦</div>
        <p class="text-xl font-semibold mb-6">无法加载模型列表</p>
        <Button @click="fetchModels" size="lg">
          重试
        </Button>
      </CardContent>
    </Card>
  </div>
</template>
