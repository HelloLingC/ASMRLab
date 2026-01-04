<template>
  <div class="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Hero Section -->
      <div class="text-center mb-12">
        <div class="inline-block mb-6">
          <div class="w-24 h-24 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl transform rotate-6 hover:rotate-0 transition-transform duration-300">
            <span class="text-5xl">🎵</span>
          </div>
        </div>
        <h1 class="text-6xl font-bold text-white mb-6 drop-shadow-lg">AudioLab</h1>
        <p class="text-2xl text-white/90 font-medium mb-4">AI-powered Audio Processing Tool</p>
        <p class="text-lg text-white/80 max-w-2xl mx-auto">
          强大的音频处理平台，集成了 Whisper AI 语音转录、音频分析和处理功能
        </p>
      </div>

      <!-- Features Grid -->
      <div class="grid md:grid-cols-2 gap-6 mb-12">
        <div class="glass rounded-2xl p-8 shadow-xl border border-white/20 card-hover">
          <div class="text-5xl mb-4">🎤</div>
          <h3 class="text-2xl font-bold text-gray-800 mb-3">AI 语音转录</h3>
          <p class="text-gray-700 leading-relaxed">
            使用 OpenAI Whisper 模型进行高精度语音转录，支持多种语言和模型大小选择。
          </p>
        </div>

        <div class="glass rounded-2xl p-8 shadow-xl border border-white/20 card-hover">
          <div class="text-5xl mb-4">🎚️</div>
          <h3 class="text-2xl font-bold text-gray-800 mb-3">音频处理</h3>
          <p class="text-gray-700 leading-relaxed">
            提供音频分析、降噪、格式转换等多种音频处理功能，满足您的各种需求。
          </p>
        </div>

        <div class="glass rounded-2xl p-8 shadow-xl border border-white/20 card-hover">
          <div class="text-5xl mb-4">🎧</div>
          <h3 class="text-2xl font-bold text-gray-800 mb-3">音频播放器</h3>
          <p class="text-gray-700 leading-relaxed">
            支持音频播放和 SRT 字幕同步显示，让您轻松查看转录结果。
          </p>
        </div>

        <div class="glass rounded-2xl p-8 shadow-xl border border-white/20 card-hover">
          <div class="text-5xl mb-4">🤖</div>
          <h3 class="text-2xl font-bold text-gray-800 mb-3">模型管理</h3>
          <p class="text-gray-700 leading-relaxed">
            灵活管理 Whisper 模型，支持下载、删除和状态监控，方便您选择最适合的模型。
          </p>
        </div>
      </div>

      <!-- Tech Stack -->
      <div class="glass rounded-2xl p-8 shadow-xl border border-white/20 mb-12">
        <h2 class="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-3">
          <span>⚙️</span>
          <span>技术栈</span>
        </h2>
        <div class="grid md:grid-cols-3 gap-4">
          <div class="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-200">
            <div class="font-bold text-blue-900 mb-2">前端</div>
            <div class="text-sm text-gray-700">Vue.js 3 + Vite + Tailwind CSS</div>
          </div>
          <div class="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-200">
            <div class="font-bold text-green-900 mb-2">后端</div>
            <div class="text-sm text-gray-700">FastAPI + Python</div>
          </div>
          <div class="p-4 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
            <div class="font-bold text-purple-900 mb-2">AI 模型</div>
            <div class="text-sm text-gray-700">OpenAI Whisper</div>
          </div>
        </div>
      </div>

      <!-- CTA Section -->
      <div class="glass rounded-2xl p-8 shadow-xl border border-white/20 text-center">
        <h2 class="text-3xl font-bold text-gray-800 mb-4">开始使用 AudioLab</h2>
        <p class="text-gray-700 mb-6 text-lg">
          立即体验强大的 AI 音频处理功能
        </p>
        <div class="flex gap-4 justify-center flex-wrap">
          <router-link
            to="/"
            class="px-8 py-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            🏠 返回首页
          </router-link>
          <router-link
            to="/audio"
            class="px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-600 text-white rounded-lg hover:from-blue-600 hover:to-cyan-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            🎤 开始转录
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// No script needed for this view
</script>
