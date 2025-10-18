<template>
<div class="min-h-screen bg-white text-gray-900 p-6 mx-auto max-w-3xl">
<h1 class="text-2xl font-bold mb-4">RAG Chat (PDF) · Nuxt 3 + Socket.IO</h1>


<UploadBox class="mb-4" />


<form @submit.prevent="onAsk" class="flex gap-2 mb-4">
<input v-model="question" placeholder="Escribe tu pregunta sobre el PDF…" class="flex-1 border p-3 rounded" />
<button :disabled="busy" class="bg-blue-600 text-white px-4 py-2 rounded">
{{ busy ? 'Consultando…' : 'Preguntar' }}
</button>
</form>


<div class="space-y-3">
<ChatMessage v-for="(m,i) in messages" :key="i" :role="m.role">{{ m.text }}</ChatMessage>
<ChatMessage v-if="busy || currentAnswer" role="assistant">{{ currentAnswer }}</ChatMessage>
</div>


<div v-if="sources.length" class="mt-6 border-t pt-4">
<h2 class="font-semibold mb-2">Fuentes utilizadas</h2>
<ul class="list-disc pl-6 text-sm text-gray-700">
<li v-for="(s,i) in sources" :key="i">
<span class="font-mono">[{{ (s.score||0).toFixed(2) }}]</span>
<strong>{{ s.metadata?.source }}</strong>
— idx: {{ s.metadata?.index }} — “{{ s.text }}”
</li>
</ul>
</div>
</div>
</template>


<script setup lang="ts">
import UploadBox from '~/components/UploadBox.vue'
import ChatMessage from '~/components/ChatMessage.vue'


const question = ref('')
const { $socket } = useNuxtApp()
const { messages, busy, currentAnswer, sources, collection, addUser, startAnswer, appendAnswer, endAnswer } = useChat()


onMounted(() => {
$socket.on('answer_chunk', (payload: { text: string }) => appendAnswer(payload.text))
$socket.on('answer_done', (payload: { sources: any[], used_context: boolean, error?: string }) => {
endAnswer(payload.sources || [])
})
})


function onAsk() {
if (!question.value.trim()) return
addUser(question.value)
startAnswer()
$socket.emit('ask', { question: question.value, collection: collection.value, top_k: 4, min_score: 0.35 })
question.value = ''
}
</script>


<style>

</style>