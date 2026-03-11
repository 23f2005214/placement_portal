<template>
  <div class="drives-list">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Browse Placement Drives</h4>
        <p class="text-muted mb-0">Find and apply to opportunities matching your profile</p>
      </div>
    </div>
    
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control"
                placeholder="Search by title, company..."
                v-model="filters.search"
                @input="debouncedFetch"
              >
            </div>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.job_type" @change="fetchDrives">
              <option value="">All Types</option>
              <option value="Full-time">Full-time</option>
              <option value="Internship">Internship</option>
              <option value="Part-time">Part-time</option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.branch" @change="fetchDrives">
              <option value="">All Branches</option>
              <option v-for="branch in branches" :key="branch" :value="branch">
                {{ branch }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <div class="form-check form-switch mt-2">
              <input 
                type="checkbox" 
                class="form-check-input"
                id="showAll"
                v-model="showAllDrives"
                @change="fetchDrives"
              >
              <label class="form-check-label" for="showAll">Show All</label>
            </div>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-x-circle me-1"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Results Info -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <p class="text-muted mb-0">
        Showing {{ drives.length }} drives
        <span v-if="!showAllDrives">(eligible only)</span>
      </p>
      <div class="btn-group btn-group-sm">
        <button 
          class="btn"
          :class="viewMode === 'grid' ? 'btn-primary' : 'btn-outline-primary'"
          @click="viewMode = 'grid'"
        >
          <i class="bi bi-grid"></i>
        </button>
        <button 
          class="btn"
          :class="viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'"
          @click="viewMode = 'list'"
        >
          <i class="bi bi-list"></i>
        </button>
      </div>
    </div>
    
    <!-- Loading -->
    <div class="text-center py-5" v-if="loading">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-2">Loading drives...</p>
    </div>
    
    <!-- No Results -->
    <div class="card" v-else-if="drives.length === 0">
      <div class="card-body text-center py-5">
        <i class="bi bi-briefcase fs-1 text-muted"></i>
        <p class="text-muted mt-2 mb-0">No drives found matching your criteria</p>
      </div>
    </div>
    
    <!-- Grid View -->
    <div class="row g-4" v-else-if="viewMode === 'grid'">
      <div class="col-md-6 col-lg-4" v-for="drive in drives" :key="drive.id">
        <div class="card h-100 drive-card" :class="{ 'border-success': drive.is_eligible && !drive.has_applied }">
          <div class="card-body">
            <!-- Header -->
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex">
                <img 
                  :src="drive.company?.logo_url || 'https://via.placeholder.com/48'"
                  class="rounded me-3"
                  width="48"
                  height="48"
                >
                <div>
                  <h6 class="mb-1">{{ drive.job_title }}</h6>
                  <p class="text-muted small mb-0">{{ drive.company?.company_name }}</p>
                </div>
              </div>
            </div>
            
            <!-- Tags -->
            <div class="d-flex flex-wrap gap-1 mb-3">
              <span class="badge bg-light text-dark">{{ drive.job_type }}</span>
              <span class="badge bg-light text-dark">{{ drive.work_mode }}</span>
              <span class="badge bg-light text-dark" v-if="drive.job_location">
                {{ drive.job_location }}
              </span>
            </div>
            
            <!-- Salary -->
            <p class="text-success fw-medium mb-3">{{ drive.salary_display }}</p>
            
            <!-- Eligibility -->
            <div class="mb-3">
              <div class="d-flex align-items-center text-success small" v-if="drive.is_eligible">
                <i class="bi bi-check-circle me-1"></i>
                You are eligible
              </div>
              <div class="text-danger small" v-else>
                <i class="bi bi-x-circle me-1"></i>
                Not eligible
                <ul class="mb-0 ps-3 mt-1" v-if="drive.eligibility_reasons?.length">
                  <li v-for="(reason, idx) in drive.eligibility_reasons.slice(0, 2)" :key="idx">
                    {{ reason }}
                  </li>
                </ul>
              </div>
            </div>
            
            <!-- Footer -->
            <div class="d-flex justify-content-between align-items-center pt-3 border-top">
              <small class="text-muted">
                <i class="bi bi-clock me-1"></i>
                {{ getDaysLeft(drive.application_deadline) }} days left
              </small>
              <router-link 
                :to="`/student/drives/${drive.id}`"
                class="btn btn-sm"
                :class="drive.has_applied ? 'btn-outline-secondary' : 'btn-primary'"
              >
                {{ drive.has_applied ? 'View Status' : 'View & Apply' }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- List View -->
    <div class="card" v-else>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light">
            <tr>
              <th>Company</th>
              <th>Position</th>
              <th>Type</th>
              <th>Salary</th>
              <th>Deadline</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in drives" :key="drive.id">
              <td>
                <div class="d-flex align-items-center">
                  <img 
                    :src="drive.company?.logo_url || 'https://via.placeholder.com/32'"
                    class="rounded me-2"
                    width="32"
                    height="32"
                  >
                  {{ drive.company?.company_name }}
                </div>
              </td>
              <td>{{ drive.job_title }}</td>
              <td>{{ drive.job_type }}</td>
              <td>{{ drive.salary_display }}</td>
              <td>{{ formatDate(drive.application_deadline) }}</td>
              <td>
                <span class="badge bg-success" v-if="drive.is_eligible && !drive.has_applied">
                  Eligible
                </span>
                <span class="badge bg-info" v-else-if="drive.has_applied">
                  Applied
                </span>
                <span class="badge bg-danger" v-else>
                  Not Eligible
                </span>
              </td>
              <td>
                <router-link 
                  :to="`/student/drives/${drive.id}`"
                  class="btn btn-sm btn-outline-primary"
                >
                  View
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
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
import { studentAPI } from '../../services/api'

export default {
  name: 'DrivesList',
  
  data() {
    return {
      loading: true,
      drives: [],
      pagination: {
        page: 1,
        per_page: 12,
        total: 0,
        pages: 1,
        has_next: false,
        has_prev: false
      },
      filters: {
        search: '',
        job_type: '',
        branch: ''
      },
      showAllDrives: false,
      viewMode: 'grid',
      searchTimeout: null
    }
  },
  
  computed: {
    branches() {
      return this.$store.state.branches
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
          search: this.filters.search,
          job_type: this.filters.job_type,
          branch: this.filters.branch,
          show_all: this.showAllDrives
        }
        
        const response = await studentAPI.getDrives(params)
        this.drives = response.data.drives || []
        this.pagination = response.data.pagination || this.pagination
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
    
    resetFilters() {
      this.filters = {
        search: '',
        job_type: '',
        branch: ''
      }
      this.showAllDrives = false
      this.pagination.page = 1
      this.fetchDrives()
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.pagination.page = page
        this.fetchDrives()
      }
    },
    
    getDaysLeft(deadline) {
      if (!deadline) return 0
      const days = Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24))
      return days > 0 ? days : 0
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short'
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