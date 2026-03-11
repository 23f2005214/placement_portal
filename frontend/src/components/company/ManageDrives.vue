<template>
  <div class="manage-drives">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Placement Drives</h4>
        <p class="text-muted mb-0">Manage your placement drives and applications</p>
      </div>
      <router-link to="/company/drives/create" class="btn btn-primary" v-if="companyApproved">
        <i class="bi bi-plus-lg me-2"></i>
        Create New Drive
      </router-link>
    </div>
    
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body py-3">
        <div class="row g-3 align-items-center">
          <div class="col-md-4">
            <select class="form-select" v-model="filters.status" @change="fetchDrives">
              <option value="">All Status</option>
              <option value="pending">Pending Approval</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white">
                <i class="bi bi-search"></i>
              </span>
              <input 
                type="text" 
                class="form-control"
                placeholder="Search drives..."
                v-model="filters.search"
                @input="debouncedFetch"
              >
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Drives List -->
    <div class="row g-4">
      <div class="col-12" v-if="loading">
        <div class="text-center py-5">
          <div class="spinner-border text-primary"></div>
        </div>
      </div>
      
      <div class="col-12" v-else-if="drives.length === 0">
        <div class="card">
          <div class="card-body text-center py-5">
            <i class="bi bi-briefcase fs-1 text-muted"></i>
            <h5 class="mt-3">No Drives Found</h5>
            <p class="text-muted">Create your first placement drive to start recruiting!</p>
            <router-link to="/company/drives/create" class="btn btn-primary" v-if="companyApproved">
              Create Drive
            </router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-xl-4" v-else v-for="drive in drives" :key="drive.id">
        <div class="card h-100 drive-card">
          <div class="card-header bg-white d-flex justify-content-between align-items-center">
            <span class="badge" :class="getStatusBadge(drive.status)">
              {{ drive.status }}
            </span>
            <div class="dropdown">
              <button 
                class="btn btn-sm btn-link text-dark"
                data-bs-toggle="dropdown"
              >
                <i class="bi bi-three-dots-vertical"></i>
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <router-link 
                    :to="`/company/drives/${drive.id}/applications`"
                    class="dropdown-item"
                    v-if="drive.status === 'approved'"
                  >
                    <i class="bi bi-people me-2"></i> View Applications
                  </router-link>
                </li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="editDrive(drive)">
                    <i class="bi bi-pencil me-2"></i> Edit
                  </a>
                </li>
                <li v-if="drive.status === 'approved'">
                  <a class="dropdown-item" href="#" @click.prevent="closeDrive(drive)">
                    <i class="bi bi-x-circle me-2"></i> Close Drive
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div class="card-body">
            <h5 class="card-title mb-2">{{ drive.job_title }}</h5>
            <p class="text-muted small mb-3">{{ drive.job_type }} • {{ drive.work_mode }}</p>
            
            <div class="mb-3">
              <div class="d-flex align-items-center text-muted small mb-2">
                <i class="bi bi-geo-alt me-2"></i>
                {{ drive.job_location || 'Location not specified' }}
              </div>
              <div class="d-flex align-items-center text-muted small mb-2">
                <i class="bi bi-currency-rupee me-2"></i>
                {{ drive.salary_display }}
              </div>
              <div class="d-flex align-items-center text-muted small">
                <i class="bi bi-calendar me-2"></i>
                Deadline: {{ formatDate(drive.application_deadline) }}
              </div>
            </div>
            
            <!-- Stats -->
            <div class="row text-center border-top pt-3">
              <div class="col-4">
                <h5 class="mb-0">{{ drive.application_count }}</h5>
                <small class="text-muted">Applied</small>
              </div>
              <div class="col-4">
                <h5 class="mb-0">{{ drive.number_of_positions }}</h5>
                <small class="text-muted">Positions</small>
              </div>
              <div class="col-4">
                <h5 class="mb-0" :class="getDaysLeftClass(drive)">
                  {{ getDaysLeft(drive.application_deadline) }}
                </h5>
                <small class="text-muted">Days Left</small>
              </div>
            </div>
          </div>
          <div class="card-footer bg-white" v-if="drive.status === 'approved'">
            <router-link 
              :to="`/company/drives/${drive.id}/applications`"
              class="btn btn-primary btn-sm w-100"
            >
              <i class="bi bi-people me-2"></i>
              Manage Applications
            </router-link>
          </div>
          <div class="card-footer bg-white" v-else-if="drive.status === 'rejected'">
            <div class="alert alert-danger mb-0 py-2 small">
              <i class="bi bi-exclamation-circle me-1"></i>
              {{ drive.admin_remarks || 'Rejected by admin' }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Pagination -->
    <div class="d-flex justify-content-center mt-4" v-if="pagination.pages > 1">
      <nav>
        <ul class="pagination">
          <li class="page-item" :class="{ disabled: !pagination.has_prev }">
            <a class="page-link" href="#" @click.prevent="goToPage(pagination.page - 1)">
              Previous
            </a>
          </li>
          <li 
            class="page-item" 
            v-for="page in visiblePages" 
            :key="page"
            :class="{ active: page === pagination.page }"
          >
            <a class="page-link" href="#" @click.prevent="goToPage(page)">
              {{ page }}
            </a>
          </li>
          <li class="page-item" :class="{ disabled: !pagination.has_next }">
            <a class="page-link" href="#" @click.prevent="goToPage(pagination.page + 1)">
              Next
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
import { companyAPI } from '../../services/api'

export default {
  name: 'ManageDrives',
  
  data() {
    return {
      loading: true,
      drives: [],
      pagination: {
        page: 1,
        per_page: 9,
        total: 0,
        pages: 1,
        has_next: false,
        has_prev: false
      },
      filters: {
        status: '',
        search: ''
      },
      searchTimeout: null
    }
  },
  
  computed: {
    companyApproved() {
      return this.$store.getters.companyApproved
    },
    
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.pagination.page - 2)
      const end = Math.min(this.pagination.pages, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    }
  },
  
  methods: {
    async fetchDrives() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          status: this.filters.status
        }
        
        const response = await companyAPI.getDrives(params)
        this.drives = response.drives || []
        this.pagination = response.pagination || this.pagination
      } catch (error) {
        console.error('Failed to fetch drives:', error)
      } finally {
        this.loading = false
      }
    },
    
    debouncedFetch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.pagination.page = 1
        this.fetchDrives()
      }, 300)
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.pagination.page = page
        this.fetchDrives()
      }
    },
    
    editDrive(drive) {
      // For now, just show alert
      alert('Edit functionality will redirect to edit page')
    },
    
    async closeDrive(drive) {
      if (!confirm(`Close "${drive.job_title}"? This will stop accepting new applications.`)) return
      
      try {
        await companyAPI.closeDrive(drive.id)
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Drive closed successfully'
        })
        this.fetchDrives()
      } catch (error) {
        console.error('Failed to close drive:', error)
      }
    },
    
    getStatusBadge(status) {
      const badges = {
        pending: 'bg-warning text-dark',
        approved: 'bg-success',
        rejected: 'bg-danger',
        completed: 'bg-secondary'
      }
      return badges[status] || 'bg-secondary'
    },
    
    getDaysLeft(deadline) {
      if (!deadline) return 'N/A'
      const days = Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24))
      return days > 0 ? days : 0
    },
    
    getDaysLeftClass(drive) {
      const days = this.getDaysLeft(drive.application_deadline)
      if (days <= 0) return 'text-danger'
      if (days <= 3) return 'text-warning'
      return 'text-success'
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      })
    }
  },
  
  mounted() {
    this.fetchDrives()
  }
}
</script>

<style scoped>
.drive-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.drive-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}
</style>