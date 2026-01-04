<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header class="flex items-center justify-between p-4 md:p-6 border-b border-gray-200 bg-white">
    <nav class="flex gap-4 md:gap-6">
      <RouterLink
        to="/"
        class="px-4 py-2 text-gray-700 hover:text-primary hover:bg-primary/10 rounded transition-colors duration-300"
        active-class="!text-primary !bg-primary/10 font-medium"
      >
        Home
      </RouterLink>
      <RouterLink
        to="/audio"
        class="px-4 py-2 text-gray-700 hover:text-primary hover:bg-primary/10 rounded transition-colors duration-300"
        active-class="!text-primary !bg-primary/10 font-medium"
      >
        音频转录
      </RouterLink>
      <RouterLink
        to="/about"
        class="px-4 py-2 text-gray-700 hover:text-primary hover:bg-primary/10 rounded transition-colors duration-300"
        active-class="!text-primary !bg-primary/10 font-medium"
      >
        About
      </RouterLink>
    </nav>
  </header>

  <RouterView />
</template>
