<template>
  <div class="student-layout">
    <Sidebar 
      :menu-items="menuItems"
      :collapsed="sidebarCollapsed"
      :mobile-show="mobileSidebarShow"
    />
    
    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <Navbar @toggle-sidebar="toggleMobileSidebar" />
      
      <main class="content-wrapper p-4">
        <router-view />
      </main>
    </div>
    
    <div 
      class="sidebar-overlay d-lg-none"
      :class="{ show: mobileSidebarShow }"
      @click="mobileSidebarShow = false"
    ></div>
  </div>
</template>

<script>
import Sidebar from '../common/Sidebar.vue'
import Navbar from '../common/Navbar.vue'

export default {
  name: 'StudentLayout',
  
  components: {
    Sidebar,
    Navbar
  },
  
  data() {
    return {
      sidebarCollapsed: false,
      mobileSidebarShow: false,
      menuItems: [
        {
          path: '/student',
          label: 'Dashboard',
          icon: 'bi bi-speedometer2'
        },
        {
          path: '/student/drives',
          label: 'Browse Drives',
          icon: 'bi bi-briefcase'
        },
        {
          path: '/student/applications',
          label: 'My Applications',
          icon: 'bi bi-file-text'
        },
        {
          path: '/student/history',
          label: 'Placement History',
          icon: 'bi bi-clock-history'
        },
        {
          path: '/student/profile',
          label: 'Profile',
          icon: 'bi bi-person'
        }
      ]
    }
  },
  
  methods: {
    toggleMobileSidebar() {
      this.mobileSidebarShow = !this.mobileSidebarShow
    }
  }
}
</script>

<style scoped>
.student-layout {
  min-height: 100vh;
  background-color: #f5f7fb;
}

.main-content {
  margin-left: 260px;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 70px;
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1035;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
}

.sidebar-overlay.show {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 991.98px) {
  .main-content {
    margin-left: 0;
  }
}
</style>