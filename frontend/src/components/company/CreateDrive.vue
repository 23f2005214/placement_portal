<template>
  <div class="create-drive">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Create Placement Drive</h4>
        <p class="text-muted mb-0">Post a new job opportunity for students</p>
      </div>
      <router-link to="/company/drives" class="btn btn-outline-secondary">
        <i class="bi bi-arrow-left me-2"></i>
        Back to Drives
      </router-link>
    </div>
    
    <!-- Not Approved Warning -->
    <div class="alert alert-warning" v-if="!companyApproved">
      <i class="bi bi-exclamation-triangle me-2"></i>
      Your company is not yet approved. You cannot create drives until admin approves your registration.
    </div>
    
    <!-- Create Form -->
    <div class="card" v-if="companyApproved">
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <!-- Basic Information -->
          <h6 class="text-primary mb-3">
            <i class="bi bi-info-circle me-2"></i>
            Basic Information
          </h6>
          
          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <label class="form-label">Job Title *</label>
              <input 
                type="text" 
                class="form-control"
                v-model="form.job_title"
                placeholder="e.g., Software Engineer"
                required
              >
            </div>
            <div class="col-md-3">
              <label class="form-label">Job Type *</label>
              <select class="form-select" v-model="form.job_type" required>
                <option value="Full-time">Full-time</option>
                <option value="Internship">Internship</option>
                <option value="Part-time">Part-time</option>
                <option value="Contract">Contract</option>
              </select>
            </div>
            <div class="col-md-3">
              <label class="form-label">Work Mode</label>
              <select class="form-select" v-model="form.work_mode">
                <option value="On-site">On-site</option>
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
              </select>
            </div>
            <div class="col-12">
              <label class="form-label">Job Description *</label>
              <textarea 
                class="form-control"
                rows="5"
                v-model="form.job_description"
                placeholder="Describe the role, responsibilities, and requirements..."
                required
              ></textarea>
            </div>
            <div class="col-md-6">
              <label class="form-label">Job Location</label>
              <input 
                type="text" 
                class="form-control"
                v-model="form.job_location"
                placeholder="e.g., Bangalore, India"
              >
            </div>
            <div class="col-md-6">
              <label class="form-label">Number of Positions</label>
              <input 
                type="number" 
                class="form-control"
                v-model="form.number_of_positions"
                min="1"
                placeholder="1"
              >
            </div>
          </div>
          
          <!-- Compensation -->
          <h6 class="text-primary mb-3">
            <i class="bi bi-currency-rupee me-2"></i>
            Compensation
          </h6>
          
          <div class="row g-3 mb-4">
            <div class="col-md-4">
              <label class="form-label">Minimum Salary (LPA)</label>
              <input 
                type="number" 
                class="form-control"
                v-model="form.salary_min"
                step="0.5"
                min="0"
                placeholder="e.g., 6"
              >
            </div>
            <div class="col-md-4">
              <label class="form-label">Maximum Salary (LPA)</label>
              <input 
                type="number" 
                class="form-control"
                v-model="form.salary_max"
                step="0.5"
                min="0"
                placeholder="e.g., 12"
              >
            </div>
            <div class="col-md-4">
              <label class="form-label">Salary Period</label>
              <select class="form-select" v-model="form.salary_period">
                <option value="per annum">Per Annum</option>
                <option value="per month">Per Month</option>
              </select>
            </div>
          </div>
          
          <!-- Eligibility Criteria -->
          <h6 class="text-primary mb-3">
            <i class="bi bi-check2-square me-2"></i>
            Eligibility Criteria
          </h6>
          
          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <label class="form-label">Eligible Branches</label>
              <div class="border rounded p-3" style="max-height: 200px; overflow-y: auto;">
                <div class="form-check" v-for="branch in branches" :key="branch">
                  <input 
                    type="checkbox" 
                    class="form-check-input"
                    :id="'branch-' + branch"
                    :value="branch"
                    v-model="selectedBranches"
                  >
                  <label class="form-check-label" :for="'branch-' + branch">
                    {{ branch }}
                  </label>
                </div>
              </div>
              <small class="text-muted">Leave empty for all branches</small>
            </div>
            <div class="col-md-6">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Minimum CGPA</label>
                  <input 
                    type="number" 
                    class="form-control"
                    v-model="form.min_cgpa"
                    step="0.1"
                    min="0"
                    max="10"
                    placeholder="e.g., 7.0"
                  >
                </div>
                <div class="col-12">
                  <label class="form-label">Maximum Active Backlogs</label>
                  <input 
                    type="number" 
                    class="form-control"
                    v-model="form.max_backlogs"
                    min="0"
                    placeholder="e.g., 0"
                  >
                </div>
                <div class="col-12">
                  <label class="form-label">Eligible Graduation Years</label>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="form.eligible_graduation_years"
                    placeholder="e.g., 2024, 2025"
                  >
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <label class="form-label">Minimum 10th %</label>
              <input 
                type="number" 
                class="form-control"
                v-model="form.min_tenth_percentage"
                step="0.1"
                min="0"
                max="100"
                placeholder="e.g., 60"
              >
            </div>
            <div class="col-md-6">
              <label class="form-label">Minimum 12th %</label>
              <input 
                type="number" 
                class="form-control"
                v-model="form.min_twelfth_percentage"
                step="0.1"
                min="0"
                max="100"
                placeholder="e.g., 60"
              >
            </div>
            <div class="col-12">
              <label class="form-label">Required Skills</label>
              <input 
                type="text" 
                class="form-control"
                v-model="form.required_skills"
                placeholder="e.g., Python, JavaScript, SQL (comma-separated)"
              >
            </div>
          </div>
          
          <!-- Drive Details -->
          <h6 class="text-primary mb-3">
            <i class="bi bi-calendar-event me-2"></i>
            Drive Details
          </h6>
          
          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <label class="form-label">Application Deadline *</label>
              <input 
                type="datetime-local" 
                class="form-control"
                v-model="form.application_deadline"
                :min="minDateTime"
                required
              >
            </div>
            <div class="col-md-6">
              <label class="form-label">Drive Date</label>
              <input 
                type="datetime-local" 
                class="form-control"
                v-model="form.drive_date"
              >
            </div>
            <div class="col-md-6">
              <label class="form-label">Drive Venue</label>
              <input 
                type="text" 
                class="form-control"
                v-model="form.drive_venue"
                placeholder="e.g., Campus Auditorium"
              >
            </div>
            <div class="col-md-6">
              <label class="form-label">Number of Rounds</label>
              <input 
                type="number" 
                class="form-control"
                v-model="form.number_of_rounds"
                min="1"
                placeholder="e.g., 3"
              >
            </div>
            <div class="col-12">
              <label class="form-label">Selection Process</label>
              <textarea 
                class="form-control"
                rows="3"
                v-model="form.selection_process"
                placeholder="Describe the selection process (e.g., Online Test → Technical Interview → HR Interview)"
              ></textarea>
            </div>
          </div>
          
          <!-- Submit -->
          <div class="d-flex justify-content-end gap-3">
            <router-link to="/company/drives" class="btn btn-outline-secondary">
              Cancel
            </router-link>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="submitting"
            >
              <span v-if="submitting">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Creating...
              </span>
              <span v-else>
                <i class="bi bi-plus-lg me-2"></i>
                Create Drive
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { companyAPI } from '../../services/api'

