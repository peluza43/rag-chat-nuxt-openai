// composables/useChat.ts
export type Msg = { role: 'user' | 'assistant' | 'system'; text: string }


export function useChat() {
const messages = useState<Msg[]>("messages", () => [])
const busy = useState<boolean>("busy", () => false)
const currentAnswer = useState<string>("currentAnswer", () => "")
const sources = useState<any[]>("sources", () => [])
const collection = useState<string>("collection", () => 'docs')


function addUser(text: string) {
messages.value.push({ role: 'user', text })
}


function startAnswer() {
busy.value = true
currentAnswer.value = ''
}


function appendAnswer(chunk: string) {
currentAnswer.value += chunk
}


function endAnswer(finalSources: any[]) {
busy.value = false
messages.value.push({ role: 'assistant', text: currentAnswer.value || 'No poseo información sobre ese tema en el documento cargado.' })
sources.value = finalSources
currentAnswer.value = ''
}


return { messages, busy, currentAnswer, sources, collection, addUser, startAnswer, appendAnswer, endAnswer }
}