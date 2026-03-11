<template>
  <div class="company-profile">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Company Profile</h4>
        <p class="text-muted mb-0">Manage your company information</p>
      </div>
      <button 
        class="btn btn-primary"
        @click="isEditing = !isEditing"
        v-if="!isEditing"
      >
        <i class="bi bi-pencil me-2"></i>
        Edit Profile
      </button>
    </div>
    
    <!-- Approval Status Banner -->
    <div 
      class="alert mb-4"
      :class="getApprovalAlertClass()"
      v-if="profile"
    >
      <div class="d-flex align-items-center">
        <i :class="getApprovalIcon()" class="fs-4 me-3"></i>
        <div>
          <strong>{{ getApprovalTitle() }}</strong>
          <p class="mb-0 small">{{ getApprovalMessage() }}</p>
        </div>
      </div>
    </div>
    
    <div class="row g-4">
      <!-- Profile Card -->
      <div class="col-lg-4">
        <div class="card">
          <div class="card-body text-center">
            <div class="mb-3">
              <img 
                :src="profile?.logo_url || 'https://via.placeholder.com/120'"
                alt="Company Logo"
                class="rounded-circle"
                width="120"
                height="120"
                style="object-fit: cover;"
              >
            </div>
            <h5 class="mb-1">{{ profile?.company_name }}</h5>
            <p class="text-muted">{{ profile?.industry || 'Industry not specified' }}</p>
            <span class="badge" :class="getTypeBadge(profile?.company_type)">
              {{ profile?.company_type || 'N/A' }}
            </span>
            
            <hr class="my-4">
            
            <div class="text-start">
              <p class="mb-2">
                <i class="bi bi-envelope text-muted me-2"></i>
                {{ user?.email }}
              </p>
              <p class="mb-2" v-if="profile?.website">
                <i class="bi bi-globe text-muted me-2"></i>
                <a :href="profile.website" target="_blank">{{ profile.website }}</a>
              </p>
              <p class="mb-2" v-if="profile?.city">
                <i class="bi bi-geo-alt text-muted me-2"></i>
                {{ [profile.city, profile.state, profile.country].filter(Boolean).join(', ') }}
              </p>
              <p class="mb-0" v-if="profile?.company_size">
                <i class="bi bi-people text-muted me-2"></i>
                {{ profile.company_size }} employees
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Profile Form -->
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">{{ isEditing ? 'Edit Profile' : 'Company Details' }}</h6>
          </div>
          <div class="card-body">
            <form @submit.prevent="saveProfile" v-if="isEditing">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label">Company Name *</label>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="form.company_name"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Industry</label>
                  <select class="form-select" v-model="form.industry">
                    <option value="">Select Industry</option>
                    <option value="IT/Software">IT/Software</option>
                    <option value="Finance">Finance</option>
                    <option value="Consulting">Consulting</option>
                    <option value="Manufacturing">Manufacturing</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="E-commerce">E-commerce</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Company Type</label>
                  <select class="form-select" v-model="form.company_type">
                    <option value="">Select Type</option>
                    <option value="MNC">MNC</option>
                    <option value="Startup">Startup</option>
                    <option value="Private">Private</option>
                    <option value="Government">Government</option>
                    <option value="PSU">PSU</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Company Size</label>
                  <select class="form-select" v-model="form.company_size">
                    <option value="">Select Size</option>
                    <option value="1-10">1-10 employees</option>
                    <option value="11-50">11-50 employees</option>
                    <option value="51-200">51-200 employees</option>
                    <option value="201-500">201-500 employees</option>
                    <option value="500+">500+ employees</option>
                  </select>
                </div>
                <div class="col-12">
                  <label class="form-label">Website</label>
                  <input 
                    type="url" 
                    class="form-control"
                    v-model="form.website"
                    placeholder="https://www.company.com"
                  >
                </div>
                <div class="col-12">
                  <label class="form-label">Company Description</label>
                  <textarea 
                    class="form-control"
                    rows="4"
                    v-model="form.company_description"
                    placeholder="Describe your company..."
                  ></textarea>
                </div>
                
                <div class="col-12">
                  <h6 class="text-muted mt-3 mb-3">HR Contact Information</h6>
                </div>
                <div class="col-md-4">
                  <label class="form-label">HR Name</label>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="form.hr_name"
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">HR Email</label>
                  <input 
                    type="email" 
                    class="form-control"
                    v-model="form.hr_email"
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">HR Phone</label>
                  <input 
                    type="tel" 
                    class="form-control"
                    v-model="form.hr_phone"
                  >
                </div>
                
                <div class="col-12">
                  <h6 class="text-muted mt-3 mb-3">Address</h6>
                </div>
                <div class="col-12">
                  <label class="form-label">Address</label>
                  <textarea 
                    class="form-control"
                    rows="2"
                    v-model="form.address"
                  ></textarea>
                </div>
                <div class="col-md-4">
                  <label class="form-label">City</label>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="form.city"
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">State</label>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="form.state"
                  >
                </div>
                <div class="col-md-4">
                  <label class="form-label">Country</label>
                  <input 
                    type="text" 
                    class="form-control"
                    v-model="form.country"
                  >
                </div>
              </div>
              
              <div class="d-flex justify-content-end gap-3 mt-4">
                <button 
                  type="button" 
                  class="btn btn-outline-secondary"
                  @click="cancelEdit"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="saving"
                >
                  <span v-if="saving">
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Saving...
                  </span>
                  <span v-else>Save Changes</span>
                </button>
              </div>
            </form>
            
            <!-- View Mode -->
            <div v-else>
              <div class="row g-4">
                <div class="col-md-6">
                  <label class="text-muted small">Company Description</label>
                  <p>{{ profile?.company_description || 'No description provided' }}</p>
                </div>
              </div>
              
              <h6 class="text-muted mt-4 mb-3">HR Contact</h6>
              <div class="row g-3">
                <div class="col-md-4">
                  <label class="text-muted small">Name</label>
                  <p class="mb-0">{{ profile?.hr_name || '-' }}</p>
                </div>
                <div class="col-md-4">
                  <label class="text-muted small">Email</label>
                  <p class="mb-0">{{ profile?.hr_email || '-' }}</p>
                </div>
                <div class="col-md-4">
                  <label class="text-muted small">Phone</label>
                  <p class="mb-0">{{ profile?.hr_phone || '-' }}</p>
                </div>
              </div>
              
              <h6 class="text-muted mt-4 mb-3">Address</h6>
              <p>
                {{ profile?.address || '' }}
                {{ [profile?.city, profile?.state, profile?.country].filter(Boolean).join(', ') || 'Not provided' }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { companyAPI } from '../../services/api'

export default {
  name: 'CompanyProfile',
  
  data() {
    return {
      isEditing: false,
      saving: false,
      form: {}
    }
  },
  
  computed: {
    user() {
      return this.$store.state.user
    },
    
    profile() {
      return this.$store.state.profile
    }
  },
  
  methods: {
    initForm() {
      this.form = {
        company_name: this.profile?.company_name || '',
        company_description: this.profile?.company_description || '',
        industry: this.profile?.industry || '',
        company_type: this.profile?.company_type || '',
        company_size: this.profile?.company_size || '',
        website: this.profile?.website || '',
        hr_name: this.profile?.hr_name || '',
        hr_email: this.profile?.hr_email || '',
        hr_phone: this.profile?.hr_phone || '',
        address: this.profile?.address || '',
        city: this.profile?.city || '',
        state: this.profile?.state || '',
        country: this.profile?.country || 'India'
      }
    },
    
    async saveProfile() {
      this.saving = true
      try {
        await companyAPI.updateProfile(this.form)
        await this.$store.dispatch('refreshUserData')
        
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Profile updated successfully'
        })
        
        this.isEditing = false
      } catch (error) {
        console.error('Failed to save profile:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: 'Failed to update profile'
        })
      } finally {
        this.saving = false
      }
    },
    
    cancelEdit() {
      this.initForm()
      this.isEditing = false
    },
    
    getApprovalAlertClass() {
      const status = this.profile?.approval_status
      if (status === 'approved') return 'alert-success'
      if (status === 'rejected') return 'alert-danger'
      return 'alert-warning'
    },
    
    getApprovalIcon() {
      const status = this.profile?.approval_status
      if (status === 'approved') return 'bi bi-check-circle-fill text-success'
      if (status === 'rejected') return 'bi bi-x-circle-fill text-danger'
      return 'bi bi-hourglass-split text-warning'
    },
    
    getApprovalTitle() {
      const status = this.profile?.approval_status
      if (status === 'approved') return 'Approved'
      if (status === 'rejected') return 'Rejected'
      return 'Pending Approval'
    },
    
    getApprovalMessage() {
      const status = this.profile?.approval_status
      if (status === 'approved') return 'Your company is verified and can create placement drives.'
      if (status === 'rejected') return this.profile?.rejection_reason || 'Your registration was rejected. Please contact admin.'
      return 'Your registration is being reviewed by the admin.'
    },
    
    getTypeBadge(type) {
      const badges = {
        'MNC': 'bg-primary',
        'Startup': 'bg-success',
        'Private': 'bg-info',
        'Government': 'bg-warning text-dark',
        'PSU': 'bg-secondary'
      }
      return badges[type] || 'bg-secondary'
    }
  },
  
  mounted() {
    this.initForm()
  },
  
  watch: {
    profile: {
      handler() {
        if (!this.isEditing) {
          this.initForm()
        }
      },
      deep: true
    }
  }
}
</script>