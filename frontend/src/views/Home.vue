<template>
  <div class="home">
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
      <div class="container">
        <a class="navbar-brand fw-bold text-primary" href="#">
          <i class="bi bi-briefcase-fill me-2"></i>Placement Portal
        </a>
        <div class="d-flex gap-2">
          <template v-if="isLoggedIn">
            <router-link :to="dashboardLink" class="btn btn-primary">
              <i class="bi bi-speedometer2 me-1"></i> Dashboard
            </router-link>
            <button @click="logout" class="btn btn-outline-danger">Logout</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn btn-outline-primary">Login</router-link>
            <router-link to="/register" class="btn btn-primary">Register</router-link>
          </template>
        </div>
      </div>
    </nav>
    
    <!-- Hero -->
    <section class="py-5 text-white" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
      <div class="container py-5 text-center">
        <h1 class="display-4 fw-bold mb-3">Find Your Dream Job</h1>
        <p class="lead mb-4">Connect with top companies and kickstart your career</p>
        <router-link to="/register" class="btn btn-light btn-lg px-5">Get Started</router-link>
      </div>
    </section>
    
    <!-- Features -->
    <section class="py-5">
      <div class="container">
        <div class="row g-4 text-center">
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4">
                <i class="bi bi-building fs-1 text-primary mb-3"></i>
                <h5>Top Companies</h5>
                <p class="text-muted">Connect with leading recruiters</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4">
                <i class="bi bi-search fs-1 text-success mb-3"></i>
                <h5>Smart Matching</h5>
                <p class="text-muted">Find jobs that fit your skills</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body p-4">
                <i class="bi bi-graph-up fs-1 text-info mb-3"></i>
                <h5>Track Progress</h5>
                <p class="text-muted">Monitor your applications</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Footer -->
    <footer class="bg-dark text-white py-4 mt-auto">
      <div class="container text-center">
        <p class="mb-0">&copy; 2024 Placement Portal</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  computed: {
    isLoggedIn() {
      return this.$store.getters.isLoggedIn
    },
    dashboardLink() {
      const role = this.$store.getters.userRole
      if (role === 'admin') return '/admin'
      if (role === 'company') return '/company'
      if (role === 'student') return '/student'
      return '/'
    }
  },
  methods: {
    async logout() {
      await this.$store.dispatch('logout')
      this.$router.push('/login')
    }
  },
  mounted() {
    console.log('Home page mounted')
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>