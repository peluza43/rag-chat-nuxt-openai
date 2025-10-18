// plugins/socket.client.ts
import { io, Socket } from 'socket.io-client'


export default defineNuxtPlugin((nuxtApp) => {
const config = useRuntimeConfig()
const socket: Socket = io(config.public.backendUrl, { transports: ['websocket'] })
return { provide: { socket } }
})