import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 通过Vite代理访问后端
  timeout: 30000, // 30秒超时，音频处理可能需要更长时间
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)

// API方法
export const audioAPI = {
  // 健康检查
  async healthCheck() {
    return await api.get('/health')
  },

  // 上传音频文件
  async uploadAudio(file) {
    const formData = new FormData()
    formData.append('file', file)
    return await api.post('/upload', formData)
  },

  // 处理音频文件
  async processAudio(file, operation = 'analyze') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('operation', operation)
    return await api.post('/process', formData)
  },

  // 使用Whisper转录音频
  async transcribeAudio(file, modelName = 'base', language = null) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model_name', modelName)
    if (language) {
      formData.append('language', language)
    }
    return await api.post('/transcribe', formData)
  },

  // 下载SRT字幕文件
  async downloadSRT(file, modelName = 'base', language = null) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model_name', modelName)
    formData.append('format', 'srt')
    if (language) {
      formData.append('language', language)
    }

    // 使用axios直接获取blob
    const response = await axios.post('/api/transcribe', formData, {
      responseType: 'blob',
      timeout: 30000,
    })

    return response
  },

  // 模型管理相关API
  async getModels() {
    return await api.get('/models')
  },

  async getModelStatus(modelName) {
    return await api.get('/model/status', { params: { model_name: modelName } })
  },

  async downloadModel(modelName, revision = null) {
    const params = { model_name: modelName }
    if (revision) params.revision = revision
    return await api.post('/model/download', null, { params })
  },

  async deleteModel(modelName) {
    return await api.delete('/model/delete', { params: { model_name: modelName } })
  },

  // 翻译SRT字幕文件
  async translateSRT(file, targetLanguage = 'en', sourceLanguage = null) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('target_language', targetLanguage)
    if (sourceLanguage) {
      formData.append('source_language', sourceLanguage)
    }

    // 使用axios直接获取blob
    const response = await axios.post('/api/translate-srt', formData, {
      responseType: 'blob',
      timeout: 120000, // 2分钟超时，翻译可能需要更长时间
    })

    return response
  },

  // 配置相关API
  async getConfig() {
    return await api.get('/config')
  },

  async updateConfig(configData) {
    return await api.post('/config', configData)
  },

  async validateConfig() {
    return await api.get('/config/validate')
  },

  // 语音分离相关API
  async separateVoice(file, model = 'htdemucs', stems = 'vocals,drums,bass,other') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('model', model)
    formData.append('stems', stems)

    // 使用axios直接获取blob（可能是单个文件或ZIP）
    const response = await axios.post('/api/separate-voice', formData, {
      responseType: 'blob',
      timeout: 300000, // 5分钟超时，分离可能需要较长时间
    })

    return response
  },
}

export default api
