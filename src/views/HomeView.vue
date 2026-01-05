<script setup>
import { ref, onMounted } from 'vue'
import { audioAPI } from '../services/api'
import SystemInfoSection from '../components/SystemInfoSection.vue'
import InstructionsSection from '../components/InstructionsSection.vue'

const systemInfo = ref(null)
const systemInfoLoading = ref(false)

// 获取系统信息 (CUDA/cuDNN)
const fetchSystemInfo = async () => {
  try {
    systemInfoLoading.value = true
    const response = await audioAPI.healthCheck()
    systemInfo.value = response
  } catch (err) {
    console.error('获取系统信息失败:', err)
  } finally {
    systemInfoLoading.value = false
  }
}

// 组件挂载时获取数据
onMounted(async () => {
  await fetchSystemInfo()
})
</script>

<template>
  <main class="min-h-screen w-full py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">

      <!-- System Info Section (CUDA/cuDNN) -->
      <SystemInfoSection :system-info="systemInfo" :loading="systemInfoLoading" @retry="fetchSystemInfo" />

      <!-- Instructions Section -->
      <InstructionsSection />
    </div>
  </main>
</template>
