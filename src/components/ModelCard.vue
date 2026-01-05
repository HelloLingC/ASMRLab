<script setup>
import { defineProps, defineEmits } from 'vue'
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from './ui'

const props = defineProps({
    model: {
        type: Object,
        required: true
    },
    modelSize: {
        type: String,
        required: true
    },
    status: {
        type: Object,
        default: null
    }
})

const emit = defineEmits(['download', 'delete'])

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

const getStatusText = (status) => {
    switch (status) {
        case 'loaded':
            return '已加载'
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

const getStatusColor = (status) => {
    switch (status) {
        case 'loaded':
            return 'bg-green-50 text-green-900 border-green-300'
        case 'downloading':
            return 'bg-blue-50 text-blue-900 border-blue-300'
        case 'not_downloaded':
            return 'bg-muted text-muted-foreground border-border'
        case 'error':
            return 'bg-destructive/10 text-destructive border-destructive/30'
        default:
            return 'bg-muted text-muted-foreground border-border'
    }
}

const getStatusBadgeVariant = (status) => {
    switch (status) {
        case 'loaded':
            return 'default'
        case 'downloading':
            return 'secondary'
        case 'error':
            return 'destructive'
        default:
            return 'outline'
    }
}

const handleDownload = () => {
    emit('download', props.modelSize)
}

const handleDelete = () => {
    emit('delete', props.modelSize)
}
</script>

<template>
    <Card class="p-6 hover:shadow-lg transition-shadow">
        <!-- Card Header -->
        <CardHeader class="pb-3">
            <div class="flex items-center justify-between">
                <CardTitle class="text-xl">{{ model.name }} {{ model.size_mb }} MB</CardTitle>
                <span class="text-2xl">{{ getStatusIcon(status?.status) }}</span>
            </div>
        </CardHeader>

        <!-- Model Info -->
        <CardContent class="space-y-3">
            <div class="flex justify-between items-center p-3 rounded-lg border-2"
                :class="getStatusColor(status?.status)">
                <span class="text-sm font-medium">状态:</span>
                <Badge :variant="getStatusBadgeVariant(status?.status)">
                    {{ getStatusText(status?.status) }}
                </Badge>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-2">
                <Button v-if="status?.status === 'not_downloaded'" @click="handleDownload" class="flex-1">
                    下载模型
                </Button>
                <Button v-else-if="status?.status === 'downloading'" disabled class="flex-1">
                    下载中...
                </Button>
                <div v-else-if="status?.status === 'loaded'" class="flex gap-2 flex-1">
                    <Button variant="secondary" class="flex-1" disabled>
                        ✓ 已就绪
                    </Button>
                    <Button @click="handleDelete" variant="destructive" size="icon" title="删除模型">
                        🗑️
                    </Button>
                </div>
                <Button v-else-if="status?.status === 'error'" @click="handleDownload" variant="destructive" class="flex-1">
                    重试下载
                </Button>
            </div>
        </CardContent>
    </Card>
</template>
