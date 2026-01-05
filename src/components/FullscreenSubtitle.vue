<template>
    <Transition name="fade">
        <div v-if="modelValue"
            class="fixed inset-0 z-50 bg-gradient-to-br from-slate-900 via-purple-900 to-indigo-900 flex flex-col items-center justify-center p-8"
            tabindex="-1" @keydown.esc="handleEscape">
            <div class="absolute top-4 right-4 z-10">
                <Button @click="handleClose" variant="secondary" size="lg"
                    class="backdrop-blur-md bg-black/30 hover:bg-black/50 text-white border border-white/20 flex items-center gap-2">
                    <span>退出全屏</span>
                    <span>⤓</span>
                </Button>
            </div>
            <div class="text-center max-w-7xl w-full px-8 flex-1 flex items-center justify-center">
                <p v-if="currentCaption || lastValidCaption"
                    class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-light text-white leading-relaxed drop-shadow-2xl animate-fade-in">
                    {{ currentCaption || lastValidCaption }}
                </p>
                <p v-else class="text-4xl md:text-5xl text-white/40 font-light">
                    字幕将在这里显示
                </p>
            </div>
            <!-- Progress Bar -->
            <div class="absolute bottom-0 left-0 right-0 w-full h-1 bg-black/20">
                <div class="h-full bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 transition-all duration-300 ease-out"
                    :style="{ width: progressPercentage + '%' }"></div>
            </div>
        </div>
    </Transition>
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { Button } from '@/components/ui/button'

const props = defineProps({
    modelValue: {
        type: Boolean,
        required: true
    },
    currentCaption: {
        type: String,
        default: ''
    },
    lastValidCaption: {
        type: String,
        default: ''
    },
    progressPercentage: {
        type: Number,
        default: 0
    }
})

const emit = defineEmits(['update:modelValue', 'close'])

const handleClose = () => {
    emit('update:modelValue', false)
    emit('close')
}

const handleEscape = (event) => {
    if (event.key === 'Escape' && props.modelValue) {
        handleClose()
    }
}

// Watch for modelValue changes to manage body overflow
watch(() => props.modelValue, (newValue) => {
    if (newValue) {
        document.body.style.overflow = 'hidden'
    } else {
        document.body.style.overflow = ''
    }
}, { immediate: true })

onMounted(() => {
    window.addEventListener('keydown', handleEscape)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleEscape)
    document.body.style.overflow = ''
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
