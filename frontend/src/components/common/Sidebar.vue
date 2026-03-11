<template>
  <aside 
    class="sidebar bg-white border-end"
    :class="{ 'collapsed': collapsed, 'show': mobileShow }"
  >
    <!-- Brand -->
    <div class="sidebar-brand px-4 py-3 border-bottom">
      <router-link to="/" class="text-decoration-none d-flex align-items-center">
        <i class="bi bi-briefcase-fill text-primary fs-4 me-2"></i>
        <span class="brand-text fw-bold text-dark" v-if="!collapsed">
          Placement Portal
        </span>
      </router-link>
    </div>
    
    <!-- Navigation -->
    <nav class="sidebar-nav p-3">
      <ul class="nav flex-column">
        <li class="nav-item" v-for="item in menuItems" :key="item.path">
          <!-- Menu Item -->
          <router-link 
            v-if="!item.children"
            :to="item.path"
            class="nav-link d-flex align-items-center"
            :class="{ 'active': isActive(item.path) }"
          >
            <i :class="item.icon" class="me-3 fs-5"></i>
            <span v-if="!collapsed">{{ item.label }}</span>
            <span 
              v-if="item.badge && !collapsed" 
              class="badge ms-auto"
              :class="item.badgeClass || 'bg-primary'"
            >
              {{ item.badge }}
            </span>
          </router-link>
          
          <!-- Submenu -->
          <div v-else>
            <a 
              href="#"
              class="nav-link d-flex align-items-center"
              :class="{ 'active': hasActiveChild(item) }"
              @click.prevent="toggleSubmenu(item.label)"
            >
              <i :class="item.icon" class="me-3 fs-5"></i>
              <span v-if="!collapsed">{{ item.label }}</span>
              <i 
                v-if="!collapsed"
                class="bi ms-auto"
                :class="openSubmenus.includes(item.label) ? 'bi-chevron-up' : 'bi-chevron-down'"
              ></i>
            </a>
            <ul 
              class="nav flex-column submenu"
              v-show="openSubmenus.includes(item.label) && !collapsed"
            >
              <li class="nav-item" v-for="child in item.children" :key="child.path">
                <router-link 
                  :to="child.path"
                  class="nav-link ps-5"
                  :class="{ 'active': isActive(child.path) }"
                >
                  {{ child.label }}
                </router-link>
              </li>
            </ul>
          </div>
        </li>
      </ul>
      
      <!-- Divider -->
      <hr class="my-3">
      
      <!-- Quick Actions -->
      <div v-if="!collapsed">
        <h6 class="text-uppercase text-muted small mb-3 px-3">Quick Actions</h6>
        <slot name="quick-actions"></slot>
      </div>
    </nav>
    
    <!-- User Info (Bottom) -->
    <div class="sidebar-footer mt-auto border-top p-3" v-if="!collapsed">
      <div class="d-flex align-items-center">
        <div class="avatar bg-primary text-white rounded-circle me-3">
          {{ userInitials }}
        </div>
        <div class="flex-grow-1">
          <p class="mb-0 small fw-semibold text-truncate">{{ userName }}</p>
          <p class="mb-0 small text-muted text-capitalize">{{ userRole }}</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script>
export default {
  name: 'SidebarComponent',
  
  props: {
    menuItems: {
      type: Array,
      required: true
    },
    collapsed: {
      type: Boolean,
      default: false
    },
    mobileShow: {
      type: Boolean,
      default: false
    }
  },
  
  data() {
    return {
      openSubmenus: []
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
    }
  },
  
  methods: {
    isActive(path) {
      return this.$route.path === path
    },
    
    hasActiveChild(item) {
      if (!item.children) return false
      return item.children.some(child => this.$route.path === child.path)
    },
    
    toggleSubmenu(label) {
      const index = this.openSubmenus.indexOf(label)
      if (index > -1) {
        this.openSubmenus.splice(index, 1)
      } else {
        this.openSubmenus.push(label)
      }
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  z-index: 1040;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar.collapsed .brand-text,
.sidebar.collapsed .sidebar-footer {
  display: none;
}

.nav-link {
  color: #64748b;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #4361ee;
  background-color: rgba(67, 97, 238, 0.08);
}

.nav-link.active {
  color: #4361ee;
  background-color: rgba(67, 97, 238, 0.12);
  font-weight: 500;
}

.submenu .nav-link {
  font-size: 0.9rem;
  padding: 0.5rem 1rem;
}

.avatar {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

/* Mobile styles */
@media (max-width: 991.98px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.show {
    transform: translateX(0);
  }
}
</style>