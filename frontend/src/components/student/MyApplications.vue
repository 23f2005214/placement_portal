<template>
  <div class="my-applications">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">My Applications</h4>
        <p class="text-muted mb-0">Track all your job applications</p>
      </div>
      <button class="btn btn-outline-primary" @click="exportApplications" :disabled="exporting">
        <span v-if="exporting">
          <span class="spinner-border spinner-border-sm me-2"></span>
          Exporting...
        </span>
        <span v-else>
          <i class="bi bi-download me-2"></i>
          Export CSV
        </span>
      </button>
    </div>
    
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body py-3">
        <div class="row g-3">
          <div class="col-md-4">
            <input 
              type="text" 
              class="form-control"
              placeholder="Search applications..."
              v-model="searchQuery"
            >
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="statusFilter" @change="fetchApplications">
              <option value="">All Status</option>
              <option value="applied">Applied</option>
              <option value="shortlisted">Shortlisted</option>
              <option value="interview_scheduled">Interview Scheduled</option>
              <option value="selected">Selected</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Applications List -->
    <div class="text-center py-5" v-if="loading">
      <div class="spinner-border text-primary"></div>
    </div>
    
    <div class="card" v-else-if="filteredApplications.length === 0">
      <div class="card-body text-center py-5">
        <i class="bi bi-inbox fs-1 text-muted"></i>
        <p class="text-muted mt-2 mb-3">No applications found</p>
        <router-link to="/student/drives" class="btn btn-primary">
          Browse Drives
        </router-link>
      </div>
    </div>
    
    <div class="row g-4" v-else>
      <div class="col-md-6" v-for="app in filteredApplications" :key="app.id">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex">
                <img 
                  :src="app.drive?.company_logo || 'https://via.placeholder.com/48'"
                  class="rounded me-3"
                  width="48"
                  height="48"
                >
                <div>
                  <h6 class="mb-1">{{ app.drive?.job_title }}</h6>
                  <p class="text-muted small mb-0">{{ app.drive?.company_name }}</p>
                </div>
              </div>
              <span class="badge" :class="getStatusBadge(app.status)">
                {{ formatStatus(app.status) }}
              </span>
            </div>
            
            <!-- Timeline -->
            <div class="timeline mb-3">
              <div class="timeline-item" :class="{ active: true }">
                <i class="bi bi-check-circle-fill"></i>
                <span>Applied on {{ formatDate(app.applied_at) }}</span>
              </div>
              <div 
                class="timeline-item"
                :class="{ active: isStatusReached(app.status, 'shortlisted') }"
                v-if="app.shortlisted_at || isStatusReached(app.status, 'shortlisted')"
              >
                <i class="bi bi-check-circle-fill"></i>
                <span>Shortlisted {{ app.shortlisted_at ? 'on ' + formatDate(app.shortlisted_at) : '' }}</span>
              </div>
              <div 
                class="timeline-item"
                :class="{ active: app.status === 'interview_scheduled' }"
                v-if="app.interview_date"
              >
                <i class="bi bi-calendar-check"></i>
                <span>Interview: {{ formatDateTime(app.interview_date) }}</span>
              </div>
              <div 
                class="timeline-item"
                :class="{ active: app.status === 'selected', rejected: app.status === 'rejected' }"
                v-if="['selected', 'rejected'].includes(app.status)"
              >
                <i :class="app.status === 'selected' ? 'bi bi-trophy-fill' : 'bi bi-x-circle-fill'"></i>
                <span>{{ app.status === 'selected' ? 'Selected!' : 'Not selected' }}</span>
              </div>
            </div>
            
            <!-- Interview Details -->
            <div class="alert alert-info small py-2 mb-3" v-if="app.status === 'interview_scheduled' && app.interview_date">
              <strong>Interview Details:</strong><br>
              <i class="bi bi-clock me-1"></i> {{ formatDateTime(app.interview_date) }}<br>
              <i class="bi bi-camera-video me-1"></i> {{ app.interview_mode }}
              <span v-if="app.interview_link">
                <br>
                <a :href="app.interview_link" target="_blank" class="text-primary">
                  Join Meeting <i class="bi bi-box-arrow-up-right"></i>
                </a>
              </span>
            </div>
            
            <!-- Offer Details -->
            <div class="alert alert-success small py-2 mb-3" v-if="app.status === 'selected' && app.offer_salary">
              <strong>Offer Details:</strong><br>
              <i class="bi bi-currency-rupee me-1"></i> {{ formatSalary(app.offer_salary) }}<br>
              <i class="bi bi-briefcase me-1"></i> {{ app.offer_position || app.drive?.job_title }}
            </div>
            
            <!-- Actions -->
            <div class="d-flex gap-2">
              <router-link 
                :to="`/student/drives/${app.drive_id}`"
                class="btn btn-sm btn-outline-primary"
              >
                View Drive
              </router-link>
              <button 
                class="btn btn-sm btn-outline-danger"
                v-if="['applied', 'under_review', 'shortlisted'].includes(app.status)"
                @click="withdrawApplication(app)"
              >
                Withdraw
              </button>
              <div class="btn-group btn-group-sm" v-if="app.status === 'selected'">
                <button class="btn btn-success" @click="respondToOffer(app, 'accept')">
                  Accept Offer
                </button>
                <button class="btn btn-outline-danger" @click="respondToOffer(app, 'decline')">
                  Decline
                </button>
              </div>
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
            v-for="page in pagination.pages" 
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
  name: 'MyApplications',
  
  data() {
    return {
      loading: true,
      applications: [],
      pagination: {
        page: 1,
        per_page: 10,
        total: 0,
        pages: 1,
        has_next: false,
        has_prev: false
      },
      searchQuery: '',
      statusFilter: '',
      exporting: false
    }
  },
  
  computed: {
    filteredApplications() {
      if (!this.searchQuery) return this.applications
      
      const query = this.searchQuery.toLowerCase()
      return this.applications.filter(app => 
        app.drive?.job_title?.toLowerCase().includes(query) ||
        app.drive?.company_name?.toLowerCase().includes(query)
      )
    }
  },
  
  methods: {
    async fetchApplications() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          status: this.statusFilter
        }
        
        const response = await studentAPI.getApplications(params)
        this.applications = response.data.applications || []
        this.pagination = response.data.pagination || this.pagination
      } catch (error) {
        console.error('Failed to fetch applications:', error)
      } finally {
        this.loading = false
      }
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.pagination.page = page
        this.fetchApplications()
      }
    },
    
    async withdrawApplication(app) {
      if (!confirm('Are you sure you want to withdraw this application?')) return
      
      try {
        await studentAPI.withdrawApplication(app.id)
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Application withdrawn successfully'
        })
        this.fetchApplications()
      } catch (error) {
        console.error('Failed to withdraw:', error)
      }
    },
    
    async respondToOffer(app, response) {
      const action = response === 'accept' ? 'accept' : 'decline'
      if (!confirm(`Are you sure you want to ${action} this offer?`)) return
      
      try {
        await studentAPI.respondToOffer(app.id, { response })
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: `Offer ${action}ed successfully`
        })
        this.fetchApplications()
        this.$store.dispatch('refreshUserData')
      } catch (error) {
        console.error('Failed to respond:', error)
      }
    },
    
    async exportApplications() {
      this.exporting = true
      try {
        const response = await studentAPI.exportApplications()
        this.$store.dispatch('showNotification', {
          type: 'info',
          message: 'Export started. You will be notified when ready.'
        })
        
        // Poll for status
        const taskId = response.data.task_id
        this.pollExportStatus(taskId)
      } catch (error) {
        console.error('Failed to export:', error)
        this.exporting = false
      }
    },
    
    async pollExportStatus(taskId) {
      try {
        const response = await studentAPI.checkExportStatus(taskId)
        
        if (response.data.status === 'completed') {
          this.$store.dispatch('showNotification', {
            type: 'success',
            message: 'Export completed! Check your email.'
          })
          this.exporting = false
        } else if (response.data.status === 'failed') {
          this.$store.dispatch('showNotification', {
            type: 'error',
            message: 'Export failed. Please try again.'
          })
          this.exporting = false
        } else {
          // Still processing, poll again
          setTimeout(() => this.pollExportStatus(taskId), 2000)
        }
      } catch (error) {
        this.exporting = false
      }
    },
    
    formatStatus(status) {
      return status ? status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A'
    },
    
    getStatusBadge(status) {
      const badges = {
        applied: 'bg-info',
        under_review: 'bg-warning',
        shortlisted: 'bg-primary',
        interview_scheduled: 'bg-info',
        interviewed: 'bg-secondary',
        selected: 'bg-success',
        rejected: 'bg-danger',
        offer_accepted: 'bg-success',
        offer_declined: 'bg-secondary',
        withdrawn: 'bg-secondary'
      }
      return badges[status] || 'bg-secondary'
    },
    
    isStatusReached(currentStatus, targetStatus) {
      const order = ['applied', 'under_review', 'shortlisted', 'interview_scheduled', 'interviewed', 'selected']
      return order.indexOf(currentStatus) >= order.indexOf(targetStatus)
    },
    
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short'
      })
    },
    
    formatDateTime(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    formatSalary(salary) {
      if (!salary) return 'N/A'
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
      }).format(salary)
    }
  },
  
  mounted() {
    this.fetchApplications()
  }
}
</script>

<style scoped>
.timeline {
  padding-left: 20px;
  border-left: 2px solid #e9ecef;
}

.timeline-item {
  position: relative;
  padding-left: 15px;
  padding-bottom: 10px;
  color: #6c757d;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-item i {
  position: absolute;
  left: -26px;
  top: 2px;
  background: white;
  color: #e9ecef;
}

.timeline-item.active i {
  color: #28a745;
}

.timeline-item.rejected i {
  color: #dc3545;
}

.timeline-item.active {
  color: #212529;
}
</style>