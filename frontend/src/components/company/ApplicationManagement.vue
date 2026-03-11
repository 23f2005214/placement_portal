<template>
  <div class="application-management">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb mb-1">
            <li class="breadcrumb-item">
              <router-link to="/company/drives">Drives</router-link>
            </li>
            <li class="breadcrumb-item active">Applications</li>
          </ol>
        </nav>
        <h4 class="mb-0">{{ drive?.job_title || 'Loading...' }}</h4>
      </div>
      <router-link to="/company/drives" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-2"></i>
        Back to Drives
      </router-link>
    </div>
    
    <!-- Drive Summary Card -->
    <div class="card mb-4" v-if="drive">
      <div class="card-body">
        <div class="row">
          <div class="col-md-8">
            <div class="d-flex flex-wrap gap-4">
              <div>
                <small class="text-muted d-block">Location</small>
                <span>{{ drive.job_location || 'Not specified' }}</span>
              </div>
              <div>
                <small class="text-muted d-block">Package</small>
                <span>{{ drive.salary_display }}</span>
              </div>
              <div>
                <small class="text-muted d-block">Deadline</small>
                <span>{{ formatDate(drive.application_deadline) }}</span>
              </div>
              <div>
                <small class="text-muted d-block">Positions</small>
                <span>{{ drive.number_of_positions }}</span>
              </div>
            </div>
          </div>
          <div class="col-md-4 text-md-end mt-3 mt-md-0">
            <div class="d-flex justify-content-md-end gap-3">
              <div class="text-center">
                <h4 class="mb-0 text-primary">{{ applicationBreakdown.total }}</h4>
                <small class="text-muted">Total</small>
              </div>
              <div class="text-center">
                <h4 class="mb-0 text-warning">{{ applicationBreakdown.shortlisted }}</h4>
                <small class="text-muted">Shortlisted</small>
              </div>
              <div class="text-center">
                <h4 class="mb-0 text-success">{{ applicationBreakdown.selected }}</h4>
                <small class="text-muted">Selected</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body py-3">
        <div class="row g-3 align-items-center">
          <div class="col-md-3">
            <select class="form-select" v-model="filters.status" @change="fetchApplications">
              <option value="">All Status</option>
              <option value="applied">Applied</option>
              <option value="under_review">Under Review</option>
              <option value="shortlisted">Shortlisted</option>
              <option value="interview_scheduled">Interview Scheduled</option>
              <option value="selected">Selected</option>
              <option value="rejected">Rejected</option>
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
                placeholder="Search by name or email..."
                v-model="filters.search"
                @input="debouncedFetch"
              >
            </div>
          </div>
          <div class="col-md-5 text-md-end">
            <button class="btn btn-outline-primary me-2" @click="selectAllVisible">
              <i class="bi bi-check2-square me-1"></i> Select All
            </button>
            <div class="btn-group" v-if="selectedApplications.length > 0">
              <button 
                class="btn btn-success"
                @click="bulkUpdateStatus('shortlisted')"
              >
                Shortlist ({{ selectedApplications.length }})
              </button>
              <button 
                class="btn btn-danger"
                @click="bulkUpdateStatus('rejected')"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Applications Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th style="width: 40px;">
                  <input 
                    type="checkbox"
                    class="form-check-input"
                    @change="toggleSelectAll"
                    :checked="allSelected"
                  >
                </th>
                <th>Student</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Year</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="text-center py-5">
                  <div class="spinner-border text-primary"></div>
                </td>
              </tr>
              <tr v-else-if="applications.length === 0">
                <td colspan="8" class="text-center py-5">
                  <i class="bi bi-inbox fs-1 text-muted"></i>
                  <p class="text-muted mt-2 mb-0">No applications found</p>
                </td>
              </tr>
              <tr v-else v-for="app in applications" :key="app.id">
                <td>
                  <input 
                    type="checkbox"
                    class="form-check-input"
                    :value="app.id"
                    v-model="selectedApplications"
                  >
                </td>
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-primary text-white rounded-circle me-2">
                      {{ getInitials(app.student?.full_name) }}
                    </div>
                    <div>
                      <p class="mb-0 fw-medium">{{ app.student?.full_name }}</p>
                      <small class="text-muted">{{ app.student?.email }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ app.student?.branch }}</td>
                <td>
                  <span class="badge" :class="getCgpaBadge(app.student?.cgpa)">
                    {{ app.student?.cgpa?.toFixed(2) }}
                  </span>
                </td>
                <td>{{ app.student?.graduation_year }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>
                  <span class="badge" :class="getStatusBadge(app.status)">
                    {{ formatStatus(app.status) }}
                  </span>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      class="btn btn-outline-primary"
                      @click="viewApplication(app)"
                      title="View Details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button 
                      class="btn btn-outline-success"
                      @click="updateStatus(app, 'shortlisted')"
                      title="Shortlist"
                      v-if="app.status === 'applied' || app.status === 'under_review'"
                    >
                      <i class="bi bi-check-lg"></i>
                    </button>
                    <button 
                      class="btn btn-outline-info"
                      @click="showScheduleModal(app)"
                      title="Schedule Interview"
                      v-if="app.status === 'shortlisted'"
                    >
                      <i class="bi bi-calendar"></i>
                    </button>
                    <button 
                      class="btn btn-outline-success"
                      @click="updateStatus(app, 'selected')"
                      title="Select"
                      v-if="app.status === 'shortlisted' || app.status === 'interviewed'"
                    >
                      <i class="bi bi-trophy"></i>
                    </button>
                    <button 
                      class="btn btn-outline-danger"
                      @click="updateStatus(app, 'rejected')"
                      title="Reject"
                      v-if="!['selected', 'rejected', 'withdrawn'].includes(app.status)"
                    >
                      <i class="bi bi-x-lg"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Pagination -->
      <div class="card-footer bg-white" v-if="pagination.pages > 1">
        <nav class="d-flex justify-content-between align-items-center">
          <span class="text-muted small">
            Showing {{ (pagination.page - 1) * pagination.per_page + 1 }} 
            to {{ Math.min(pagination.page * pagination.per_page, pagination.total) }}
            of {{ pagination.total }} applications
          </span>
          <ul class="pagination pagination-sm mb-0">
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
    
    <!-- Application Details Modal -->
    <div class="modal fade" id="applicationModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Application Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedApplication">
            <div class="row">
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Student Information</h6>
                <table class="table table-sm">
                  <tr>
                    <td class="text-muted">Name</td>
                    <td class="fw-medium">{{ selectedApplication.student?.full_name }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Email</td>
                    <td>{{ selectedApplication.student?.email }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Phone</td>
                    <td>{{ selectedApplication.student?.phone || '-' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Roll Number</td>
                    <td>{{ selectedApplication.student?.roll_number || '-' }}</td>
                  </tr>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Academic Details</h6>
                <table class="table table-sm">
                  <tr>
                    <td class="text-muted">Branch</td>
                    <td>{{ selectedApplication.student?.branch }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">CGPA</td>
                    <td>{{ selectedApplication.student?.cgpa?.toFixed(2) }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Graduation Year</td>
                    <td>{{ selectedApplication.student?.graduation_year }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Resume</td>
                    <td>
                      <a 
                        :href="selectedApplication.student?.resume_url" 
                        target="_blank"
                        v-if="selectedApplication.student?.resume_url"
                        class="btn btn-sm btn-outline-primary"
                      >
                        <i class="bi bi-download me-1"></i> Download
                      </a>
                      <span v-else class="text-muted">Not uploaded</span>
                    </td>
                  </tr>
                </table>
              </div>
            </div>
            
            <div class="mt-3" v-if="selectedApplication.cover_letter">
              <h6 class="text-muted mb-2">Cover Letter</h6>
              <p class="mb-0">{{ selectedApplication.cover_letter }}</p>
            </div>
            
            <div class="mt-3">
              <h6 class="text-muted mb-2">Application Status</h6>
              <div class="d-flex align-items-center">
                <span class="badge me-3" :class="getStatusBadge(selectedApplication.status)">
                  {{ formatStatus(selectedApplication.status) }}
                </span>
                <span class="text-muted small">
                  Applied on {{ formatDate(selectedApplication.applied_at) }}
                </span>
              </div>
            </div>
            
            <div class="mt-3" v-if="selectedApplication.interview_date">
              <h6 class="text-muted mb-2">Interview Details</h6>
              <p class="mb-1">
                <i class="bi bi-calendar me-2"></i>
                {{ formatDateTime(selectedApplication.interview_date) }}
              </p>
              <p class="mb-1">
                <i class="bi bi-camera-video me-2"></i>
                {{ selectedApplication.interview_mode }}
              </p>
              <p class="mb-0" v-if="selectedApplication.interview_link">
                <a :href="selectedApplication.interview_link" target="_blank">
                  Join Interview
                </a>
              </p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button 
              type="button" 
              class="btn btn-success"
              @click="updateStatus(selectedApplication, 'shortlisted')"
              v-if="selectedApplication?.status === 'applied'"
            >
              Shortlist
            </button>
            <button 
              type="button" 
              class="btn btn-success"
              @click="updateStatus(selectedApplication, 'selected')"
              v-if="['shortlisted', 'interviewed'].includes(selectedApplication?.status)"
            >
              Select
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Schedule Interview Modal -->
    <div class="modal fade" id="scheduleModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Schedule Interview</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Interview Date & Time *</label>
              <input 
                type="datetime-local" 
                class="form-control"
                v-model="interviewForm.interview_date"
                :min="minDateTime"
                required
              >
            </div>
            <div class="mb-3">
              <label class="form-label">Interview Mode *</label>
              <select class="form-select" v-model="interviewForm.interview_mode" required>
                <option value="online">Online</option>
                <option value="offline">Offline</option>
                <option value="telephonic">Telephonic</option>
              </select>
            </div>
            <div class="mb-3" v-if="interviewForm.interview_mode === 'online'">
              <label class="form-label">Meeting Link</label>
              <input 
                type="url" 
                class="form-control"
                v-model="interviewForm.interview_link"
                placeholder="https://meet.google.com/..."
              >
            </div>
            <div class="mb-3" v-if="interviewForm.interview_mode === 'offline'">
              <label class="form-label">Venue</label>
              <input 
                type="text" 
                class="form-control"
                v-model="interviewForm.interview_venue"
                placeholder="e.g., Room 101, Main Building"
              >
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="scheduleInterview"
            >
              Schedule Interview
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { companyAPI } from '../../services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'ApplicationManagement',
  
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  
  data() {
    return {
      loading: true,
      drive: null,
      applications: [],
      applicationBreakdown: {
        total: 0,
        applied: 0,
        shortlisted: 0,
        selected: 0,
        rejected: 0
      },
      pagination: {
        page: 1,
        per_page: 10,
        total: 0,
        pages: 1,
        has_next: false,
        has_prev: false
      },
      filters: {
        status: '',
        search: ''
      },
      selectedApplications: [],
      selectedApplication: null,
      interviewForm: {
        interview_date: '',
        interview_mode: 'online',
        interview_link: '',
        interview_venue: ''
      },
      applicationModal: null,
      scheduleModal: null,
      searchTimeout: null
    }
  },
  
  computed: {
    allSelected() {
      return this.applications.length > 0 && 
             this.selectedApplications.length === this.applications.length
    },
    
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.pagination.page - 2)
      const end = Math.min(this.pagination.pages, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    },
    
    minDateTime() {
      const now = new Date()
      now.setHours(now.getHours() + 1)
      return now.toISOString().slice(0, 16)
    }
  },
  
  methods: {
    async fetchDrive() {
      try {
        const response = await companyAPI.getDrive(this.id)
        this.drive = response.data.drive
        this.applicationBreakdown = response.data.application_breakdown || this.applicationBreakdown
      } catch (error) {
        console.error('Failed to fetch drive:', error)
      }
    },
    
    async fetchApplications() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          status: this.filters.status,
          search: this.filters.search
        }
        
        const response = await companyAPI.getDriveApplications(this.id, params)
        this.applications = response.data.applications || []
        this.pagination = response.data.pagination || this.pagination
        this.selectedApplications = []
      } catch (error) {
        console.error('Failed to fetch applications:', error)
      } finally {
        this.loading = false
      }
    },
    
    debouncedFetch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.pagination.page = 1
        this.fetchApplications()
      }, 300)
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.pagination.page = page
        this.fetchApplications()
      }
    },
    
    toggleSelectAll(e) {
      if (e.target.checked) {
        this.selectedApplications = this.applications.map(a => a.id)
      } else {
        this.selectedApplications = []
      }
    },
    
    selectAllVisible() {
      this.selectedApplications = this.applications.map(a => a.id)
    },
    
    viewApplication(app) {
      this.selectedApplication = app
      this.applicationModal.show()
    },
    
    showScheduleModal(app) {
      this.selectedApplication = app
      this.interviewForm = {
        interview_date: '',
        interview_mode: 'online',
        interview_link: '',
        interview_venue: ''
      }
      this.scheduleModal.show()
    },
    
    async updateStatus(app, status) {
      try {
        await companyAPI.updateApplicationStatus(app.id, { status })
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: `Application ${status}`
        })
        this.fetchApplications()
        this.fetchDrive()
        
        if (this.applicationModal) {
          this.applicationModal.hide()
        }
      } catch (error) {
        console.error('Failed to update status:', error)
      }
    },
    
    async bulkUpdateStatus(status) {
      if (this.selectedApplications.length === 0) return
      
      const confirmMsg = `${status} ${this.selectedApplications.length} applications?`
      if (!confirm(confirmMsg)) return
      
      try {
        for (const appId of this.selectedApplications) {
          await companyAPI.updateApplicationStatus(appId, { status })
        }
        
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: `${this.selectedApplications.length} applications updated`
        })
        
        this.selectedApplications = []
        this.fetchApplications()
        this.fetchDrive()
      } catch (error) {
        console.error('Failed to bulk update:', error)
      }
    },
    
    async scheduleInterview() {
      if (!this.interviewForm.interview_date || !this.interviewForm.interview_mode) {
        alert('Please fill required fields')
        return
      }
      
      try {
        await companyAPI.scheduleInterview(this.selectedApplication.id, this.interviewForm)
        
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Interview scheduled successfully'
        })
        
        this.scheduleModal.hide()
        this.fetchApplications()
      } catch (error) {
        console.error('Failed to schedule interview:', error)
      }
    },
    
    getInitials(name) {
      if (!name) return 'U'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    },
    
    getCgpaBadge(cgpa) {
      if (cgpa >= 8.5) return 'bg-success'
      if (cgpa >= 7) return 'bg-primary'
      if (cgpa >= 6) return 'bg-warning text-dark'
      return 'bg-danger'
    },
    
    getStatusBadge(status) {
      const badges = {
        applied: 'bg-info',
        under_review: 'bg-warning text-dark',
        shortlisted: 'bg-primary',
        interview_scheduled: 'bg-info',
        interviewed: 'bg-secondary',
        selected: 'bg-success',
        rejected: 'bg-danger',
        withdrawn: 'bg-secondary'
      }
      return badges[status] || 'bg-secondary'
    },
    
    formatStatus(status) {
      return status ? status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A'
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      })
    },
    
    formatDateTime(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  },
  
  mounted() {
    this.fetchDrive()
    this.fetchApplications()
    
    this.applicationModal = new Modal(document.getElementById('applicationModal'))
    this.scheduleModal = new Modal(document.getElementById('scheduleModal'))
  }
}
</script>

<style scoped>
.avatar-sm {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}
</style>