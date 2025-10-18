<template>
<div :class="isUser ? 'justify-end' : 'justify-start'" class="w-full flex">
<div :class="isUser ? 'bg-blue-600 text-white' : 'bg-gray-100'" class="px-4 py-2 rounded-2xl max-w-[75%] whitespace-pre-wrap">
<slot />
</div>
</div>
</template>


<script setup lang="ts">
const props = defineProps<{ role: 'user' | 'assistant' | 'system' }>()
const isUser = computed(() => props.role === 'user')
</script>