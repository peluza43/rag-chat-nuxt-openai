// nuxt.config.ts
export default defineNuxtConfig({
devtools: { enabled: true },
runtimeConfig: {
public: {
backendUrl: process.env.NUXT_BACKEND_URL || 'http://localhost:8000',
}
}
})