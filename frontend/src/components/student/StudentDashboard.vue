<template>
  <div class="student-dashboard">
    <!-- Welcome Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Welcome, {{ studentName }}!</h4>
        <p class="text-muted mb-0">Here's your placement overview</p>
      </div>
      <router-link to="/student/drives" class="btn btn-primary">
        <i class="bi bi-search me-2"></i>
        Browse Drives
      </router-link>
    </div>
    
    <!-- Stats Cards -->
    <div class="row g-4 mb-4">
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Total Applications"
          :value="stats.total_applications"
          icon="bi bi-file-text"
          color="primary"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Shortlisted"
          :value="stats.shortlisted"
          icon="bi bi-check-circle"
          color="info"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Interviews"
          :value="stats.interview_scheduled"
          icon="bi bi-calendar-check"
          color="warning"
          :loading="loading"
        />
      </div>
      <div class="col-sm-6 col-xl-3">
        <StatCard 
          title="Offers"
          :value="stats.selected"
          icon="bi bi-trophy"
          color="success"
          :loading="loading"
        />
      </div>
    </div>
    
    <!-- Profile Completion Alert -->
    <div class="alert alert-info d-flex align-items-center mb-4" v-if="profileIncomplete">
      <i class="bi bi-info-circle fs-4 me-3"></i>
      <div>
        <strong>Complete Your Profile</strong>
        <p class="mb-0 small">Add your skills, resume, and other details to improve your visibility.</p>
      </div>
      <router-link to="/student/profile" class="btn btn-info btn-sm ms-auto">
        Complete Profile
      </router-link>
    </div>
    
    <!-- Main Content -->
    <div class="row g-4">
      <!-- Upcoming Interviews -->
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-calendar-event me-2 text-primary"></i>
              Upcoming Interviews
            </h6>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div 
                class="list-group-item"
                v-for="interview in upcomingInterviews"
                :key="interview.id"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 class="mb-1">{{ interview.drive?.job_title }}</h6>
                    <p class="text-muted small mb-1">{{ interview.drive?.company_name }}</p>
                    <div class="d-flex gap-2">
                      <span class="badge bg-light text-dark">
                        <i class="bi bi-clock me-1"></i>
                        {{ formatDateTime(interview.interview_date) }}
                      </span>
                      <span class="badge bg-light text-dark">
                        <i class="bi bi-camera-video me-1"></i>
                        {{ interview.interview_mode }}
                      </span>
                    </div>
                  </div>
                  <a 
                    v-if="interview.interview_link"
                    :href="interview.interview_link"
                    target="_blank"
                    class="btn btn-sm btn-primary"
                  >
                    Join
                  </a>
                </div>
              </div>
              <div class="list-group-item text-center text-muted py-4" v-if="upcomingInterviews.length === 0">
                <i class="bi bi-calendar-x fs-3 mb-2 d-block"></i>
                No upcoming interviews
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Applications -->
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-clock-history me-2 text-primary"></i>
              Recent Applications
            </h6>
            <router-link to="/student/applications" class="small">View All</router-link>
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
                    <h6 class="mb-1">{{ app.drive?.job_title }}</h6>
                    <p class="text-muted small mb-0">{{ app.drive?.company_name }}</p>
                  </div>
                  <span class="badge" :class="getStatusBadge(app.status)">
                    {{ formatStatus(app.status) }}
                  </span>
                </div>
              </div>
              <div class="list-group-item text-center text-muted py-4" v-if="recentApplications.length === 0">
                <i class="bi bi-inbox fs-3 mb-2 d-block"></i>
                No applications yet
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Eligible Drives -->
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h6 class="mb-0">
              <i class="bi bi-briefcase me-2 text-primary"></i>
              Recommended Drives for You
            </h6>
            <router-link to="/student/drives" class="btn btn-sm btn-outline-primary">
              View All Drives
            </router-link>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6 col-lg-4" v-for="drive in eligibleDrives" :key="drive.id">
                <div class="card h-100 border">
                  <div class="card-body">
                    <div class="d-flex align-items-start mb-2">
                      <img 
                        :src="drive.company?.logo_url || 'https://via.placeholder.com/40'"
                        class="rounded me-2"
                        width="40"
                        height="40"
                      >
                      <div>
                        <h6 class="mb-0">{{ drive.job_title }}</h6>
                        <small class="text-muted">{{ drive.company?.company_name }}</small>
                      </div>
                    </div>
                    <div class="d-flex flex-wrap gap-1 mb-2">
                      <span class="badge bg-light text-dark small">{{ drive.job_type }}</span>
                      <span class="badge bg-light text-dark small">{{ drive.job_location || 'Remote' }}</span>
                    </div>
                    <p class="text-success small mb-2">{{ drive.salary_display }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                      <small class="text-muted">
                        <i class="bi bi-clock me-1"></i>
                        {{ getDaysLeft(drive.application_deadline) }} days left
                      </small>
                      <router-link 
                        :to="`/student/drives/${drive.id}`"
                        class="btn btn-sm btn-primary"
                      >
                        Apply
                      </router-link>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12 text-center py-4" v-if="eligibleDrives.length === 0">
                <i class="bi bi-briefcase fs-1 text-muted"></i>
                <p class="text-muted mt-2 mb-0">No matching drives found. Check back later!</p>
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
import { studentAPI } from '../../services/api'

export default {
  name: 'StudentDashboard',
  
  components: {
    StatCard
  },
  
  data() {
    return {
      loading: true,
      stats: {
        total_applications: 0,
        shortlisted: 0,
        interview_scheduled: 0,
        selected: 0,
        eligible_drives: 0
      },
      upcomingInterviews: [],
      recentApplications: [],
      eligibleDrives: []
    }
  },
  
  computed: {
    studentName() {
      return this.$store.state.profile?.first_name || 'Student'
    },
    
    profileIncomplete() {
      const profile = this.$store.state.profile
      return !profile?.resume_url || !profile?.skills
    }
  },
  
  methods: {
    async fetchDashboard() {
      this.loading = true
      try {
        const data = await studentAPI.getDashboard()
        
        this.stats = data.statistics || {}
        this.upcomingInterviews = data.upcoming_interviews || []
        this.recentApplications = data.recent_applications || []
      } catch (error) {
        console.error('Failed to fetch dashboard:', error)
      } finally {
        this.loading = false
      }
    },
    
    async fetchEligibleDrives() {
      try {
        const response = await studentAPI.getDrives({ per_page: 6 })
        const drives = response?.drives || response?.data?.drives || []
        this.eligibleDrives = drives.filter(d => d.is_eligible && !d.has_applied)
      } catch (error) {
        console.error('Failed to fetch drives:', error)
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
        selected: 'bg-success',
        rejected: 'bg-danger'
      }
      return badges[status] || 'bg-secondary'
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
    
    getDaysLeft(deadline) {
      if (!deadline) return 0
      const days = Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24))
      return days > 0 ? days : 0
    }
  },
  
  mounted() {
    this.fetchDashboard()
    this.fetchEligibleDrives()
  }
}
</script>