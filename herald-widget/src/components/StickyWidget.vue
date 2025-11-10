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
import { parseFragment, assertParam, handleError } from '@/util.js'
import { WidgetApi, MatrixCapabilities, WidgetApiToWidgetAction } from "matrix-widget-api"

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

    // Berechtigungen anfragen
    // messages im Raum
    widgetApi.requestCapabilityToReceiveEvent("m.room.message")  
    // Custom event mit state_key ""
    widgetApi.requestCapabilityToReceiveState("org.herald.tree_structure", "")
      
    // Event-Listener registrieren  
    widgetApi.on(`action:${WidgetApiToWidgetAction.SendEvent}`, (ev) => {  
      ev.preventDefault()  
      const roomEvent = ev.detail.data  
        
      // Prüfen ob es das gewünschte Event ist  
      if (roomEvent.type === "org.herald.tree_structure") {  
        console.log('Herald Tree Update empfangen:', roomEvent)  
      }  
      else {
        console.log('Sonstige Nachricht empfangen:', roomEvent)  
      }
        
      widgetApi.transport.reply(ev.detail, {})  
    }) 
  
    await widgetApi.start()  
  } catch (e) {  
    handleError(e)  
    error.value = true  
  }  
})
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
