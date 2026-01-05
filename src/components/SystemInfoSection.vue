<script setup>
import { defineProps } from 'vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

const props = defineProps({
    systemInfo: {
        type: Object,
        default: null
    },
    loading: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['retry'])

const handleRetry = () => {
    emit('retry')
}
</script>

<template>
    <Card class="p-8 mb-8">
        <CardHeader>
            <CardTitle class="flex items-center gap-3">
                <span>🖥️</span>
                <span>系统信息</span>
            </CardTitle>
        </CardHeader>
        <CardContent>
            <div v-if="loading" class="text-center py-8">
                <div
                    class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent mb-4">
                </div>
                <p class="text-muted-foreground">加载系统信息中...</p>
            </div>

            <div v-else-if="systemInfo" class="grid md:grid-cols-2 gap-6">
                <!-- CUDA Info -->
                <Card class="p-6"
                    :class="systemInfo.cuda?.available ? 'border-blue-300 bg-blue-50/50' : 'border-border'">
                    <CardHeader class="pb-3">
                        <div class="flex items-center justify-between">
                            <CardTitle class="text-xl flex items-center gap-2">
                                <span>{{ systemInfo.cuda?.available ? '✅' : '❌' }}</span>
                                <span>CUDA</span>
                            </CardTitle>
                            <Badge :variant="systemInfo.cuda?.available ? 'default' : 'secondary'">
                                {{ systemInfo.cuda?.available ? '可用' : '不可用' }}
                            </Badge>
                        </div>
                    </CardHeader>
                    <CardContent>

                        <div v-if="systemInfo.cuda?.available" class="space-y-2 text-sm">
                            <div class="flex justify-between items-center">
                                <span class="text-muted-foreground font-medium">设备数量:</span>
                                <span class="font-bold">{{ systemInfo.cuda.device_count }}</span>
                            </div>
                            <div v-if="systemInfo.cuda.cuda_version" class="flex justify-between items-center">
                                <span class="text-muted-foreground font-medium">CUDA 版本:</span>
                                <span class="font-bold">{{ systemInfo.cuda.cuda_version }}</span>
                            </div>
                            <div v-if="systemInfo.cuda.devices && systemInfo.cuda.devices.length > 0" class="mt-4">
                                <p class="text-muted-foreground font-medium mb-2">设备列表:</p>
                                <div class="space-y-2">
                                    <Card v-for="device in systemInfo.cuda.devices" :key="device.index" class="p-3">
                                        <div class="font-semibold">{{ device.name }}</div>
                                        <div v-if="device.total_memory_mb" class="text-xs text-muted-foreground mt-1">
                                            显存: {{ device.total_memory_mb }} MB
                                        </div>
                                    </Card>
                                </div>
                            </div>
                        </div>

                        <div v-else class="text-sm text-muted-foreground">
                            <p>{{ systemInfo.cuda?.error || 'CUDA未安装或不可用' }}</p>
                        </div>
                    </CardContent>
                </Card>

                <!-- cuDNN Info -->
                <Card class="p-6"
                    :class="systemInfo.cudnn?.available ? 'border-purple-300 bg-purple-50/50' : 'border-border'">
                    <CardHeader class="pb-3">
                        <div class="flex items-center justify-between">
                            <CardTitle class="text-xl flex items-center gap-2">
                                <span>{{ systemInfo.cudnn?.available ? '✅' : '❌' }}</span>
                                <span>cuDNN</span>
                            </CardTitle>
                            <Badge :variant="systemInfo.cudnn?.available ? 'default' : 'secondary'">
                                {{ systemInfo.cudnn?.available ? '可用' : '不可用' }}
                            </Badge>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div v-if="systemInfo.cudnn?.available" class="space-y-2 text-sm">
                            <div v-if="systemInfo.cudnn.version" class="flex justify-between items-center">
                                <span class="text-muted-foreground font-medium">版本:</span>
                                <span class="font-bold">{{ systemInfo.cudnn.version }}</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span class="text-muted-foreground font-medium">已启用:</span>
                                <Badge :variant="systemInfo.cudnn.enabled ? 'default' : 'secondary'">
                                    {{ systemInfo.cudnn.enabled ? '是' : '否' }}
                                </Badge>
                            </div>
                            <div v-if="systemInfo.cudnn.benchmark !== undefined"
                                class="flex justify-between items-center">
                                <span class="text-muted-foreground font-medium">Benchmark:</span>
                                <Badge :variant="systemInfo.cudnn.benchmark ? 'default' : 'secondary'">
                                    {{ systemInfo.cudnn.benchmark ? '启用' : '禁用' }}
                                </Badge>
                            </div>
                            <div v-if="systemInfo.cudnn.deterministic !== undefined"
                                class="flex justify-between items-center">
                                <span class="text-muted-foreground font-medium">确定性模式:</span>
                                <Badge :variant="systemInfo.cudnn.deterministic ? 'default' : 'secondary'">
                                    {{ systemInfo.cudnn.deterministic ? '启用' : '禁用' }}
                                </Badge>
                            </div>
                        </div>

                        <div v-else class="text-sm text-muted-foreground">
                            <p>{{ systemInfo.cudnn?.error || 'cuDNN未安装或不可用' }}</p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div v-else class="text-center py-8 text-muted-foreground">
                <p>无法加载系统信息</p>
                <Button @click="handleRetry" class="mt-4" size="sm">
                    重试
                </Button>
            </div>
        </CardContent>
    </Card>
</template>
