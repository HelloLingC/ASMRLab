<script setup>
// No props needed for this static component
</script>

<template>
    <div class="glass rounded-2xl p-8 shadow-xl border border-white/20">
        <h2 class="text-3xl font-bold text-gray-800 mb-6 flex items-center gap-3">
            <span>📚</span>
            <span>使用说明</span>
        </h2>
        <div class="grid md:grid-cols-2 gap-6">
            <div class="p-4 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100">
                <h3 class="font-bold text-indigo-900 mb-2 flex items-center gap-2">
                    <span>🎯</span>
                    <span>模型选择</span>
                </h3>
                <p class="text-gray-700 text-sm leading-relaxed">
                    根据您的需求选择合适的模型。Tiny 模型最小最快，但精度较低；Large 模型精度最高，但需要更多存储空间和处理时间。
                </p>
            </div>
            <div class="p-4 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl border border-blue-100">
                <h3 class="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span>🚀</span>
                    <span>首次使用</span>
                </h3>
                <p class="text-gray-700 text-sm leading-relaxed">
                    使用转录功能前，请先下载所需的模型。下载完成后，模型会自动加载到内存中。
                </p>
            </div>
            <div class="p-4 bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl border border-green-100">
                <h3 class="font-bold text-green-900 mb-2 flex items-center gap-2">
                    <span>💾</span>
                    <span>存储空间</span>
                </h3>
                <p class="text-gray-700 text-sm leading-relaxed">
                    确保有足够的磁盘空间存储模型文件。模型文件保存在服务器的 models 目录中。
                </p>
            </div>
            <div class="p-4 bg-gradient-to-br from-orange-50 to-amber-50 rounded-xl border border-orange-100">
                <h3 class="font-bold text-orange-900 mb-2 flex items-center gap-2">
                    <span>⚡</span>
                    <span>性能考虑</span>
                </h3>
                <p class="text-gray-700 text-sm leading-relaxed">
                    较大的模型需要更多 RAM 和处理时间，但提供更好的转录精度。
                </p>
            </div>
        </div>
    </div>
</template>
