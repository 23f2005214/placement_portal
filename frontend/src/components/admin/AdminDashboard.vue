<template>
  <div class="admin-dashboard">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Admin Dashboard</h4>
        <p class="text-muted mb-0">Welcome back! Here's what's happening.</p>
      </div>
      <div>
        <button class="btn btn-primary" @click="refreshData">
          <i class="bi bi-arrow-clockwise me-2"></i>
          Refresh
        </button>
      </div>
    </div>
    
    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Total Students"
          :value="stats.total_students"
          icon="bi bi-people"
          color="primary"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Total Companies"
          :value="stats.total_companies"
          icon="bi bi-building"
          color="success"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Active Drives"
          :value="stats.approved_drives"
          icon="bi bi-briefcase"
          color="info"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Placement Rate"
          :value="stats.placement_rate"
          icon="bi bi-graph-up"
          color="warning"
          format="percentage"
          :loading="loading"
        />
      </div>
    </div>
    
    <!-- Pending Approvals Alert -->
    <div class="alert alert-warning d-flex align-items-center mb-4" v-if="hasPendingItems">
      <i class="bi bi-exclamation-triangle fs-4 me-3"></i>
      <div>
        <strong>Pending Approvals:</strong>
        <span v-if="stats.pending_companies > 0">
          {{ stats.pending_companies }} companies
        </span>
        <span v-if="stats.pending_companies > 0 && stats.pending_drives > 0"> and </span>
        <span v-if="stats.pending_drives > 0">
          {{ stats.pending_drives }} drives
        </span>
        awaiting your approval.
      </div>
      <router-link 
        :to="stats.pending_companies > 0 ? '/admin/companies' : '/admin/drives'"
        class="btn btn-warning btn-sm ms-auto"
      >
        Review Now
      </router-link>
    </div>
    
    <!-- Main Content Row -->
    <div class="row g-4">
      <!-- Recent Applications -->
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Recent Applications</h6>
            <router-link to="/admin/drives" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="bg-light">
                  <tr>
                    <th>Student</th>
                    <th>Company</th>
                    <th>Position</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loading">
                    <td colspan="5" class="text-center py-4">
                      <div class="spinner-border spinner-border-sm text-primary"></div>
                    </td>
                  </tr>
                  <tr v-else-if="recentApplications.length === 0">
                    <td colspan="5" class="text-center py-4 text-muted">
                      No recent applications
                    </td>
                  </tr>
                  <tr v-else v-for="app in recentApplications" :key="app.id">
                    <td>
                      <div class="d-flex align-items-center">
                        <div class="avatar-sm bg-primary text-white rounded-circle me-2">
                          {{ getInitials(app.student?.full_name) }}
                        </div>
                        <div>
                          <p class="mb-0 fw-medium">{{ app.student?.full_name }}</p>
                          <small class="text-muted">{{ app.student?.branch }}</small>
                        </div>
                      </div>
                    </td>
                    <td>{{ app.drive?.company_name }}</td>
                    <td>{{ app.drive?.job_title }}</td>
                    <td>
                      <span class="badge" :class="getStatusBadgeClass(app.status)">
                        {{ formatStatus(app.status) }}
                      </span>
                    </td>
                    <td>{{ formatDate(app.applied_at) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Quick Stats / Sidebar -->
      <div class="col-lg-4">
        <!-- Weekly Stats -->
        <div class="card mb-4">
          <div class="card-header">
            <h6 class="mb-0">This Week</h6>
          </div>
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="text-muted">New Students</span>
              <span class="fw-bold">{{ weeklyStats.new_students }}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="text-muted">New Companies</span>
              <span class="fw-bold">{{ weeklyStats.new_companies }}</span>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <span class="text-muted">New Applications</span>
              <span class="fw-bold">{{ weeklyStats.new_applications }}</span>
            </div>
          </div>
        </div>
        
        <!-- Recent Drives -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Recent Drives</h6>
            <router-link to="/admin/drives" class="small">View All</router-link>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div 
                class="list-group-item"
                v-for="drive in recentDrives"
                :key="drive.id"
              >
                <div class="d-flex justify-content-between">
                  <div>
                    <p class="mb-1 fw-medium">{{ drive.job_title }}</p>
                    <small class="text-muted">{{ drive.company?.company_name }}</small>
                  </div>
                  <span class="badge" :class="getDriveStatusBadge(drive.status)">
                    {{ drive.status }}
                  </span>
                </div>
              </div>
              <div class="list-group-item text-center text-muted" v-if="recentDrives.length === 0">
                No recent drives
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import StatCard from '../common/StatCard.vue'
import { adminAPI } from '../../services/api'

export default {
  name: 'AdminDashboard',
  
  components: {
    StatCard
  },
  
  data() {
    return {
      loading: true,
      stats: {
        total_students: 0,
        total_companies: 0,
        total_drives: 0,
        approved_drives: 0,
        pending_companies: 0,
        pending_drives: 0,
        placement_rate: 0
      },
      weeklyStats: {
        new_students: 0,
        new_companies: 0,
        new_applications: 0
      },
      recentApplications: [],
      recentDrives: []
    }
  },
  
  computed: {
    hasPendingItems() {
      return this.stats.pending_companies > 0 || this.stats.pending_drives > 0
    }
  },
  
  methods: {
    async fetchDashboard() {
      this.loading = true
      try {
        const response = await adminAPI.getDashboard()
        const data = response.data
        
        this.stats = data.statistics || {}
        this.weeklyStats = data.weekly || {}
        this.recentApplications = data.recent_applications || []
        this.recentDrives = data.recent_drives || []
      } catch (error) {
        console.error('Failed to fetch dashboard:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: 'Failed to load dashboard data'
        })
      } finally {
        this.loading = false
      }
    },
    
    refreshData() {
      this.fetchDashboard()
    },
    
    getInitials(name) {
      if (!name) return 'U'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    },
    
    formatStatus(status) {
      return status ? status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A'
    },
    
    getStatusBadgeClass(status) {
      const classes = {
        applied: 'bg-info',
        under_review: 'bg-warning',
        shortlisted: 'bg-primary',
        interview_scheduled: 'bg-info',
        selected: 'bg-success',
        rejected: 'bg-danger',
        withdrawn: 'bg-secondary'
      }
      return classes[status] || 'bg-secondary'
    },
    
    getDriveStatusBadge(status) {
      const classes = {
        pending: 'bg-warning',
        approved: 'bg-success',
        rejected: 'bg-danger',
        completed: 'bg-secondary'
      }
      return classes[status] || 'bg-secondary'
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
    this.fetchDashboard()
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