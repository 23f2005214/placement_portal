<template>
  <div class="company-dashboard">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Company Dashboard</h4>
        <p class="text-muted mb-0">Welcome back, {{ companyName }}!</p>
      </div>
      <router-link to="/company/drives/create" class="btn btn-primary" v-if="companyApproved">
        <i class="bi bi-plus-lg me-2"></i>
        Create Drive
      </router-link>
    </div>
    
    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Total Drives"
          :value="stats.total_drives"
          icon="bi bi-briefcase"
          color="primary"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Active Drives"
          :value="stats.active_drives"
          icon="bi bi-broadcast"
          color="success"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Total Applications"
          :value="stats.total_applications"
          icon="bi bi-file-text"
          color="info"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Hired"
          :value="stats.selected"
          icon="bi bi-person-check"
          color="warning"
          :loading="loading"
        />
      </div>
    </div>
    
    <!-- Main Content -->
    <div class="row g-4">
      <!-- Recent Drives -->
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">Recent Placement Drives</h6>
            <router-link to="/company/drives" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body p-0">
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="bg-light">
                  <tr>
                    <th>Job Title</th>
                    <th>Status</th>
                    <th>Applications</th>
                    <th>Deadline</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="loading">
                    <td colspan="5" class="text-center py-4">
                      <div class="spinner-border spinner-border-sm text-primary"></div>
                    </td>
                  </tr>
                  <tr v-else-if="recentDrives.length === 0">
                    <td colspan="5" class="text-center py-4 text-muted">
                      No drives created yet
                    </td>
                  </tr>
                  <tr v-else v-for="drive in recentDrives" :key="drive.id">
                    <td>
                      <p class="mb-0 fw-medium">{{ drive.job_title }}</p>
                      <small class="text-muted">{{ drive.job_type }}</small>
                    </td>
                    <td>
                      <span class="badge" :class="getStatusBadge(drive.status)">
                        {{ drive.status }}
                      </span>
                    </td>
                    <td>{{ drive.application_count }}</td>
                    <td>{{ formatDate(drive.application_deadline) }}</td>
                    <td>
                      <router-link 
                        :to="`/company/drives/${drive.id}/applications`"
                        class="btn btn-sm btn-outline-primary"
                        v-if="drive.status === 'approved'"
                      >
                        View Apps
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Applications -->
      <div class="col-lg-4">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Recent Applications</h6>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div 
                class="list-group-item"
                v-for="app in recentApplications"
                :key="app.id"
              >
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <p class="mb-0 fw-medium">{{ app.student?.full_name }}</p>
                    <small class="text-muted">
                      {{ app.drive?.job_title }} • {{ formatDate(app.applied_at) }}
                    </small>
                  </div>
                  <span class="badge" :class="getAppStatusBadge(app.status)">
                    {{ app.status }}
                  </span>
                </div>
              </div>
              <div class="list-group-item text-center text-muted" v-if="recentApplications.length === 0">
                No recent applications
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
import { companyAPI } from '../../services/api'

export default {
  name: 'CompanyDashboard',
  
  components: {
    StatCard
  },
  
  data() {
    return {
      loading: true,
      stats: {
        total_drives: 0,
        active_drives: 0,
        total_applications: 0,
        selected: 0
      },
      recentDrives: [],
      recentApplications: []
    }
  },
  
  computed: {
    companyName() {
      return this.$store.state.profile?.company_name || 'Company'
    },
    
    companyApproved() {
      return this.$store.getters.companyApproved
    }
  },
  
  methods: {
    async fetchDashboard() {
      this.loading = true
      try {
        const response = await companyAPI.getDashboard()
        const data = response.data
        
        this.stats = data.statistics || {}
        this.recentDrives = data.recent_drives || []
        this.recentApplications = data.recent_applications || []
      } catch (error) {
        console.error('Failed to fetch dashboard:', error)
      } finally {
        this.loading = false
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
    
    getAppStatusBadge(status) {
      const badges = {
        applied: 'bg-info',
        shortlisted: 'bg-primary',
        selected: 'bg-success',
        rejected: 'bg-danger'
      }
      return badges[status] || 'bg-secondary'
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