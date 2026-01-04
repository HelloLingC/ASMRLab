<template>
    <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
        <div class="max-w-5xl mx-auto">
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-5xl font-bold text-white mb-4 drop-shadow-lg">SRT 字幕翻译</h1>
                <p class="text-xl text-white/90 font-medium">上传SRT字幕文件进行翻译</p>
            </div>

            <!-- Upload Section -->
            <div class="mb-8">
                <div class="glass rounded-2xl p-8 shadow-xl border border-white/20">
                    <h3 class="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-3">
                        <span>🌐</span>
                        <span>SRT 字幕翻译</span>
                    </h3>
                    <div class="mb-6">
                        <div class="glass rounded-xl p-8 text-center shadow-lg border-2 border-dashed border-white/30 hover:border-indigo-400 transition-all duration-300 cursor-pointer card-hover"
                            @drop.prevent="handleSrtDrop" @dragover.prevent>
                            <input ref="srtFileInput" type="file" accept=".srt" @change="handleSrtSelect"
                                class="hidden" />
                            <div v-if="!selectedSrtFile" class="upload-placeholder">
                                <div class="text-6xl mb-6">📄</div>
                                <p class="mb-6 text-xl font-semibold text-gray-700">拖拽SRT文件到此处或点击选择</p>
                                <button @click="$refs.srtFileInput.click()"
                                    class="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105">
                                    选择SRT文件
                                </button>
                            </div>
                            <div v-else class="flex flex-col items-center gap-4">
                                <div class="text-5xl">✅</div>
                                <div class="text-center">
                                    <p class="text-xl font-semibold text-gray-800 mb-2">
                                        已选择: <span class="text-indigo-600">{{ selectedSrtFile.name }}</span>
                                    </p>
                                    <p class="text-gray-600 font-medium">大小: {{ formatFileSize(selectedSrtFile.size) }}
                                    </p>
                                </div>
                                <button @click="clearSrtFile"
                                    class="px-6 py-3 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-lg hover:from-red-600 hover:to-pink-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl">
                                    清除文件
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="grid md:grid-cols-2 gap-6 mb-6" v-if="selectedSrtFile">
                        <div class="flex flex-col gap-2">
                            <label for="source-language" class="font-semibold text-gray-700 flex items-center gap-2">
                                <span>🔤</span>
                                <span>源语言 (可选):</span>
                            </label>
                            <select id="source-language" v-model="sourceLanguage" :disabled="translating"
                                class="p-4 border-2 border-gray-300 rounded-lg bg-white disabled:bg-gray-100 disabled:cursor-not-allowed text-base focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                                <option value="">自动检测</option>
                                <option value="zh">中文</option>
                                <option value="en">English</option>
                                <option value="ja">日本語</option>
                                <option value="ko">한국어</option>
                                <option value="es">Español</option>
                                <option value="fr">Français</option>
                                <option value="de">Deutsch</option>
                                <option value="ru">Русский</option>
                            </select>
                        </div>
                        <div class="flex flex-col gap-2">
                            <label for="target-language" class="font-semibold text-gray-700 flex items-center gap-2">
                                <span>🎯</span>
                                <span>目标语言:</span>
                            </label>
                            <select id="target-language" v-model="targetLanguage" :disabled="translating"
                                class="p-4 border-2 border-gray-300 rounded-lg bg-white disabled:bg-gray-100 disabled:cursor-not-allowed text-base focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200">
                                <option value="en">English</option>
                                <option value="zh">中文</option>
                                <option value="ja">日本語</option>
                                <option value="ko">한국어</option>
                                <option value="es">Español</option>
                                <option value="fr">Français</option>
                                <option value="de">Deutsch</option>
                                <option value="ru">Русский</option>
                            </select>
                        </div>
                    </div>
                    <button @click="translateSrt" :disabled="!selectedSrtFile || translating"
                        class="w-full px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-all duration-200 font-semibold text-lg shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
                        v-if="selectedSrtFile">
                        {{ translating ? '⏳ 翻译中...' : '🚀 开始翻译' }}
                    </button>
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
            <div class="glass rounded-2xl p-12 text-center shadow-xl" v-if="translating">
                <div
                    class="inline-block animate-spin rounded-full h-16 w-16 border-4 border-indigo-500 border-t-transparent mb-6">
                </div>
                <p class="text-xl font-semibold text-gray-700">翻译中，请稍候...</p>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { audioAPI } from '../services/api'

const srtFileInput = ref(null)
const selectedSrtFile = ref(null)
const translating = ref(false)
const error = ref(null)
const sourceLanguage = ref('')
const targetLanguage = ref('en')

const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const handleSrtSelect = (event) => {
    const file = event.target.files[0]
    if (file) {
        if (file.name.endsWith('.srt')) {
            selectedSrtFile.value = file
        } else {
            error.value = '请选择SRT文件'
        }
    }
}

const handleSrtDrop = (event) => {
    const file = event.dataTransfer.files[0]
    if (file && file.name.endsWith('.srt')) {
        selectedSrtFile.value = file
    } else {
        error.value = '请选择SRT文件'
    }
}

const clearSrtFile = () => {
    selectedSrtFile.value = null
    error.value = null
    if (srtFileInput.value) {
        srtFileInput.value.value = ''
    }
}

const translateSrt = async () => {
    if (!selectedSrtFile.value) {
        error.value = '请先选择SRT文件'
        return
    }

    translating.value = true
    error.value = null

    try {
        const sourceLang = sourceLanguage.value || null
        const response = await audioAPI.translateSRT(
            selectedSrtFile.value,
            targetLanguage.value,
            sourceLang,
        )

        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        const filename = selectedSrtFile.value.name.replace(/\.srt$/i, '') + `_translated_${targetLanguage.value}.srt`
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)

        alert('SRT翻译完成并已下载')
    } catch (err) {
        error.value = err.message || '翻译SRT失败'
    } finally {
        translating.value = false
    }
}
</script>
