<template>
  <div class="company-management">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Company Management</h4>
        <p class="text-muted mb-0">Manage company registrations and approvals</p>
      </div>
    </div>
    
    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <div class="input-group">
              <span class="input-group-text bg-white">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input 
                type="text" 
                class="form-control"
                placeholder="Search companies..."
                v-model="filters.search"
                @input="debouncedFetch"
              >
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filters.status" @change="fetchCompanies">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="filters.sort" @change="fetchCompanies">
              <option value="created_at">Sort by Date</option>
              <option value="company_name">Sort by Name</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="resetFilters">
              <i class="bi bi-x-circle me-1"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Companies Table -->
    <div class="card">
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="bg-light">
              <tr>
                <th>Company</th>
                <th>Industry</th>
                <th>Type</th>
                <th>HR Contact</th>
                <th>Status</th>
                <th>Registered</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center py-5">
                  <div class="spinner-border text-primary"></div>
                  <p class="text-muted mt-2 mb-0">Loading companies...</p>
                </td>
              </tr>
              <tr v-else-if="companies.length === 0">
                <td colspan="7" class="text-center py-5">
                  <i class="bi bi-building fs-1 text-muted"></i>
                  <p class="text-muted mt-2 mb-0">No companies found</p>
                </td>
              </tr>
              <tr v-else v-for="company in companies" :key="company.id">
                <td>
                  <div class="d-flex align-items-center">
                    <div class="company-logo me-3">
                      <img 
                        :src="company.logo_url || 'https://via.placeholder.com/40'"
                        :alt="company.company_name"
                        class="rounded"
                      >
                    </div>
                    <div>
                      <p class="mb-0 fw-medium">{{ company.company_name }}</p>
                      <small class="text-muted">{{ company.email }}</small>
                    </div>
                  </div>
                </td>
                <td>{{ company.industry || '-' }}</td>
                <td>{{ company.company_type || '-' }}</td>
                <td>
                  <span v-if="company.hr_name">{{ company.hr_name }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>
                  <span class="badge" :class="getStatusBadge(company.approval_status)">
                    {{ company.approval_status }}
                  </span>
                  <span class="badge bg-danger ms-1" v-if="company.is_blacklisted">
                    Blacklisted
                  </span>
                </td>
                <td>{{ formatDate(company.created_at) }}</td>
                <td>
                  <div class="dropdown">
                    <button 
                      class="btn btn-sm btn-outline-secondary"
                      data-bs-toggle="dropdown"
                    >
                      <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-end">
                      <li>
                        <a 
                          class="dropdown-item" 
                          href="#"
                          @click.prevent="viewCompany(company)"
                        >
                          <i class="bi bi-eye me-2"></i> View Details
                        </a>
                      </li>
                      <li v-if="company.approval_status === 'pending'">
                        <a 
                          class="dropdown-item text-success" 
                          href="#"
                          @click.prevent="approveCompany(company)"
                        >
                          <i class="bi bi-check-circle me-2"></i> Approve
                        </a>
                      </li>
                      <li v-if="company.approval_status === 'pending'">
                        <a 
                          class="dropdown-item text-danger" 
                          href="#"
                          @click.prevent="showRejectModal(company)"
                        >
                          <i class="bi bi-x-circle me-2"></i> Reject
                        </a>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <a 
                          class="dropdown-item" 
                          href="#"
                          @click.prevent="toggleBlacklist(company)"
                        >
                          <i class="bi bi-slash-circle me-2"></i>
                          {{ company.is_blacklisted ? 'Remove Blacklist' : 'Blacklist' }}
                        </a>
                      </li>
                      <li>
                        <a 
                          class="dropdown-item" 
                          href="#"
                          @click.prevent="toggleStatus(company)"
                        >
                          <i class="bi bi-toggle-on me-2"></i>
                          {{ company.is_active ? 'Deactivate' : 'Activate' }}
                        </a>
                      </li>
                    </ul>
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
            of {{ pagination.total }} companies
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
    
    <!-- Reject Modal -->
    <div class="modal fade" id="rejectModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reject Company</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to reject <strong>{{ selectedCompany?.company_name }}</strong>?</p>
            <div class="mb-3">
              <label class="form-label">Rejection Reason</label>
              <textarea 
                class="form-control" 
                rows="3"
                v-model="rejectReason"
                placeholder="Provide a reason for rejection..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger"
              @click="confirmReject"
              :disabled="processing"
            >
              <span v-if="processing" class="spinner-border spinner-border-sm me-1"></span>
              Reject Company
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Company Details Modal -->
    <div class="modal fade" id="companyModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Company Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body" v-if="selectedCompany">
            <div class="row">
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Basic Information</h6>
                <table class="table table-sm">
                  <tr>
                    <td class="text-muted">Company Name</td>
                    <td class="fw-medium">{{ selectedCompany.company_name }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Email</td>
                    <td>{{ selectedCompany.email }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Industry</td>
                    <td>{{ selectedCompany.industry || '-' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Type</td>
                    <td>{{ selectedCompany.company_type || '-' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Website</td>
                    <td>
                      <a :href="selectedCompany.website" target="_blank" v-if="selectedCompany.website">
                        {{ selectedCompany.website }}
                      </a>
                      <span v-else>-</span>
                    </td>
                  </tr>
                </table>
              </div>
              <div class="col-md-6">
                <h6 class="text-muted mb-3">Contact Information</h6>
                <table class="table table-sm">
                  <tr>
                    <td class="text-muted">HR Name</td>
                    <td>{{ selectedCompany.hr_name || '-' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">HR Email</td>
                    <td>{{ selectedCompany.hr_email || '-' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">HR Phone</td>
                    <td>{{ selectedCompany.hr_phone || '-' }}</td>
                  </tr>
                  <tr>
                    <td class="text-muted">Location</td>
                    <td>
                      {{ [selectedCompany.city, selectedCompany.state].filter(Boolean).join(', ') || '-' }}
                    </td>
                  </tr>
                </table>
              </div>
            </div>
            <div class="mt-3" v-if="selectedCompany.company_description">
              <h6 class="text-muted mb-2">Description</h6>
              <p class="mb-0">{{ selectedCompany.company_description }}</p>
            </div>
            <div class="mt-3" v-if="companyStats">
              <h6 class="text-muted mb-2">Statistics</h6>
              <div class="row g-3">
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0">{{ companyStats.total_drives }}</h4>
                    <small class="text-muted">Total Drives</small>
                  </div>
                </div>
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0">{{ companyStats.approved_drives }}</h4>
                    <small class="text-muted">Approved</small>
                  </div>
                </div>
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0">{{ companyStats.total_applications }}</h4>
                    <small class="text-muted">Applications</small>
                  </div>
                </div>
                <div class="col-3">
                  <div class="text-center p-3 bg-light rounded">
                    <h4 class="mb-0">{{ companyStats.total_selections }}</h4>
                    <small class="text-muted">Selections</small>
                  </div>
                </div>
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
  name: 'CompanyManagement',
  
  data() {
    return {
      loading: true,
      processing: false,
      companies: [],
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
        status: '',
        sort: 'created_at'
      },
      selectedCompany: null,
      companyStats: null,
      rejectReason: '',
      rejectModal: null,
      companyModal: null,
      searchTimeout: null
    }
  },
  
  computed: {
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
    async fetchCompanies() {
      this.loading = true
      try {
        const params = {
          page: this.pagination.page,
          per_page: this.pagination.per_page,
          search: this.filters.search,
          status: this.filters.status,
          sort: this.filters.sort,
          order: 'desc'
        }
        
        const response = await adminAPI.getCompanies(params)
        this.companies = response.companies || []
        this.pagination = response.pagination || this.pagination
      } catch (error) {
        console.error('Failed to fetch companies:', error)
      } finally {
        this.loading = false
      }
    },
    
    debouncedFetch() {
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.pagination.page = 1
        this.fetchCompanies()
      }, 300)
    },
    
    resetFilters() {
      this.filters = {
        search: '',
        status: '',
        sort: 'created_at'
      }
      this.pagination.page = 1
      this.fetchCompanies()
    },
    
    goToPage(page) {
      if (page >= 1 && page <= this.pagination.pages) {
        this.pagination.page = page
        this.fetchCompanies()
      }
    },
    
    async viewCompany(company) {
      this.selectedCompany = company
      this.companyStats = null
      
      try {
        const response = await adminAPI.getCompany(company.id)
        this.companyStats = response.stats
      } catch (error) {
        console.error('Failed to fetch company details:', error)
      }
      
      this.companyModal.show()
    },
    
    async approveCompany(company) {
      if (!confirm(`Approve ${company.company_name}?`)) return
      
      try {
        await adminAPI.approveCompany(company.id)
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Company approved successfully'
        })
        this.fetchCompanies()
      } catch (error) {
        console.error('Failed to approve company:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: 'Failed to approve company'
        })
      }
    },
    
    showRejectModal(company) {
      this.selectedCompany = company
      this.rejectReason = ''
      this.rejectModal.show()
    },
    
    async confirmReject() {
      this.processing = true
      try {
        await adminAPI.rejectCompany(this.selectedCompany.id, this.rejectReason)
        this.rejectModal.hide()
        this.$store.dispatch('showNotification', {
          type: 'success',
          message: 'Company rejected'
        })
        this.fetchCompanies()
      } catch (error) {
        console.error('Failed to reject company:', error)
        this.$store.dispatch('showNotification', {
          type: 'error',
          message: 'Failed to reject company'
        })
      } finally {
        this.processing = false
      }
    },
    
    async toggleBlacklist(company) {
      const action = company.is_blacklisted ? 'remove from blacklist' : 'blacklist'
      if (!confirm(`Are you sure you want to ${action} ${company.company_name}?`)) return
      
      try {
        await adminAPI.toggleCompanyBlacklist(company.id)
        this.fetchCompanies()
      } catch (error) {
        console.error('Failed to toggle blacklist:', error)
      }
    },
    
    async toggleStatus(company) {
      const action = company.is_active ? 'deactivate' : 'activate'
      if (!confirm(`Are you sure you want to ${action} ${company.company_name}?`)) return
      
      try {
        await adminAPI.toggleCompanyStatus(company.id)
        this.fetchCompanies()
      } catch (error) {
        console.error('Failed to toggle status:', error)
      }
    },
    
    getStatusBadge(status) {
      const badges = {
        pending: 'bg-warning',
        approved: 'bg-success',
        rejected: 'bg-danger'
      }
      return badges[status] || 'bg-secondary'
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '-'
      return new Date(dateStr).toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      })
    }
  },
  
  mounted() {
    this.fetchCompanies()
    
    // Initialize modals
    this.rejectModal = new Modal(document.getElementById('rejectModal'))
    this.companyModal = new Modal(document.getElementById('companyModal'))
  }
}
</script>

<style scoped>
.company-logo img {
  width: 40px;
  height: 40px;
  object-fit: cover;
}
</style>