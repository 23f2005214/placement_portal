<template>
  <div class="register-page min-vh-100 py-5" 
       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          
          <div class="text-center mb-4">
            <h2 class="text-white fw-bold">
              <i class="bi bi-briefcase-fill me-2"></i>Placement Portal
            </h2>
          </div>
          
          <div class="card shadow border-0">
            <div class="card-body p-4">
              <h4 class="text-center mb-4">Create Account</h4>
              
              <!-- Role Selection -->
              <div class="btn-group w-100 mb-4">
                <input type="radio" class="btn-check" id="student" value="student" v-model="role">
                <label class="btn btn-outline-primary" for="student">Student</label>
                
                <input type="radio" class="btn-check" id="company" value="company" v-model="role">
                <label class="btn btn-outline-primary" for="company">Company</label>
              </div>
              
              <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
              
              <!-- Student Form -->
              <form v-if="role === 'student'" @submit.prevent="registerStudent">
                <div class="row g-3">
                  <div class="col-6">
                    <input type="text" class="form-control" placeholder="First Name *" v-model="student.first_name" required>
                  </div>
                  <div class="col-6">
                    <input type="text" class="form-control" placeholder="Last Name" v-model="student.last_name">
                  </div>
                  <div class="col-12">
                    <input type="email" class="form-control" placeholder="Email *" v-model="student.email" required>
                  </div>
                  <div class="col-12">
                    <input type="password" class="form-control" placeholder="Password *" v-model="student.password" required minlength="8">
                  </div>
                  <div class="col-6">
                    <select class="form-select" v-model="student.branch" required>
                      <option value="">Branch *</option>
                      <option>Computer Science</option>
                      <option>Information Technology</option>
                      <option>Electronics</option>
                      <option>Mechanical</option>
                    </select>
                  </div>
                  <div class="col-6">
                    <input type="number" class="form-control" placeholder="CGPA *" v-model="student.cgpa" step="0.01" min="0" max="10" required>
                  </div>
                  <div class="col-6">
                    <select class="form-select" v-model="student.year_of_study" required>
                      <option value="">Year *</option>
                      <option value="1">1st Year</option>
                      <option value="2">2nd Year</option>
                      <option value="3">3rd Year</option>
                      <option value="4">4th Year</option>
                    </select>
                  </div>
                  <div class="col-6">
                    <input type="number" class="form-control" placeholder="Graduation Year *" v-model="student.graduation_year" required>
                  </div>
                </div>
                <button type="submit" class="btn btn-primary w-100 mt-4" :disabled="loading">
                  <span v-if="loading"><span class="spinner-border spinner-border-sm"></span></span>
                  <span v-else>Register as Student</span>
                </button>
              </form>
              
              <!-- Company Form -->
              <form v-if="role === 'company'" @submit.prevent="registerCompany">
                <div class="row g-3">
                  <div class="col-12">
                    <input type="text" class="form-control" placeholder="Company Name *" v-model="company.company_name" required>
                  </div>
                  <div class="col-12">
                    <input type="email" class="form-control" placeholder="Email *" v-model="company.email" required>
                  </div>
                  <div class="col-12">
                    <input type="password" class="form-control" placeholder="Password *" v-model="company.password" required minlength="8">
                  </div>
                  <div class="col-12">
                    <select class="form-select" v-model="company.industry">
                      <option value="">Industry</option>
                      <option>IT/Software</option>
                      <option>Finance</option>
                      <option>Consulting</option>
                    </select>
                  </div>
                </div>
                <div class="alert alert-info small mt-3 py-2">
                  Company registration requires admin approval.
                </div>
                <button type="submit" class="btn btn-primary w-100 mt-2" :disabled="loading">
                  <span v-if="loading"><span class="spinner-border spinner-border-sm"></span></span>
                  <span v-else>Register as Company</span>
                </button>
              </form>
              
              <hr>
              <p class="text-center mb-0 small">
                Already have an account? <router-link to="/login">Sign In</router-link>
              </p>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterPage',
  
  data() {
    return {
      role: 'student',
      loading: false,
      error: '',
      student: {
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        branch: '',
        cgpa: '',
        year_of_study: '',
        graduation_year: new Date().getFullYear() + 1
      },
      company: {
        email: '',
        password: '',
        company_name: '',
        industry: ''
      }
    }
  },
  
  methods: {
    async registerStudent() {
      this.error = ''
      this.loading = true
      
      try {
        const response = await axios.post('http://localhost:5000/api/auth/register/student', this.student)
        
        this.$store.commit('SET_AUTH', {
          token: response.data.access_token,
          user: response.data.user,
          profile: response.data.profile
        })
        
        this.$router.push('/student')
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed'
      } finally {
        this.loading = false
      }
    },
    
    async registerCompany() {
      this.error = ''
      this.loading = true
      
      try {
        const response = await axios.post('http://localhost:5000/api/auth/register/company', this.company)
        
        this.$store.commit('SET_AUTH', {
          token: response.data.access_token,
          user: response.data.user,
          profile: response.data.profile
        })
        
        this.$router.push('/company')
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>