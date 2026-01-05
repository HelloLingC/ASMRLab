<template>
  <main class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold text-white mb-4 drop-shadow-lg">配置中心</h1>
        <p class="text-xl text-white/90 font-medium">管理 Whisper 模型和 LLM 配置</p>
      </div>

      <!-- Error Alert -->
      <Alert v-if="error" variant="destructive" class="mb-8">
        <AlertTitle>错误</AlertTitle>
        <AlertDescription class="flex justify-between items-center">
          <span>{{ error }}</span>
          <Button variant="ghost" size="sm" @click="error = null">关闭</Button>
        </AlertDescription>
      </Alert>

      <!-- Success Alert -->
      <Alert v-if="successMessage" class="mb-8 border-green-500 bg-green-50">
        <AlertTitle class="text-green-900">成功</AlertTitle>
        <AlertDescription class="flex justify-between items-center text-green-800">
          <span>{{ successMessage }}</span>
          <Button variant="ghost" size="sm" @click="successMessage = null">关闭</Button>
        </AlertDescription>
      </Alert>

      <!-- Loading State -->
      <Card v-if="loading" class="p-12 text-center">
        <CardContent class="pt-6">
          <div
            class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent mb-4">
          </div>
          <p class="text-lg font-medium">加载配置中...</p>
        </CardContent>
      </Card>

      <!-- Configuration Form -->
      <div v-else class="space-y-8">
        <!-- Two Column Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
          <!-- Whisper Model Configuration -->
          <Card class="p-8">
            <CardHeader>
              <CardTitle class="flex items-center gap-3">
                <span>🎤</span>
                <span>Whisper 模型配置</span>
              </CardTitle>
            </CardHeader>
            <CardContent>

              <div class="space-y-6">
                <div>
                  <Label class="mb-2">
                    默认 Whisper 模型
                  </Label>
                  <Select v-model="config.whisper_default_model" class="w-full">
                    <option v-for="(model, size) in availableModels" :key="size" :value="size">
                      {{ model.name }} ({{ model.size_mb }} MB)
                    </option>
                  </Select>
                  <p class="mt-2 text-sm text-muted-foreground">
                    选择用于音频转录的默认 Whisper 模型。较大的模型通常更准确但需要更多资源。
                  </p>
                </div>

                <!-- Model Management Section -->
                <div v-if="Object.keys(availableModels).length > 0">
                  <div class="flex items-center justify-between mb-3">
                    <Label>模型管理</Label>
                    <Button @click="refreshModelStatuses" :disabled="loadingModelStatuses" variant="outline" size="sm">
                      <span v-if="loadingModelStatuses"
                        class="inline-block animate-spin rounded-full h-3 w-3 border-2 border-gray-400 border-t-transparent mr-2"></span>
                      <span>{{ loadingModelStatuses ? '刷新中...' : '🔄 刷新状态' }}</span>
                    </Button>
                  </div>
                  <div class="space-y-2 max-h-96 overflow-y-auto bg-muted/50 p-4 rounded-lg border">
                    <div v-for="(model, modelSize) in availableModels" :key="modelSize"
                      class="flex items-center justify-between p-3 rounded-lg border bg-background hover:shadow-md transition-all"
                      :class="{ 'border-green-300 bg-green-50/50': modelStatuses[modelSize]?.status === 'loaded', 'border-blue-300 bg-blue-50/50': modelStatuses[modelSize]?.status === 'downloading' }">
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-2 mb-1">
                          <span class="text-lg font-semibold">{{ model.name }}</span>
                          <Badge variant="secondary">{{ model.size_mb }} MB</Badge>
                          <span class="text-sm" :title="getStatusText(modelStatuses[modelSize]?.status)">
                            {{ getStatusIcon(modelStatuses[modelSize]?.status) }}
                          </span>
                        </div>
                        <p class="text-xs text-muted-foreground">{{ getStatusText(modelStatuses[modelSize]?.status) }}
                        </p>
                      </div>
                      <div class="flex items-center gap-2 ml-4">
                        <Button
                          v-if="modelStatuses[modelSize]?.status === 'not_downloaded' || modelStatuses[modelSize]?.status === 'error'"
                          @click="downloadModel(modelSize)" size="sm">
                          下载
                        </Button>
                        <Button v-else-if="modelStatuses[modelSize]?.status === 'downloading'" disabled size="sm">
                          下载中...
                        </Button>
                        <Button v-else-if="modelStatuses[modelSize]?.status === 'loaded'"
                          @click="deleteModel(modelSize)" variant="destructive" size="sm" title="删除模型">
                          🗑️
                        </Button>
                      </div>
                    </div>
                  </div>
                  <p class="mt-2 text-xs text-muted-foreground">
                    管理已下载的 Whisper 模型。下载模型后即可使用。
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <!-- LLM Configuration -->
          <Card class="p-8">
            <CardHeader>
              <CardTitle class="flex items-center gap-3">
                <span>🤖</span>
                <span>LLM 配置 (用于翻译)</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="space-y-4">
                <!-- OpenAI API Key -->
                <div>
                  <Label class="mb-2">
                    OpenAI API 密钥
                    <span class="text-destructive">*</span>
                  </Label>
                  <div class="relative">
                    <Input v-model="config.openai_api_key" :type="showApiKey ? 'text' : 'password'"
                      :placeholder="hasApiKey ? 'API密钥已设置（输入新密钥以更新）' : '请输入您的 OpenAI API 密钥'" class="pr-12"
                      :class="{ 'border-green-500': hasApiKey }" />
                    <Button v-if="hasApiKey && config.openai_api_key" @click="toggleApiKeyVisibility" type="button"
                      variant="ghost" size="icon" class="absolute right-1 top-1/2 transform -translate-y-1/2">
                      {{ showApiKey ? '👁️‍🗨️' : '👁️' }}
                    </Button>
                  </div>
                  <p class="mt-2 text-sm text-muted-foreground">
                    用于字幕翻译功能。您可以从 <a href="https://platform.openai.com/api-keys" target="_blank"
                      class="text-primary hover:underline">OpenAI Platform</a> 获取 API 密钥。
                  </p>
                </div>

                <!-- OpenAI Model -->
                <div>
                  <Label class="mb-2">OpenAI 模型</Label>
                  <Select v-model="config.openai_model" class="w-full">
                    <option value="gpt-3.5-turbo">gpt-3.5-turbo (推荐，快速且经济)</option>
                    <option value="gpt-4">gpt-4 (更准确但更慢)</option>
                    <option value="gpt-4-turbo-preview">gpt-4-turbo-preview (最新版本)</option>
                    <option value="gpt-4o">gpt-4o (优化版本)</option>
                  </Select>
                  <p class="mt-2 text-sm text-muted-foreground">
                    选择用于翻译的 OpenAI 模型。gpt-3.5-turbo 通常足够且更经济。
                  </p>
                </div>

                <!-- Custom Base URL (Optional) -->
                <div>
                  <Label class="mb-2">API Base URL (可选)</Label>
                  <Input v-model="config.openai_base_url" type="text" placeholder="留空使用默认 OpenAI API，或输入自定义 API 端点" />
                  <p class="mt-2 text-sm text-muted-foreground">
                    用于使用兼容 OpenAI API 的自定义端点（如本地部署的模型或代理服务）。
                  </p>
                </div>

                <!-- Temperature -->
                <div>
                  <Label class="mb-2">温度 (Temperature): {{ config.openai_temperature }}</Label>
                  <Slider v-model="config.openai_temperature" :min="0" :max="1" :step="0.1" class="w-full" />
                  <div class="flex justify-between text-xs text-muted-foreground mt-1">
                    <span>0.0 (确定性)</span>
                    <span>0.5 (平衡)</span>
                    <span>1.0 (创造性)</span>
                  </div>
                  <p class="mt-2 text-sm text-muted-foreground">
                    控制翻译的随机性。较低的值使翻译更一致，较高的值使翻译更多样化。
                  </p>
                </div>

                <!-- Max Tokens -->
                <div>
                  <Label class="mb-2">最大 Token 数</Label>
                  <Input v-model.number="config.openai_max_tokens" type="number" :min="100" :max="2000" :step="100" />
                  <p class="mt-2 text-sm text-muted-foreground">
                    每次翻译请求的最大 token 数。字幕通常较短，500-1000 通常足够。
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-4 justify-center">
          <Button @click="saveConfig" :disabled="saving" size="lg">
            <span v-if="saving"
              class="inline-block animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2"></span>
            <span>{{ saving ? '保存中...' : '💾 保存配置' }}</span>
          </Button>
          <Button @click="resetConfig" variant="secondary" size="lg">
            🔄 重置
          </Button>
          <Button @click="validateConfig" variant="outline" size="lg">
            ✓ 验证配置
          </Button>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { audioAPI } from '../services/api'
