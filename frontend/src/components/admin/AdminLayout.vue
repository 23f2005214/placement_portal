<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <Sidebar 
      :menu-items="menuItems"
      :collapsed="sidebarCollapsed"
      :mobile-show="mobileSidebarShow"
    >
      <template #quick-actions>
        <div class="px-3">
          <button class="btn btn-primary btn-sm w-100 mb-2" @click="generateReport">
            <i class="bi bi-file-earmark-text me-2"></i>
            Generate Report
          </button>
        </div>
      </template>
    </Sidebar>
    
    <!-- Main Content -->
    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- Navbar -->
      <Navbar @toggle-sidebar="toggleMobileSidebar" />
      
      <!-- Page Content -->
      <main class="content-wrapper p-4">
        <router-view />
      </main>
    </div>
    
    <!-- Mobile Sidebar Overlay -->
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
  name: 'AdminLayout',
  
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
          path: '/admin',
          label: 'Dashboard',
          icon: 'bi bi-speedometer2'
        },
        {
          path: '/admin/companies',
          label: 'Companies',
          icon: 'bi bi-building',
          badge: null
        },
        {
          path: '/admin/students',
          label: 'Students',
          icon: 'bi bi-people'
        },
        {
          path: '/admin/drives',
          label: 'Placement Drives',
          icon: 'bi bi-briefcase'
        },
        {
          path: '/admin/reports',
          label: 'Reports',
          icon: 'bi bi-graph-up'
        }
      ]
    }
  },
  
  methods: {
    toggleMobileSidebar() {
      this.mobileSidebarShow = !this.mobileSidebarShow
    },
    
    generateReport() {
      this.$router.push('/admin/reports')
    }
  }
}
</script>

<style scoped>
.admin-layout {
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

.content-wrapper {
  padding-top: 20px;
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