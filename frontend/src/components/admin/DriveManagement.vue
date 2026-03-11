<template>
  <div class="drive-management">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Placement Drives</h4>
        <p class="text-muted mb-0">Manage and approve placement drives</p>
      </div>
    </div>
    
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <input 
              type="text" 
              class="form-control"
              placeholder="Search drives..."
              v-model="filters.search"
              @input="debouncedFetch"
            >
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filters.status" @change="fetchDrives">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          <div class="col-md-3">
            <button class="btn btn-outline-secondary" @click="resetFilters">
              <i class="bi bi-x-circle me-1"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Drives List -->
    <div class="row g-4">
      <div class="col-12" v-if="loading">
        <div class="text-center py-5">
          <div class="spinner-border text-primary"></div>
          <p class="text-muted mt-2">Loading drives...</p>
        </div>
      </div>
      
      <div class="col-12" v-else-if="drives.length === 0">
        <div class="card">
          <div class="card-body text-center py-5">
            <i class="bi bi-briefcase fs-1 text-muted"></i>
            <p class="text-muted mt-2 mb-0">No placement drives found</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-6 col-lg-4" v-else v-for="drive in drives" :key="drive.id">
        <div class="card h-100 drive-card">
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
              <span class="badge" :class="getStatusBadge(drive.status)">
                {{ drive.status }}
              </span>
            </div>
            
            <!-- Details -->
            <div class="mb-3">
              <div class="d-flex align-items-center text-muted small mb-2">
                <i class="bi bi-geo-alt me-2"></i>
                {{ drive.job_location || 'Not specified' }}
              </div>
              <div class="d-flex align-items-center text-muted small mb-2">
                <i class="bi bi-briefcase me-2"></i>
                {{ drive.job_type }}
              </div>
              <div class="d-flex align-items-center text-muted small">
                <i class="bi bi-currency-rupee me-2"></i>
                {{ drive.salary_display }}
              </div>
            </div>
            
            <!-- Stats -->
            <div class="d-flex justify-content-between text-center border-top border-bottom py-2 mb-3">
              <div>
                <h6 class="mb-0">{{ drive.application_count }}</h6>
                <small class="text-muted">Applications</small>
              </div>
              <div>
                <h6 class="mb-0">{{ drive.number_of_positions }}</h6>
                <small class="text-muted">Positions</small>
              </div>
              <div>
                <h6 class="mb-0">{{ getDaysLeft(drive.application_deadline) }}</h6>
                <small class="text-muted">Days Left</small>
              </div>
            </div>
            
            <!-- Actions -->
            <div class="d-flex gap-2">
              <button 
                class="btn btn-sm btn-outline-primary flex-grow-1"
                @click="viewDrive(drive)"
              >
                <i class="bi bi-eye me-1"></i> View
              </button>
              <button 
                class="btn btn-sm btn-success"
                v-if="drive.status === 'pending'"
                @click="approveDrive(drive)"
              >
                <i class="bi bi-check-lg"></i>
              </button>
              <button 
                class="btn btn-sm btn-danger"
                v-if="drive.status === 'pending'"
                @click="showRejectModal(drive)"
              >
                <i class="bi bi-x-lg"></i>
              </button>
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
    
    <!-- Drive Details Modal -->
    <div class="modal fade" id="driveModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Drive Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedDrive">
            <div class="row">
              <div class="col-md-8">
                <h5>{{ selectedDrive.job_title }}</h5>
                <p class="text-muted">{{ selectedDrive.company?.company_name }}</p>
                
                <h6 class="mt-4">Job Description</h6>
                <p>{{ selectedDrive.job_description }}</p>
                
                <h6 class="mt-4">Eligibility Criteria</h6>
                <ul>
                  <li v-if="selectedDrive.eligible_branches?.length">
                    <strong>Branches:</strong> {{ selectedDrive.eligible_branches.join(', ') }}
                  </li>
                  <li v-if="selectedDrive.min_cgpa">
                    <strong>Min CGPA:</strong> {{ selectedDrive.min_cgpa }}
                  </li>
                  <li v-if="selectedDrive.max_backlogs !== null">
                    <strong>Max Backlogs:</strong> {{ selectedDrive.max_backlogs }}
                  </li>
                  <li v-if="selectedDrive.eligible_graduation_years">
                    <strong>Graduation Years:</strong> {{ selectedDrive.eligible_graduation_years }}
                  </li>
                </ul>
                
                <h6 class="mt-4" v-if="selectedDrive.selection_process">Selection Process</h6>
                <p v-if="selectedDrive.selection_process">{{ selectedDrive.selection_process }}</p>
              </div>
              <div class="col-md-4">
                <div class="card bg-light">
                  <div class="card-body">
                    <h6 class="text-muted mb-3">Quick Info</h6>
                    <p class="mb-2">
                      <i class="bi bi-currency-rupee me-2"></i>
                      {{ selectedDrive.salary_display }}
                    </p>
                    <p class="mb-2">
                      <i class="bi bi-geo-alt me-2"></i>
                      {{ selectedDrive.job_location || 'Not specified' }}
                    </p>
                    <p class="mb-2">
                      <i class="bi bi-briefcase me-2"></i>
                      {{ selectedDrive.job_type }}
                    </p>
                    <p class="mb-2">
                      <i class="bi bi-calendar me-2"></i>
                      Deadline: {{ formatDate(selectedDrive.application_deadline) }}
                    </p>
                    <p class="mb-0">
                      <i class="bi bi-people me-2"></i>
                      {{ selectedDrive.application_count }} applications
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button 
              type="button" 
              class="btn btn-success"
              v-if="selectedDrive?.status === 'pending'"
              @click="approveDrive(selectedDrive); driveModal.hide()"
            >
              Approve Drive
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Reject Modal -->
    <div class="modal fade" id="rejectDriveModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reject Drive</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to reject this drive?</p>
            <div class="mb-3">
              <label class="form-label">Reason for Rejection</label>
              <textarea 
                class="form-control" 
                rows="3"
                v-model="rejectReason"
                placeholder="Provide a reason..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger"
              @click="confirmReject"
            >
              Reject Drive
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '../../services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'DriveManagement',
  
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
        search: '',
        status: ''
      },
      selectedDrive: null,
      rejectReason: '',
      driveModal: null,
      rejectModal: null,
      searchTimeout: null
    }
  },
  
  computed: {
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
          status: this.filters.status
        }
        
        const response = await adminAPI.getDrives(params)
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
    
    resetFilters() {
      this.filters = { search: '', status: '' }
      this.pagination.page = 1
      this.fetchDrives()
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.pagination.page = page
        this.fetchDrives()
      }
    },
    
    viewDrive(drive) {
      this.selectedDrive = drive
      this.driveModal.show()
    },
    
    async approveDrive(drive) {
      if (!confirm(`Approve "${drive.job_title}"?`)) return
      
      try {
        await adminAPI.approveDrive(drive.id)
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Drive approved successfully'
        })
        this.fetchDrives()
      } catch (error) {
        console.error('Failed to approve drive:', error)
      }
    },
    
    showRejectModal(drive) {
      this.selectedDrive = drive
      this.rejectReason = ''
      this.rejectModal.show()
    },
    
    async confirmReject() {
      try {
        await adminAPI.rejectDrive(this.selectedDrive.id, {
          remarks: this.rejectReason
        })
        this.rejectModal.hide()
        this.fetchDrives()
      } catch (error) {
        console.error('Failed to reject drive:', error)
      }
    },
    
    getStatusBadge(status) {
      const badges = {
        pending: 'bg-warning',
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
    this.driveModal = new Modal(document.getElementById('driveModal'))
    this.rejectModal = new Modal(document.getElementById('rejectDriveModal'))
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