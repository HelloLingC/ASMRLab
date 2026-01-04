<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen">
    <!-- Modern Navigation Bar -->
    <header class="glass sticky top-0 z-50 shadow-lg">
      <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center space-x-2">
            <div
              class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
              <span class="text-white text-xl font-bold">A</span>
            </div>
            <span class="text-xl font-bold gradient-text hidden sm:block">AudioLab</span>
          </div>

          <!-- Navigation Links -->
          <div class="flex items-center space-x-1">
            <RouterLink to="/"
              class="px-4 py-2 rounded-lg text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 transition-all duration-200 font-medium text-sm"
              active-class="bg-indigo-100 text-indigo-600 shadow-sm">
              <span class="flex items-center gap-2">
                <span>🏠</span>
                <span>Home</span>
              </span>
            </RouterLink>
            <RouterLink to="/audio"
              class="px-4 py-2 rounded-lg text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 transition-all duration-200 font-medium text-sm"
              active-class="bg-indigo-100 text-indigo-600 shadow-sm">
              <span class="flex items-center gap-2">
                <span>🎤</span>
                <span>音频转录</span>
              </span>
            </RouterLink>
            <RouterLink to="/player"
              class="px-4 py-2 rounded-lg text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 transition-all duration-200 font-medium text-sm"
              active-class="bg-indigo-100 text-indigo-600 shadow-sm">
              <span class="flex items-center gap-2">
                <span>🎵</span>
                <span>音频播放器</span>
              </span>
            </RouterLink>
            <RouterLink to="/srt-translator"
              class="px-4 py-2 rounded-lg text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 transition-all duration-200 font-medium text-sm"
              active-class="bg-indigo-100 text-indigo-600 shadow-sm">
              <span class="flex items-center gap-2">
                <span>🌐</span>
                <span>SRT翻译</span>
              </span>
            </RouterLink>
            <RouterLink to="/about"
              class="px-4 py-2 rounded-lg text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 transition-all duration-200 font-medium text-sm"
              active-class="bg-indigo-100 text-indigo-600 shadow-sm">
              <span class="flex items-center gap-2">
                <span>ℹ️</span>
                <span>About</span>
              </span>
            </RouterLink>
          </div>
        </div>
      </nav>
    </header>

    <!-- Main Content -->
    <main class="min-h-[calc(100vh-4rem)]">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
/* Additional component-specific styles if needed */
</style>