export default {
  name: 'CreateDrive',
  
  data() {
    return {
      submitting: false,
      selectedBranches: [],
      form: {
        job_title: '',
        job_description: '',
        job_type: 'Full-time',
        job_location: '',
        work_mode: 'On-site',
        salary_min: null,
        salary_max: null,
        salary_period: 'per annum',
        number_of_positions: 1,
        min_cgpa: null,
        max_backlogs: null,
        eligible_graduation_years: '',
        min_tenth_percentage: null,
        min_twelfth_percentage: null,
        required_skills: '',
        application_deadline: '',
        drive_date: '',
        drive_venue: '',
        selection_process: '',
        number_of_rounds: null
      }
    }
  },
  
  computed: {
    companyApproved() {
      return this.$store.getters.companyApproved
    },
    
    branches() {
      return this.$store.state.branches
    },
    
    minDateTime() {
      const now = new Date()
      now.setMinutes(now.getMinutes() + 60) // At least 1 hour from now
      return now.toISOString().slice(0, 16)
    }
  },
  
  methods: {
    async handleSubmit() {
      this.submitting = true
      
      try {
        // Prepare data
        const data = {
          ...this.form,
          eligible_branches: this.selectedBranches.join(', '),
          salary_min: this.form.salary_min ? this.form.salary_min * 100000 : null, // Convert LPA to actual
          salary_max: this.form.salary_max ? this.form.salary_max * 100000 : null
        }
        
        // Remove empty values
        Object.keys(data).forEach(key => {
          if (data[key] === '' || data[key] === null) {
            delete data[key]
          }
        })
        
        const response = await companyAPI.createDrive(data)
        
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Drive created successfully! Awaiting admin approval.'
        })
        
        this.$router.push('/company/drives')
      } catch (error) {
        console.error('Failed to create drive:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: error.response?.data?.error || 'Failed to create drive'
        })
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>