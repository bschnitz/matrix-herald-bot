<template>
  <div id="container">
    <div v-if="error" class="error">
      There was an error with the widget. See console for details.
    </div>
    <div v-else>
      <p>Hello <span>{{ userId }}</span>!</p>
      <p>
        Currently stuck on screen: <span id="stickyState">{{ isSticky }}</span>
      </p>
      <button @click="toggleSticky">Toggle sticky state</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { WidgetApi, MatrixCapabilities } from "matrix-widget-api"
import { parseFragment, assertParam, handleError } from '@/util.js'

const isSticky = ref(false)
const userId = ref('')
const error = ref(false)
let widgetApi = null

onMounted(async () => {
  try {
    const qs = parseFragment()
    const widgetId = assertParam(qs, 'widgetId')
    userId.value = assertParam(qs, 'userId')

    const targetOrigin = '*'
    widgetApi = new WidgetApi(widgetId, targetOrigin)

    widgetApi.requestCapability(MatrixCapabilities.AlwaysOnScreen)

    widgetApi.on('ready', () => {
      sendStickyState()
    })

    await widgetApi.start()
  } catch (e) {
    handleError(e)
    error.value = true
  }
})

function toggleSticky() {
  isSticky.value = !isSticky.value
  sendStickyState()
}

function sendStickyState() {
  if (!widgetApi) return
  widgetApi
    .setAlwaysOnScreen(isSticky.value)
    .then((r) => {
      console.log('[Widget] Client responded with: ', r)
    })
    .catch((e) => handleError(e))
}
</script>

<style scoped>
button {
  border: none;
  color: #ffffff;
  background-color: #2a9d8f;
  border-radius: 4px;
  padding: 6px 12px;
  cursor: pointer;
}

#error {
  color: red;
}

#stickyState {
  color: #3d5a80;
}
</style>