import { Button, Card, CardHeader, CardTitle, CardContent, Input, Label, Select, Slider, Alert, AlertTitle, AlertDescription, Badge } from '@/components/ui'

const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const successMessage = ref(null)
const config = ref({
  whisper_default_model: 'base',
  openai_api_key: '',
  openai_model: 'gpt-3.5-turbo',
  openai_base_url: '',
  openai_temperature: 0.3,
  openai_max_tokens: 500
})
const originalConfig = ref(null)
const availableModels = ref({})
const modelStatuses = ref({})
const loadingModelStatuses = ref(false)
const hasApiKey = ref(false)
const showApiKey = ref(false)

// Fetch available models
const fetchModels = async () => {
  try {
    const response = await audioAPI.getModels()
    availableModels.value = response.models
    // Fetch model statuses after getting models
    await fetchModelStatuses()
  } catch (err) {
    console.error('获取模型列表失败:', err)
  }
}

// Fetch model statuses
const fetchModelStatuses = async () => {
  if (Object.keys(availableModels.value).length === 0) return

  try {
    loadingModelStatuses.value = true
    const statuses = {}
    for (const modelSize of Object.keys(availableModels.value)) {
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
  } finally {
    loadingModelStatuses.value = false
  }
}

// Refresh model statuses
const refreshModelStatuses = async () => {
  await fetchModelStatuses()
}

// Download model
const downloadModel = async (modelSize) => {
  try {
    error.value = null
    successMessage.value = null

    await audioAPI.downloadModel(modelSize)

    // Update status immediately
    modelStatuses.value[modelSize] = {
      status: 'downloading',
      model_size: modelSize,
      message: '开始下载...',
    }

    successMessage.value = `开始下载模型 "${availableModels.value[modelSize]?.name}"`

    // Refresh statuses after a delay
    setTimeout(fetchModelStatuses, 2000)
  } catch (err) {
    error.value = err.message || '下载模型失败'
  }
}

// Delete model
const deleteModel = async (modelSize) => {
  const modelName = availableModels.value[modelSize]?.name
  if (!confirm(`确定要删除模型 "${modelName}" 吗？\n\n这将从磁盘中永久删除模型文件。`)) {
    return
  }

  try {
    error.value = null
    successMessage.value = null

    await audioAPI.deleteModel(modelSize)

    // Update status
    modelStatuses.value[modelSize] = {
      status: 'not_downloaded',
      model_size: modelSize,
      message: '模型已删除',
    }

    successMessage.value = `模型 "${modelName}" 已删除`
  } catch (err) {
    error.value = err.message || '删除模型失败'
  }
}

// Get status icon
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

// Get status text
const getStatusText = (status) => {
  switch (status) {
    case 'loaded':
      return '已下载'
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

// Fetch current config
const fetchConfig = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await audioAPI.getConfig()
    const configData = response.config

    // Store original config
    originalConfig.value = { ...configData }

    // Update config (preserve API key if it exists, but don't overwrite if user has entered one)
    // If API key is masked (contains *), keep the current value in the form
    const currentApiKey = config.value.openai_api_key
    const maskedApiKey = configData.openai_api_key || ''
    const isMasked = maskedApiKey.includes('*')

    config.value = {
      whisper_default_model: configData.whisper_default_model || 'base',
      openai_api_key: (isMasked && currentApiKey && !currentApiKey.includes('*')) ? currentApiKey : (isMasked ? '' : (configData.openai_api_key || '')),
      openai_model: configData.openai_model || 'gpt-3.5-turbo',
      openai_base_url: configData.openai_base_url || '',
      openai_temperature: configData.openai_temperature || 0.3,
      openai_max_tokens: configData.openai_max_tokens || 500
    }

    hasApiKey.value = response.has_api_key
  } catch (err) {
    error.value = err.message || '获取配置失败'
  } finally {
    loading.value = false
  }
}

// Save config
const saveConfig = async () => {
  try {
    saving.value = true
    error.value = null
    successMessage.value = null

    await audioAPI.updateConfig(config.value)
    successMessage.value = '配置保存成功！'

    // Refresh config to get updated values
    await fetchConfig()
  } catch (err) {
    error.value = err.message || '保存配置失败'
  } finally {
    saving.value = false
  }
}

// Reset config
const resetConfig = () => {
  if (confirm('确定要重置配置吗？这将恢复为默认值。')) {
    if (originalConfig.value) {
      config.value = { ...originalConfig.value }
    } else {
      config.value = {
        whisper_default_model: 'base',
        openai_api_key: '',
        openai_model: 'gpt-3.5-turbo',
        openai_base_url: '',
        openai_temperature: 0.3,
        openai_max_tokens: 500
      }
    }
    successMessage.value = '配置已重置'
  }
}

// Validate config
const validateConfig = async () => {
  try {
    error.value = null
    successMessage.value = null

    const result = await audioAPI.validateConfig()

    if (result.valid) {
      if (result.warnings && result.warnings.length > 0) {
        successMessage.value = `配置有效，但有警告：${result.warnings.join('; ')}`
      } else {
        successMessage.value = '配置验证通过！'
      }
    } else {
      error.value = `配置验证失败：${result.errors.join('; ')}`
    }
  } catch (err) {
    error.value = err.message || '验证配置失败'
  }
}

// Toggle API key visibility
const toggleApiKeyVisibility = () => {
  showApiKey.value = !showApiKey.value
}

// Component mounted
onMounted(async () => {
  await Promise.all([fetchModels(), fetchConfig()])
})
</script>
