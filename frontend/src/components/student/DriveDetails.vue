<template>
  <div class="drive-details">
    <!-- Breadcrumb -->
    <nav aria-label="breadcrumb" class="mb-4">
      <ol class="breadcrumb">
        <li class="breadcrumb-item">
          <router-link to="/student/drives">Drives</router-link>
        </li>
        <li class="breadcrumb-item active">{{ drive?.job_title || 'Loading...' }}</li>
      </ol>
    </nav>
    
    <!-- Loading -->
    <div class="text-center py-5" v-if="loading">
      <div class="spinner-border text-primary"></div>
    </div>
    
    <div class="row g-4" v-else-if="drive">
      <!-- Main Content -->
      <div class="col-lg-8">
        <div class="card">
          <div class="card-body">
            <!-- Header -->
            <div class="d-flex align-items-start mb-4">
              <img 
                :src="drive.company?.logo_url || 'https://via.placeholder.com/64'"
                class="rounded me-3"
                width="64"
                height="64"
              >
              <div class="flex-grow-1">
                <h4 class="mb-1">{{ drive.job_title }}</h4>
                <p class="text-muted mb-2">{{ drive.company?.company_name }}</p>
                <div class="d-flex flex-wrap gap-2">
                  <span class="badge bg-primary">{{ drive.job_type }}</span>
                  <span class="badge bg-secondary">{{ drive.work_mode }}</span>
                  <span class="badge bg-light text-dark" v-if="drive.job_location">
                    <i class="bi bi-geo-alt me-1"></i>{{ drive.job_location }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Description -->
            <div class="mb-4">
              <h6>Job Description</h6>
              <p style="white-space: pre-line;">{{ drive.job_description }}</p>
            </div>
            
            <!-- Requirements -->
            <div class="mb-4" v-if="drive.required_skills?.length">
              <h6>Required Skills</h6>
              <div class="d-flex flex-wrap gap-2">
                <span 
                  class="badge bg-light text-dark"
                  v-for="skill in drive.required_skills"
                  :key="skill"
                >
                  {{ skill }}
                </span>
              </div>
            </div>
            
            <!-- Eligibility Criteria -->
            <div class="mb-4">
              <h6>Eligibility Criteria</h6>
              <ul class="list-unstyled">
                <li class="mb-2" v-if="drive.eligible_branches?.length">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  <strong>Branches:</strong> {{ drive.eligible_branches.join(', ') }}
                </li>
                <li class="mb-2" v-if="drive.min_cgpa">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  <strong>Minimum CGPA:</strong> {{ drive.min_cgpa }}
                </li>
                <li class="mb-2" v-if="drive.max_backlogs !== null">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  <strong>Maximum Backlogs:</strong> {{ drive.max_backlogs }}
                </li>
                <li class="mb-2" v-if="drive.eligible_graduation_years">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  <strong>Graduation Years:</strong> {{ drive.eligible_graduation_years }}
                </li>
                <li class="mb-2" v-if="drive.min_tenth_percentage">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  <strong>Min 10th %:</strong> {{ drive.min_tenth_percentage }}%
                </li>
                <li v-if="drive.min_twelfth_percentage">
                  <i class="bi bi-check-circle text-success me-2"></i>
                  <strong>Min 12th %:</strong> {{ drive.min_twelfth_percentage }}%
                </li>
              </ul>
            </div>
            
            <!-- Selection Process -->
            <div class="mb-4" v-if="drive.selection_process">
              <h6>Selection Process</h6>
              <p>{{ drive.selection_process }}</p>
              <p class="text-muted" v-if="drive.number_of_rounds">
                <i class="bi bi-layers me-1"></i>
                {{ drive.number_of_rounds }} rounds
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Sidebar -->
      <div class="col-lg-4">
        <!-- Apply Card -->
        <div class="card sticky-top" style="top: 20px;">
          <div class="card-body">
            <h5 class="text-success mb-3">{{ drive.salary_display }}</h5>
            
            <div class="mb-3">
              <p class="mb-2">
                <i class="bi bi-calendar me-2 text-muted"></i>
                <strong>Deadline:</strong> {{ formatDate(drive.application_deadline) }}
              </p>
              <p class="mb-2">
                <i class="bi bi-people me-2 text-muted"></i>
                <strong>Positions:</strong> {{ drive.number_of_positions }}
              </p>
              <p class="mb-0">
                <i class="bi bi-file-text me-2 text-muted"></i>
                <strong>Applications:</strong> {{ drive.application_count }}
              </p>
            </div>
            
            <!-- Eligibility Status -->
            <div class="alert mb-3" :class="drive.is_eligible ? 'alert-success' : 'alert-danger'">
              <div class="d-flex align-items-center">
                <i 
                  class="bi me-2 fs-5"
                  :class="drive.is_eligible ? 'bi-check-circle' : 'bi-x-circle'"
                ></i>
                <span>
                  {{ drive.is_eligible ? 'You are eligible to apply' : 'You are not eligible' }}
                </span>
              </div>
              <ul class="mb-0 mt-2 ps-4" v-if="!drive.is_eligible && drive.eligibility_reasons?.length">
                <li v-for="(reason, idx) in drive.eligibility_reasons" :key="idx" class="small">
                  {{ reason }}
                </li>
              </ul>
            </div>
            
            <!-- Already Applied -->
            <div class="alert alert-info mb-3" v-if="drive.has_applied">
              <i class="bi bi-info-circle me-2"></i>
              You have already applied to this drive.
              <p class="mb-0 mt-2">
                <strong>Status:</strong> 
                <span class="badge" :class="getStatusBadge(drive.application?.status)">
                  {{ formatStatus(drive.application?.status) }}
                </span>
              </p>
            </div>
            
            <!-- Apply Button -->
            <button 
              class="btn btn-primary w-100 mb-2"
              v-if="drive.is_eligible && !drive.has_applied && !drive.is_deadline_passed"
              @click="showApplyModal"
              :disabled="applying"
            >
              <i class="bi bi-send me-2"></i>
              Apply Now
            </button>
            
            <button class="btn btn-secondary w-100" disabled v-else-if="drive.is_deadline_passed">
              <i class="bi bi-clock me-2"></i>
              Deadline Passed
            </button>
            
            <router-link 
              to="/student/applications"
              class="btn btn-outline-primary w-100"
              v-if="drive.has_applied"
            >
              View My Application
            </router-link>
            
            <!-- Company Website -->
            <a 
              v-if="drive.company?.website"
              :href="drive.company.website"
              target="_blank"
              class="btn btn-outline-secondary w-100 mt-2"
            >
              <i class="bi bi-globe me-2"></i>
              Visit Company Website
            </a>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Apply Modal -->
    <div class="modal fade" id="applyModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Apply to {{ drive?.job_title }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Cover Letter (Optional)</label>
              <textarea 
                class="form-control"
                v-model="coverLetter"
                rows="5"
                placeholder="Write a brief cover letter explaining why you're a good fit..."
              ></textarea>
            </div>
            <div class="alert alert-info small">
              <i class="bi bi-info-circle me-2"></i>
              Your current resume and profile will be shared with the company.
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="submitApplication"
              :disabled="applying"
            >
              <span v-if="applying">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Submitting...
              </span>
              <span v-else>
                <i class="bi bi-send me-2"></i>
                Submit Application
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { studentAPI } from '../../services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'DriveDetails',
  
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
      coverLetter: '',
      applying: false,
      applyModal: null
    }
  },
  
  methods: {
    async fetchDrive() {
      this.loading = true
      try {
        const response = await studentAPI.getDrive(this.id)
        this.drive = response.data.drive
      } catch (error) {
        console.error('Failed to fetch drive:', error)
        this.$router.push('/student/drives')
      } finally {
        this.loading = false
      }
    },
    
    showApplyModal() {
      this.coverLetter = ''
      this.applyModal.show()
    },
    
    async submitApplication() {
      this.applying = true
      try {
        await studentAPI.applyToDrive(this.id, {
          cover_letter: this.coverLetter
        })
        
        this.applyModal.hide()
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Application submitted successfully!'
        })
        
        // Refresh drive data
        this.fetchDrive()
      } catch (error) {
        const message = error.response?.data?.error || 'Failed to submit application'
        this.$store.dispatch('showNotification', {
          type: 'error',
          message
        })
      } finally {
        this.applying = false
      }
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
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
    }
  },
  
  mounted() {
    this.fetchDrive()
    this.applyModal = new Modal(document.getElementById('applyModal'))
  }
}
</script>