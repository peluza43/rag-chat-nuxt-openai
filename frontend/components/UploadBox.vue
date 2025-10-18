<template>
<form @submit.prevent="doUpload" class="flex gap-2 items-center">
<input type="file" accept="application/pdf" ref="fileRef" class="border p-2 rounded" />
<input v-model="collection" placeholder="collection (opcional)" class="border p-2 rounded" />
<button class="bg-emerald-600 text-white px-4 py-2 rounded">Subir PDF</button>
<span v-if="status" class="text-sm text-gray-600">{{ status }}</span>
</form>
</template>


<script setup lang="ts">
const fileRef = ref<HTMLInputElement | null>(null)
const status = ref('')
const { collection: collState } = useChat()
const collection = useState<string>('uploadBoxCollection', () => '')


const config = useRuntimeConfig()


async function doUpload() {
const f = fileRef.value?.files?.[0]
if (!f) { status.value = 'Selecciona un PDF'; return }
const form = new FormData()
form.append('file', f)
if (collection.value) form.append('collection', collection.value)
const res = await fetch(`${config.public.backendUrl}/api/upload`, { method: 'POST', body: form })
const json = await res.json()
collState.value = json.collection
status.value = `Indexado: ${json.doc_id} (chunks: ${json.chunks}) en colección ${json.collection}`
}
</script>