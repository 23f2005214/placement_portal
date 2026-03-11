<template>
  <div class="reports-page">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h4 class="mb-1">Reports & Analytics</h4>
        <p class="text-muted mb-0">View placement statistics and generate reports</p>
      </div>
      <div class="d-flex gap-2">
        <select class="form-select" v-model="selectedMonth" style="width: auto;">
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.label }}
          </option>
        </select>
        <button class="btn btn-primary" @click="generateReport">
          <i class="bi bi-file-earmark-text me-2"></i>
          Generate Report
        </button>
      </div>
    </div>
    
    <!-- Stats Overview -->
    <div class="row g-4 mb-4">
      <div class="col-md-3">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h3 class="mb-1">{{ reportData.total_drives || 0 }}</h3>
                <p class="mb-0 opacity-75">Total Drives</p>
              </div>
              <i class="bi bi-briefcase fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-success text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h3 class="mb-1">{{ reportData.total_applications || 0 }}</h3>
                <p class="mb-0 opacity-75">Applications</p>
              </div>
              <i class="bi bi-file-text fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-info text-white">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h3 class="mb-1">{{ reportData.total_selections || 0 }}</h3>
                <p class="mb-0 opacity-75">Selections</p>
              </div>
              <i class="bi bi-trophy fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card bg-warning text-dark">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <h3 class="mb-1">{{ (reportData.placement_rate || 0).toFixed(1) }}%</h3>
                <p class="mb-0 opacity-75">Placement Rate</p>
              </div>
              <i class="bi bi-graph-up fs-1 opacity-25"></i>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Charts Row -->
    <div class="row g-4 mb-4">
      <div class="col-lg-8">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Branch-wise Placement Statistics</h6>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <th>Branch</th>
                    <th>Total Students</th>
                    <th>Placed</th>
                    <th>Rate</th>
                    <th>Progress</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="branch in branchStats" :key="branch.branch">
                    <td>{{ branch.branch }}</td>
                    <td>{{ branch.total_students }}</td>
                    <td>{{ branch.placed_students }}</td>
                    <td>{{ branch.placement_rate.toFixed(1) }}%</td>
                    <td style="width: 200px;">
                      <div class="progress">
                        <div 
                          class="progress-bar"
                          :class="getProgressBarClass(branch.placement_rate)"
                          :style="{ width: branch.placement_rate + '%' }"
                        ></div>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-lg-4">
        <div class="card">
          <div class="card-header">
            <h6 class="mb-0">Top Recruiting Companies</h6>
          </div>
          <div class="card-body p-0">
            <div class="list-group list-group-flush">
              <div 
                class="list-group-item d-flex justify-content-between align-items-center"
                v-for="(company, index) in reportData.top_companies || []"
                :key="index"
              >
                <div>
                  <p class="mb-0 fw-medium">{{ company.name }}</p>
                  <small class="text-muted">{{ company.drives }} drives</small>
                </div>
                <span class="badge bg-primary rounded-pill">
                  {{ company.selections }} hires
                </span>
              </div>
              <div class="list-group-item text-center text-muted" 
                   v-if="!reportData.top_companies || reportData.top_companies.length === 0">
                No data available
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Report Preview -->
    <div class="card" v-if="htmlReport">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">Report Preview</h6>
        <button class="btn btn-sm btn-outline-primary" @click="downloadReport">
          <i class="bi bi-download me-1"></i> Download
        </button>
      </div>
      <div class="card-body">
        <div class="report-preview" v-html="htmlReport"></div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminAPI } from '../../services/api'

export default {
  name: 'ReportsPage',
  
  data() {
    const currentDate = new Date()
    return {
      loading: false,
      selectedMonth: currentDate.getMonth() + 1,
      selectedYear: currentDate.getFullYear(),
      reportData: {},
      branchStats: [],
      htmlReport: null
    }
  },
  
  computed: {
    months() {
      const months = []
      for (let i = 1; i <= 12; i++) {
        const date = new Date(this.selectedYear, i - 1, 1)
        months.push({
          value: i,
          label: date.toLocaleString('default', { month: 'long', year: 'numeric' })
        })
      }
      return months
    }
  },
  
  methods: {
    async generateReport() {
      this.loading = true
      try {
        const response = await adminAPI.getMonthlyReport({
          month: this.selectedMonth,
          year: this.selectedYear
        })
        
        this.reportData = response.data.report_data || {}
        this.htmlReport = response.data.html_report
      } catch (error) {
        console.error('Failed to generate report:', error)
      } finally {
        this.loading = false
      }
    },
    
    async fetchBranchStats() {
      try {
        const response = await adminAPI.getBranchStats()
        this.branchStats = response.data.branches || []
      } catch (error) {
        console.error('Failed to fetch branch stats:', error)
      }
    },
    
    downloadReport() {
      if (!this.htmlReport) return
      
      const blob = new Blob([this.htmlReport], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `placement_report_${this.selectedMonth}_${this.selectedYear}.html`
      a.click()
      URL.revokeObjectURL(url)
    },
    
    getProgressBarClass(rate) {
      if (rate >= 75) return 'bg-success'
      if (rate >= 50) return 'bg-info'
      if (rate >= 25) return 'bg-warning'
      return 'bg-danger'
    }
  },
  
  mounted() {
    this.generateReport()
    this.fetchBranchStats()
  }
}
</script>

<style scoped>
.report-preview {
  max-height: 600px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 20px;
}
</style>