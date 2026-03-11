<template>
  <div id="app">
    <router-view />
    
    <!-- Toast Notifications -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 9999;">
      <div 
        v-for="toast in $store.state.toasts" 
        :key="toast.id"
        class="toast show"
        :class="'text-bg-' + (toast.type || 'info')"
      >
        <div class="toast-body d-flex justify-content-between align-items-center">
          {{ toast.message }}
          <button type="button" class="btn-close btn-close-white ms-2" @click="$store.commit('REMOVE_TOAST', toast.id)"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f7fb;
  margin: 0;
  padding: 0;
}

#app {
  min-height: 100vh;
}
</style>