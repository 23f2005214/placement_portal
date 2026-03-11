<template>
  <div class="student-profile">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">My Profile</h4>
        <p class="text-muted mb-0">Manage your personal and academic information</p>
      </div>
      <span class="badge bg-success" v-if="profile?.is_placed">
        <i class="bi bi-trophy me-1"></i> Placed
      </span>
    </div>
    
    <div class="row">
      <div class="col-lg-8">
        <form @submit.prevent="updateProfile">
          <!-- Personal Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0">Personal Information</h6>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">First Name *</label>
                  <input type="text" class="form-control" v-model="form.first_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Last Name</label>
                  <input type="text" class="form-control" v-model="form.last_name">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Phone</label>
                  <input type="tel" class="form-control" v-model="form.phone">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Gender</label>
                  <select class="form-select" v-model="form.gender">
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Date of Birth</label>
                  <input type="date" class="form-control" v-model="form.date_of_birth">
                </div>
              </div>
            </div>
          </div>
          
          <!-- Academic Information -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0">Academic Information</h6>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Roll Number</label>
                  <input type="text" class="form-control" v-model="form.roll_number">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Branch *</label>
                  <select class="form-select" v-model="form.branch" required>
                    <option v-for="branch in branches" :key="branch" :value="branch">
                      {{ branch }}
                    </option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Year of Study *</label>
                  <select class="form-select" v-model="form.year_of_study" required>
                    <option value="1">1st Year</option>
                    <option value="2">2nd Year</option>
                    <option value="3">3rd Year</option>
                    <option value="4">4th Year</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label">Graduation Year *</label>
                  <input type="number" class="form-control" v-model="form.graduation_year" required>
                </div>
                <div class="col-md-4">
                  <label class="form-label">CGPA *</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="form.cgpa" 
                    step="0.01" 
                    min="0" 
                    max="10"
                    required
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">10th Percentage</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="form.tenth_percentage"
                    step="0.01"
                    min="0"
                    max="100"
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">12th Percentage</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="form.twelfth_percentage"
                    step="0.01"
                    min="0"
                    max="100"
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">Active Backlogs</label>
                  <input type="number" class="form-control" v-model="form.active_backlogs" min="0">
                </div>
              </div>
            </div>
          </div>
          
          <!-- Skills & Resume -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0">Skills & Resume</h6>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Skills</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="form.skills"
                    placeholder="e.g., Python, JavaScript, Machine Learning (comma-separated)"
                  >
                  <small class="text-muted">Separate skills with commas</small>
                </div>
                <div class="col-12">
                  <label class="form-label">Resume URL</label>
                  <input 
                    type="url" 
                    class="form-control" 
                    v-model="form.resume_url"
                    placeholder="https://drive.google.com/..."
                  >
                  <small class="text-muted">Upload your resume to Google Drive/Dropbox and paste the link</small>
                </div>
                <div class="col-md-4">
                  <label class="form-label">LinkedIn</label>
                  <input type="url" class="form-control" v-model="form.linkedin_url">
                </div>
                <div class="col-md-4">
                  <label class="form-label">GitHub</label>
                  <input type="url" class="form-control" v-model="form.github_url">
                </div>
                <div class="col-md-4">
                  <label class="form-label">Portfolio</label>
                  <input type="url" class="form-control" v-model="form.portfolio_url">
                </div>
              </div>
            </div>
          </div>
          
          <!-- Address -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0">Address</h6>
            </div>
            <div class="card-body">
              <div class="row g-3">
                <div class="col-12">
                  <label class="form-label">Address</label>
                  <textarea class="form-control" v-model="form.address" rows="2"></textarea>
                </div>
                <div class="col-md-6">
                  <label class="form-label">City</label>
                  <input type="text" class="form-control" v-model="form.city">
                </div>
                <div class="col-md-6">
                  <label class="form-label">State</label>
                  <input type="text" class="form-control" v-model="form.state">
                </div>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-end">
            <button type="submit" class="btn btn-primary" :disabled="saving">
              <span v-if="saving">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Saving...
              </span>
              <span v-else>
                <i class="bi bi-check-lg me-2"></i>
                Save Changes
              </span>
            </button>
          </div>
        </form>
      </div>
      
      <div class="col-lg-4">
        <!-- Profile Card -->
        <div class="card mb-4">
          <div class="card-body text-center">
            <div class="mb-3">
              <div 
                class="avatar-lg bg-primary text-white rounded-circle mx-auto d-flex align-items-center justify-content-center"
                style="width: 100px; height: 100px; font-size: 36px;"
              >
                {{ getInitials(form.first_name, form.last_name) }}
              </div>
            </div>
            <h5 class="mb-1">{{ form.first_name }} {{ form.last_name }}</h5>
            <p class="text-muted">{{ profile?.email }}</p>
            <div class="d-flex justify-content-center gap-2">
              <span class="badge bg-primary">{{ form.branch }}</span>
              <span class="badge bg-secondary">{{ form.graduation_year }}</span>
            </div>
          </div>
        </div>
        
        <!-- Stats Card -->
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Quick Stats</h6>
          </div>
          <div class="card-body">
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">CGPA</span>
              <span class="fw-bold">{{ form.cgpa }}</span>
            </div>
            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">Active Backlogs</span>
              <span class="fw-bold">{{ form.active_backlogs || 0 }}</span>
            </div>
            <div class="d-flex justify-content-between">
              <span class="text-muted">Placement Count</span>
              <span class="fw-bold">{{ profile?.placement_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { studentAPI } from '../../services/api'

export default {
  name: 'StudentProfile',
  
  data() {
    return {
      saving: false,
      form: {
        first_name: '',
        last_name: '',
        phone: '',
        gender: '',
        date_of_birth: '',
        roll_number: '',
        branch: '',
        year_of_study: 1,
        graduation_year: new Date().getFullYear() + 1,
        cgpa: 0,
        tenth_percentage: null,
        twelfth_percentage: null,
        active_backlogs: 0,
        skills: '',
        resume_url: '',
        linkedin_url: '',
        github_url: '',
        portfolio_url: '',
        address: '',
        city: '',
        state: ''
      }
    }
  },
  
  computed: {
    profile() {
      return this.$store.state.profile
    },
    
    branches() {
      return this.$store.state.branches
    }
  },
  
  methods: {
    loadProfile() {
      if (this.profile) {
        this.form = {
          first_name: this.profile.first_name || '',
          last_name: this.profile.last_name || '',
          phone: this.profile.phone || '',
          gender: this.profile.gender || '',
          date_of_birth: this.profile.date_of_birth || '',
          roll_number: this.profile.roll_number || '',
          branch: this.profile.branch || '',
          year_of_study: this.profile.year_of_study || 1,
          graduation_year: this.profile.graduation_year || new Date().getFullYear() + 1,
          cgpa: this.profile.cgpa || 0,
          tenth_percentage: this.profile.tenth_percentage,
          twelfth_percentage: this.profile.twelfth_percentage,
          active_backlogs: this.profile.active_backlogs || 0,
          skills: Array.isArray(this.profile.skills) ? this.profile.skills.join(', ') : this.profile.skills || '',
          resume_url: this.profile.resume_url || '',
          linkedin_url: this.profile.linkedin_url || '',
          github_url: this.profile.github_url || '',
          portfolio_url: this.profile.portfolio_url || '',
          address: this.profile.address || '',
          city: this.profile.city || '',
          state: this.profile.state || ''
        }
      }
    },
    
    async updateProfile() {
      this.saving = true
      try {
        await studentAPI.updateProfile(this.form)
        await this.$store.dispatch('refreshUserData')
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Profile updated successfully'
        })
      } catch (error) {
        console.error('Failed to update profile:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: 'Failed to update profile'
        })
      } finally {
        this.saving = false
      }
    },
    
    getInitials(firstName, lastName) {
      const f = firstName ? firstName[0] : ''
      const l = lastName ? lastName[0] : ''
      return (f + l).toUpperCase() || 'U'
    }
  },
  
  mounted() {
    this.loadProfile()
  },
  
  watch: {
    profile() {
      this.loadProfile()
    }
  }
}
</script>