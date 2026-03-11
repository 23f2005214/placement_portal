<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-white border-bottom sticky-top">
    <div class="container-fluid px-4">
      <!-- Sidebar Toggle -->
      <button 
        class="btn btn-link text-dark p-0 me-3 d-lg-none"
        @click="$emit('toggle-sidebar')"
      >
        <i class="bi bi-list fs-4"></i>
      </button>
      
      <!-- Brand (mobile) -->
      <a class="navbar-brand d-lg-none fw-bold text-primary" href="#">
        <i class="bi bi-briefcase-fill me-2"></i>
        PPA
      </a>
      
      <!-- Search Bar -->
      <div class="d-none d-md-flex flex-grow-1 me-3" style="max-width: 400px;">
        <div class="input-group">
          <span class="input-group-text bg-light border-end-0">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input 
            type="text" 
            class="form-control bg-light border-start-0"
            placeholder="Search..."
            v-model="searchQuery"
            @keyup.enter="handleSearch"
          >
        </div>
      </div>
      
      <!-- Right Side -->
      <div class="d-flex align-items-center ms-auto">
        <!-- Notifications -->
        <div class="dropdown me-3">
          <button 
            type="button"
            class="btn btn-link text-dark position-relative p-1 dropdown-toggle"
            @click="showNotifications = !showNotifications"
            :aria-expanded="showNotifications"
            aria-haspopup="true"
          >
            <i class="bi bi-bell fs-5"></i>
            <span 
              class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
              v-if="notifications.length > 0"
            >
              {{ notifications.length }}
            </span>
          </button>
          <div 
            class="dropdown-menu dropdown-menu-end shadow"
            style="min-width: 300px;"
            :class="{ show: showNotifications }"
          >
            <h6 class="dropdown-header">Notifications</h6>
            <div v-if="notifications.length === 0" class="px-3 py-2 text-muted small">
              No new notifications
            </div>
            <div v-for="notif in notifications" :key="notif.id">
              <a class="dropdown-item py-2" href="#">
                <div class="d-flex">
                  <div class="me-3">
                    <i :class="getNotificationIcon(notif.type)" class="fs-5"></i>
                  </div>
                  <div>
                    <p class="mb-0 small">{{ notif.message }}</p>
                    <small class="text-muted">{{ notif.time }}</small>
                  </div>
                </div>
              </a>
            </div>
            <div class="dropdown-divider" v-if="notifications.length > 0"></div>
            <a class="dropdown-item text-center small" href="#">View all notifications</a>
          </div>
        </div>
        
        <!-- User Menu -->
        <div class="dropdown">
          <button 
            type="button"
            class="btn btn-link text-dark d-flex align-items-center p-0 dropdown-toggle"
            @click="showUserMenu = !showUserMenu"
            :aria-expanded="showUserMenu"
            aria-haspopup="true"
          >
            <div class="avatar bg-primary text-white rounded-circle me-2">
              {{ userInitials }}
            </div>
            <div class="d-none d-md-block text-start me-2">
              <p class="mb-0 small fw-semibold">{{ userName }}</p>
              <p class="mb-0 small text-muted text-capitalize">{{ userRole }}</p>
            </div>
            <i class="bi bi-chevron-down small"></i>
          </button>
          <div 
            class="dropdown-menu dropdown-menu-end shadow"
            :class="{ show: showUserMenu }"
          >
            <router-link class="dropdown-item" :to="profileRoute" @click="showUserMenu = false">
              <i class="bi bi-person me-2"></i> Profile
            </router-link>
            <a class="dropdown-item" href="#" @click.prevent="showSettings">
              <i class="bi bi-gear me-2"></i> Settings
            </a>
            <hr class="dropdown-divider">
            <a class="dropdown-item text-danger" href="#" @click.prevent="handleLogout">
              <i class="bi bi-box-arrow-right me-2"></i> Logout
            </a>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavbarComponent',
  
  data() {
    return {
      searchQuery: '',
      notifications: [],
      showUserMenu: false,
      showNotifications: false,
      documentClickHandler: null
    }
  },
  
  computed: {
    userName() {
      return this.$store.getters.userName
    },
    
    userRole() {
      return this.$store.getters.userRole
    },
    
    userInitials() {
      const name = this.userName || 'U'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    },
    
    profileRoute() {
      const role = this.userRole
      if (role === 'student') return '/student/profile'
      if (role === 'company') return '/company/profile'
      return '#'
    }
  },
  
  mounted() {
    // Keep a stable function reference for add/removeEventListener
    this.documentClickHandler = (event) => this.closeDropdowns(event)
    document.addEventListener('click', this.documentClickHandler)
  },
  
  beforeUnmount() {
    if (this.documentClickHandler) {
      document.removeEventListener('click', this.documentClickHandler)
    }
  },

  methods: {
    handleSearch() {
      if (this.searchQuery.trim()) {
        this.$emit('search', this.searchQuery)
      }
    },
    
    showSettings() {
      // Implement settings modal
      console.log('Show settings')
    },
    
    async handleLogout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    },
    
    getNotificationIcon(type) {
      const icons = {
        success: 'bi bi-check-circle text-success',
        warning: 'bi bi-exclamation-triangle text-warning',
        error: 'bi bi-x-circle text-danger',
        info: 'bi bi-info-circle text-info'
      }
      return icons[type] || icons.info
    },
    
    closeDropdowns(event) {
      if (!this.$el.contains(event.target)) {
        this.showUserMenu = false
        this.showNotifications = false
      }
    }
  }
}
</script>

<style scoped>
.avatar {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.navbar {
  z-index: 1030;
}

.dropdown {
  position: relative;
}

.dropdown-menu {
  display: none;
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 1100 !important;
  min-width: 200px;
  background-color: #fff;
  border: 1px solid rgba(0, 0, 0, 0.15);
  border-radius: 0.375rem;
}

.dropdown-menu.show {
  display: block;
}

.dropdown-toggle::after {
  display: none;
}

.dropdown-item {
  cursor: pointer;
  display: block;
  width: 100%;
  padding: 0.5rem 1rem;
  clear: both;
  color: #212529;
  text-align: inherit;
  white-space: nowrap;
  background-color: transparent;
  border: 0;
  text-decoration: none;
}

.dropdown-item:hover {
  color: #1e40af;
  background-color: #f8f9fa;
}

.dropdown-item.text-danger:hover {
  color: #dc2626 !important;
  background-color: #fee2e2;
}

.dropdown-divider {
  height: 0;
  margin: 0.5rem 0;
  overflow: hidden;
  border-top: 1px solid #e5e7eb;
}

.dropdown-header {
  display: block;
  padding: 0.5rem 1rem;
  margin-bottom: 0;
  font-size: 0.875rem;
  color: #6b7280;
  white-space: nowrap;
}
</style>