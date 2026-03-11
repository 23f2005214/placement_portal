<template>
  <div class="student-management">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Student Management</h4>
        <p class="text-muted mb-0">View and manage registered students</p>
      </div>
      <button class="btn btn-outline-primary" @click="exportStudents">
        <i class="bi bi-download me-2"></i>
        Export CSV
      </button>
    </div>
    
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <input 
              type="text" 
              class="form-control"
              placeholder="Search students..."
              v-model="filters.search"
              @input="debouncedFetch"
            >
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.branch" @change="fetchStudents">
              <option value="">All Branches</option>
              <option v-for="branch in branches" :key="branch" :value="branch">
                {{ branch }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.graduation_year" @change="fetchStudents">
              <option value="">All Years</option>
              <option v-for="year in graduationYears" :key="year" :value="year">
                {{ year }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <select class="form-select" v-model="filters.is_placed" @change="fetchStudents">
              <option value="">All Status</option>
              <option value="true">Placed</option>
              <option value="false">Not Placed</option>
            </select>
          </div>
          <div class="col-md-3">
            <button class="btn btn-outline-secondary" @click="resetFilters">
              <i class="bi bi-x-circle me-1"></i> Reset Filters
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Students Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th>Student</th>
                <th>Roll Number</th>
                <th>Branch</th>
                <th>Year</th>
                <th>CGPA</th>
                <th>Status</th>
                <th>Applications</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="8" class="text-center py-5">
                  <div class="spinner-border text-primary"></div>
                </td>
              </tr>
              <tr v-else-if="students.length === 0">
                <td colspan="8" class="text-center py-5">
                  <i class="bi bi-people fs-1 text-muted"></i>
                  <p class="text-muted mt-2 mb-0">No students found</p>
                </td>
              </tr>
              <tr v-else v-for="student in students" :key="student.id">
                <td>
                  <div class="d-flex align-items-center">
                    <div class="avatar-sm bg-primary text-white rounded-circle me-2">
                      {{ getInitials(student.full_name) }}
                    </div>
                    <div>
                      <p class="mb-0 fw-medium">{{ student.full_name }}</p>
                      <small class="text-muted">{{ student.email }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ student.roll_number || '-' }}</td>
                <td>{{ student.branch }}</td>
                <td>{{ student.graduation_year }}</td>
                <td>
                  <span :class="getCgpaBadge(student.cgpa)">
                    {{ student.cgpa?.toFixed(2) }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="student.is_placed ? 'bg-success' : 'bg-secondary'">
                    {{ student.is_placed ? 'Placed' : 'Not Placed' }}
                  </span>
                  <span class="badge bg-danger ms-1" v-if="student.is_blacklisted">
                    Blacklisted
                  </span>
                </td>
                <td>{{ student.applications?.length || 0 }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      class="btn btn-outline-primary"
                      @click="viewStudent(student)"
                      title="View Details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button 
                      class="btn btn-outline-warning"
                      @click="toggleBlacklist(student)"
                      :title="student.is_blacklisted ? 'Remove Blacklist' : 'Blacklist'"
                    >
                      <i class="bi bi-slash-circle"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Pagination -->
      <div class="card-footer bg-white" v-if="pagination.pages > 1">
        <nav class="d-flex justify-content-between align-items-center">
          <span class="text-muted small">
            Showing {{ (pagination.page - 1) * pagination.per_page + 1 }} 
            to {{ Math.min(pagination.page * pagination.per_page, pagination.total) }}
            of {{ pagination.total }} students
          </span>
          <ul class="pagination pagination-sm mb-0">
            <li class="page-item" :class="{ disabled: !pagination.has_prev }">
              <a class="page-link" href="#" @click.prevent="goToPage(pagination.page - 1)">
                Previous
              </a>
            </li>
            <li 
              class="page-item" 
              v-for="page in visiblePages" 
              :key="page"
              :class="{ active: page === pagination.page }"
            >
              <a class="page-link" href="#" @click.prevent="goToPage(page)">
                {{ page }}
              </a>
            </li>
            <li class="page-item" :class="{ disabled: !pagination.has_next }">
              <a class="page-link" href="#" @click.prevent="goToPage(pagination.page + 1)">
                Next
              </a>
            </li>
          </ul>
        </nav>
      </div>
    </div>
    
    <!-- Student Details Modal -->
    <div class="modal fade" id="studentModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Student Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedStudent">
            <div class="row">
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Personal Information</h6>
                <table class="table table-sm">
                  <tr>
                    <td class="text-muted">Full Name</td>
                    <td class="fw-medium">{{ selectedStudent.full_name }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Email</td>
                    <td>{{ selectedStudent.email }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Phone</td>
                    <td>{{ selectedStudent.phone || '-' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Roll Number</td>
                    <td>{{ selectedStudent.roll_number || '-' }}</td>
                  </tr>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Academic Information</h6>
                <table class="table table-sm">
                  <tr>
                    <td class="text-muted">Branch</td>
                    <td>{{ selectedStudent.branch }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Graduation Year</td>
                    <td>{{ selectedStudent.graduation_year }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">CGPA</td>
                    <td>{{ selectedStudent.cgpa?.toFixed(2) }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Active Backlogs</td>
                    <td>{{ selectedStudent.active_backlogs }}</td>
                  </tr>
                </table>
              </div>
            </div>
            
            <!-- Application Stats -->
            <div class="mt-3" v-if="studentStats">
              <h6 class="text-muted mb-3">Application Statistics</h6>
              <div class="row g-3">
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0">{{ studentStats.total_applications }}</h4>
                    <small class="text-muted">Total</small>
                  </div>
                </div>
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0 text-success">{{ studentStats.selected }}</h4>
                    <small class="text-muted">Selected</small>
                  </div>
                </div>
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0 text-danger">{{ studentStats.rejected }}</h4>
                    <small class="text-muted">Rejected</small>
                  </div>
                </div>
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0 text-warning">{{ studentStats.pending }}</h4>
                    <small class="text-muted">Pending</small>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Skills -->
            <div class="mt-3" v-if="selectedStudent.skills && selectedStudent.skills.length">
              <h6 class="text-muted mb-2">Skills</h6>
              <div class="d-flex flex-wrap gap-2">
                <span 
                  class="badge bg-light text-dark"
                  v-for="skill in selectedStudent.skills"
                  :key="skill"
                >
                  {{ skill }}
                </span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '../../services/api'
import { Modal } from 'bootstrap'

export default {
  name: 'StudentManagement',
  
  data() {
    return {
      loading: true,
      students: [],
      pagination: {
        page: 1,
        per_page: 10,
        total: 0,
        pages: 1,
        has_next: false,
        has_prev: false
      },
      filters: {
        search: '',
        branch: '',
        graduation_year: '',
        is_placed: ''
      },
      selectedStudent: null,
      studentStats: null,
      studentModal: null,
      searchTimeout: null
    }
  },
  
  computed: {
    branches() {
      return this.$store.state.branches
    },
    
    graduationYears() {
      const currentYear = new Date().getFullYear()
      return [currentYear, currentYear + 1, currentYear + 2, currentYear + 3]
    },
    
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.pagination.page - 2)
      const end = Math.min(this.pagination.pages, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    }
  },
  
  methods: {
    async fetchStudents() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          search: this.filters.search,
          branch: this.filters.branch,
          graduation_year: this.filters.graduation_year,
          is_placed: this.filters.is_placed
        }
        
        const response = await adminAPI.getStudents(params)
        this.students = response.data.students || []
        this.pagination = response.data.pagination || this.pagination
      } catch (error) {
        console.error('Failed to fetch students:', error)
      } finally {
        this.loading = false
      }
    },
    
    debouncedFetch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.pagination.page = 1
        this.fetchStudents()
      }, 300)
    },
    
    resetFilters() {
      this.filters = {
        search: '',
        branch: '',
        graduation_year: '',
        is_placed: ''
      }
      this.pagination.page = 1
      this.fetchStudents()
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.pagination.page = page
        this.fetchStudents()
      }
    },
    
    async viewStudent(student) {
      this.selectedStudent = student
      this.studentStats = null
      
      try {
        const response = await adminAPI.getStudent(student.id)
        this.studentStats = response.data.stats
      } catch (error) {
        console.error('Failed to fetch student details:', error)
      }
      
      this.studentModal.show()
    },
    
    async toggleBlacklist(student) {
      const action = student.is_blacklisted ? 'remove from blacklist' : 'blacklist'
      if (!confirm(`Are you sure you want to ${action} ${student.full_name}?`)) return
      
      try {
        await adminAPI.toggleStudentBlacklist(student.id)
        this.fetchStudents()
      } catch (error) {
        console.error('Failed to toggle blacklist:', error)
      }
    },
    
    exportStudents() {
      // Implement CSV export
      alert('Export functionality will be implemented')
    },
    
    getInitials(name) {
      if (!name) return 'U'
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    },
    
    getCgpaBadge(cgpa) {
      if (cgpa >= 8.5) return 'badge bg-success'
      if (cgpa >= 7) return 'badge bg-primary'
      if (cgpa >= 6) return 'badge bg-warning'
      return 'badge bg-danger'
    }
  },
  
  mounted() {
    this.fetchStudents()
    this.studentModal = new Modal(document.getElementById('studentModal'))
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