<template>
  <div class="placement-history">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Placement History</h4>
        <p class="text-muted mb-0">Complete history of your placement journey</p>
      </div>
      <button class="btn btn-outline-primary" @click="exportHistory">
        <i class="bi bi-download me-2"></i>
        Export Report
      </button>
    </div>
    
    <!-- Summary Cards -->
    <div class="row g-4 mb-4">
      <div class="col-sm-6 col-lg-3">
        <div class="card text-center">
          <div class="card-body">
            <h3 class="text-primary">{{ history.total_applications }}</h3>
            <p class="text-muted mb-0">Total Applications</p>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-lg-3">
        <div class="card text-center bg-success text-white">
          <div class="card-body">
            <h3>{{ history.selected?.length || 0 }}</h3>
            <p class="mb-0 opacity-75">Offers Received</p>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-lg-3">
        <div class="card text-center bg-danger text-white">
          <div class="card-body">
            <h3>{{ history.rejected?.length || 0 }}</h3>
            <p class="mb-0 opacity-75">Rejected</p>
          </div>
        </div>
      </div>
      <div class="col-sm-6 col-lg-3">
        <div class="card text-center bg-warning">
          <div class="card-body">
            <h3>{{ history.in_progress?.length || 0 }}</h3>
            <p class="mb-0 opacity-75">In Progress</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Placement Status Banner -->
    <div class="alert alert-success d-flex align-items-center mb-4" v-if="isPlaced">
      <i class="bi bi-trophy-fill fs-3 me-3"></i>
      <div>
        <h5 class="mb-1">Congratulations! You are placed!</h5>
        <p class="mb-0">You have received {{ placementCount }} offer(s).</p>
      </div>
    </div>
    
    <!-- Loading -->
    <div class="text-center py-5" v-if="loading">
      <div class="spinner-border text-primary"></div>
      <p class="text-muted mt-2">Loading history...</p>
    </div>
    
    <template v-else>
      <!-- Selected/Offers Section -->
      <div class="card mb-4" v-if="history.selected?.length">
        <div class="card-header bg-success text-white">
          <h6 class="mb-0">
            <i class="bi bi-trophy me-2"></i>
            Offers Received ({{ history.selected.length }})
          </h6>
        </div>
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="bg-light">
              <tr>
                <th>Company</th>
                <th>Position</th>
                <th>Offer Salary</th>
                <th>Selected On</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in history.selected" :key="app.id">
                <td>
                  <div class="d-flex align-items-center">
                    <img 
                      :src="app.drive?.company_logo || 'https://via.placeholder.com/32'"
                      class="rounded me-2"
                      width="32"
                      height="32"
                    >
                    {{ app.drive?.company_name }}
                  </div>
                </td>
                <td>{{ app.drive?.job_title }}</td>
                <td>
                  <span class="text-success fw-bold" v-if="app.offer_salary">
                    {{ formatSalary(app.offer_salary) }}
                  </span>
                  <span class="text-muted" v-else>{{ app.drive?.salary_display }}</span>
                </td>
                <td>{{ formatDate(app.selected_at) }}</td>
                <td>
                  <span class="badge" :class="getOfferStatusBadge(app.status)">
                    {{ formatStatus(app.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- In Progress Section -->
      <div class="card mb-4" v-if="history.in_progress?.length">
        <div class="card-header bg-warning">
          <h6 class="mb-0">
            <i class="bi bi-hourglass-split me-2"></i>
            In Progress ({{ history.in_progress.length }})
          </h6>
        </div>
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="bg-light">
              <tr>
                <th>Company</th>
                <th>Position</th>
                <th>Applied On</th>
                <th>Current Status</th>
                <th>Next Step</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in history.in_progress" :key="app.id">
                <td>
                  <div class="d-flex align-items-center">
                    <img 
                      :src="app.drive?.company_logo || 'https://via.placeholder.com/32'"
                      class="rounded me-2"
                      width="32"
                      height="32"
                    >
                    {{ app.drive?.company_name }}
                  </div>
                </td>
                <td>{{ app.drive?.job_title }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>
                  <span class="badge" :class="getStatusBadge(app.status)">
                    {{ formatStatus(app.status) }}
                  </span>
                </td>
                <td>
                  <span v-if="app.status === 'interview_scheduled' && app.interview_date">
                    <i class="bi bi-calendar-event me-1"></i>
                    Interview: {{ formatDateTime(app.interview_date) }}
                  </span>
                  <span v-else-if="app.status === 'applied'" class="text-muted">
                    Awaiting review
                  </span>
                  <span v-else-if="app.status === 'shortlisted'" class="text-muted">
                    Interview to be scheduled
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Rejected Section -->
      <div class="card mb-4" v-if="history.rejected?.length">
        <div class="card-header bg-danger text-white">
          <h6 class="mb-0">
            <i class="bi bi-x-circle me-2"></i>
            Not Selected ({{ history.rejected.length }})
          </h6>
        </div>
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="bg-light">
              <tr>
                <th>Company</th>
                <th>Position</th>
                <th>Applied On</th>
                <th>Rejected On</th>
                <th>Feedback</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in history.rejected" :key="app.id">
                <td>
                  <div class="d-flex align-items-center">
                    <img 
                      :src="app.drive?.company_logo || 'https://via.placeholder.com/32'"
                      class="rounded me-2"
                      width="32"
                      height="32"
                    >
                    {{ app.drive?.company_name }}
                  </div>
                </td>
                <td>{{ app.drive?.job_title }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>{{ formatDate(app.rejected_at) }}</td>
                <td>
                  <span class="text-muted" v-if="app.company_remarks">
                    {{ app.company_remarks }}
                  </span>
                  <span class="text-muted" v-else>No feedback provided</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Withdrawn Section -->
      <div class="card mb-4" v-if="history.withdrawn?.length">
        <div class="card-header bg-secondary text-white">
          <h6 class="mb-0">
            <i class="bi bi-arrow-return-left me-2"></i>
            Withdrawn ({{ history.withdrawn.length }})
          </h6>
        </div>
        <div class="table-responsive">
          <table class="table table-hover mb-0">
            <thead class="bg-light">
              <tr>
                <th>Company</th>
                <th>Position</th>
                <th>Applied On</th>
                <th>Withdrawn On</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in history.withdrawn" :key="app.id">
                <td>
                  <div class="d-flex align-items-center">
                    <img 
                      :src="app.drive?.company_logo || 'https://via.placeholder.com/32'"
                      class="rounded me-2"
                      width="32"
                      height="32"
                    >
                    {{ app.drive?.company_name }}
                  </div>
                </td>
                <td>{{ app.drive?.job_title }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>{{ formatDate(app.updated_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Empty State -->
      <div class="card" v-if="!hasAnyApplications">
        <div class="card-body text-center py-5">
          <i class="bi bi-inbox fs-1 text-muted"></i>
          <h5 class="mt-3">No Placement History</h5>
          <p class="text-muted mb-4">You haven't applied to any placement drives yet.</p>
          <router-link to="/student/drives" class="btn btn-primary">
            <i class="bi bi-search me-2"></i>
            Browse Drives
          </router-link>
        </div>
      </div>
      
      <!-- Timeline View -->
      <div class="card mt-4" v-if="hasAnyApplications">
        <div class="card-header">
          <h6 class="mb-0">
            <i class="bi bi-clock-history me-2"></i>
            Application Timeline
          </h6>
        </div>
        <div class="card-body">
          <div class="timeline-container">
            <div 
              class="timeline-item"
              v-for="app in sortedApplications"
              :key="app.id"
            >
              <div class="timeline-marker" :class="getTimelineMarkerClass(app.status)">
                <i :class="getTimelineIcon(app.status)"></i>
              </div>
              <div class="timeline-content">
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 class="mb-1">{{ app.drive?.job_title }}</h6>
                    <p class="text-muted small mb-1">{{ app.drive?.company_name }}</p>
                    <span class="badge" :class="getStatusBadge(app.status)">
                      {{ formatStatus(app.status) }}
                    </span>
                  </div>
                  <small class="text-muted">{{ formatDate(app.applied_at) }}</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { studentAPI } from '../../services/api'

export default {
  name: 'PlacementHistory',
  
  data() {
    return {
      loading: true,
      history: {
        total_applications: 0,
        selected: [],
        rejected: [],
        in_progress: [],
        withdrawn: []
      },
      isPlaced: false,
      placementCount: 0
    }
  },
  
  computed: {
    hasAnyApplications() {
      return (
        this.history.selected?.length ||
        this.history.rejected?.length ||
        this.history.in_progress?.length ||
        this.history.withdrawn?.length
      )
    },
    
    sortedApplications() {
      const all = [
        ...(this.history.selected || []),
        ...(this.history.rejected || []),
        ...(this.history.in_progress || []),
        ...(this.history.withdrawn || [])
      ]
      return all.sort((a, b) => new Date(b.applied_at) - new Date(a.applied_at))
    }
  },
  
  methods: {
    async fetchHistory() {
      this.loading = true
      try {
        const response = await studentAPI.getPlacementHistory()
        this.history = response.data.history || {}
        this.isPlaced = response.data.is_placed || false
        this.placementCount = response.data.placement_count || 0
      } catch (error) {
        console.error('Failed to fetch history:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: 'Failed to load placement history'
        })
      } finally {
        this.loading = false
      }
    },
    
    async exportHistory() {
      try {
        await studentAPI.exportApplications()
        this.$store.dispatch('showNotification', {
          type: 'info',
          message: 'Export started. You will receive an email when ready.'
        })
      } catch (error) {
        console.error('Failed to export:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: 'Failed to start export'
        })
      }
    },
    
    formatStatus(status) {
      if (!status) return 'N/A'
      return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
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
    
    getOfferStatusBadge(status) {
      const badges = {
        selected: 'bg-warning',
        offer_accepted: 'bg-success',
        offer_declined: 'bg-secondary'
      }
      return badges[status] || 'bg-success'
    },
    
    getTimelineMarkerClass(status) {
      const classes = {
        selected: 'bg-success',
        offer_accepted: 'bg-success',
        rejected: 'bg-danger',
        withdrawn: 'bg-secondary'
      }
      return classes[status] || 'bg-primary'
    },
    
    getTimelineIcon(status) {
      const icons = {
        selected: 'bi bi-trophy-fill',
        offer_accepted: 'bi bi-check-circle-fill',
        rejected: 'bi bi-x-circle-fill',
        withdrawn: 'bi bi-arrow-return-left',
        applied: 'bi bi-send-fill',
        shortlisted: 'bi bi-star-fill',
        interview_scheduled: 'bi bi-calendar-check-fill'
      }
      return icons[status] || 'bi bi-circle-fill'
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
    this.fetchHistory()
  }
}
</script>

<style scoped>
.timeline-container {
  position: relative;
  padding-left: 40px;
}

.timeline-container::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #e9ecef;
}

.timeline-item {
  position: relative;
  padding-bottom: 25px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -40px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
}

.timeline-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
}
</style>