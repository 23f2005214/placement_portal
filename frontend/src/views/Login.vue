<template>
  <div class="login-page min-vh-100 d-flex align-items-center justify-content-center" 
       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-5 col-lg-4">
          
          <!-- Logo -->
          <div class="text-center mb-4">
            <h2 class="text-white fw-bold">
              <i class="bi bi-briefcase-fill me-2"></i>Placement Portal
            </h2>
          </div>
          
          <!-- Login Card -->
          <div class="card shadow border-0">
            <div class="card-body p-4">
              <h4 class="text-center mb-4">Sign In</h4>
              
              <!-- Error -->
              <div class="alert alert-danger py-2" v-if="error">{{ error }}</div>
              
              <!-- Success -->
              <div class="alert alert-success py-2" v-if="success">{{ success }}</div>
              
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" class="form-control" v-model="email" required :disabled="loading">
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Password</label>
                  <input type="password" class="form-control" v-model="password" required :disabled="loading">
                </div>
                
                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                  <span v-if="loading">
                    <span class="spinner-border spinner-border-sm me-1"></span> Loading...
                  </span>
                  <span v-else>Sign In</span>
                </button>
              </form>
              
              <hr>
              
              <p class="text-center mb-0 small">
                Don't have an account? <router-link to="/register">Register</router-link>
              </p>
            </div>
          </div>
          
          <!-- Demo -->
          <div class="card mt-3 border-0 bg-light">
            <div class="card-body py-2 small">
              <strong>Demo:</strong> admin@placement.edu / Admin@123
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
  name: 'LoginPage',
  
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: '',
      success: ''
    }
  },
  
  mounted() {
    // Already logged in? redirect
    const token = localStorage.getItem('access_token')
    if (token) {
      this.redirectToDashboard()
    }
  },
  
  methods: {
    async handleLogin() {
      this.error = ''
      this.success = ''
      this.loading = true
      
      try {
        const response = await axios.post('http://localhost:5000/api/auth/login', {
          email: this.email,
          password: this.password
        })
        
        const { access_token, user, profile } = response.data
        
        if (!access_token) {
          throw new Error('No token received from server')
        }

        // ✅ Persist auth
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('user', JSON.stringify(user))
        localStorage.setItem('profile', JSON.stringify(profile || {}))

        // ✅ Vuex store
        this.$store.commit('SET_AUTH', {
          token: access_token,
          user: user,
          profile: profile
        })
        
        this.success = 'Login successful! Redirecting...'
        
        setTimeout(() => {
          this.redirectToDashboard()
        }, 400)
        
      } catch (err) {
        console.error('Login error:', err)
        this.error = err.response?.data?.error || err.message || 'Login failed'
      } finally {
        this.loading = false
      }
    },
    
    redirectToDashboard() {
      const role = this.$store.getters.userRole || JSON.parse(localStorage.getItem('user'))?.role
      
      if (role === 'admin') {
        this.$router.push('/admin')
      } else if (role === 'company') {
        this.$router.push('/company')
      } else if (role === 'student') {
        this.$router.push('/student')
      } else {
        this.$router.push('/')
      }
    }
  }
}
</script>
