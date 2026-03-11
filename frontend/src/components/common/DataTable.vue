<template>
  <div class="data-table-wrapper">
    <!-- Table Header -->
    <div class="d-flex justify-content-between align-items-center mb-3" v-if="showHeader">
      <div class="d-flex align-items-center">
        <div class="input-group" style="width: 300px;" v-if="searchable">
          <span class="input-group-text bg-white">
            <i class="bi bi-search text-muted"></i>
          </span>
          <input 
            type="text" 
            class="form-control"
            :placeholder="searchPlaceholder"
            v-model="searchQuery"
            @input="handleSearch"
          >
        </div>
      </div>
      
      <div class="d-flex align-items-center gap-2">
        <slot name="actions"></slot>
      </div>
    </div>
    
    <!-- Table -->
    <div class="table-responsive">
      <table class="table table-hover align-middle mb-0">
        <thead class="bg-light">
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              :style="{ width: column.width }"
              :class="{ 'sortable': column.sortable }"
              @click="column.sortable && handleSort(column.key)"
            >
              <div class="d-flex align-items-center">
                {{ column.label }}
                <i 
                  v-if="column.sortable"
                  class="bi ms-1"
                  :class="getSortIcon(column.key)"
                ></i>
              </div>
            </th>
            <th v-if="$slots.rowActions" style="width: 100px;">Actions</th>
          </tr>
        </thead>
        <tbody>
          <!-- Loading State -->
          <tr v-if="loading">
            <td :colspan="columns.length + ($slots.rowActions ? 1 : 0)" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="text-muted mt-2 mb-0">Loading data...</p>
            </td>
          </tr>
          
          <!-- Empty State -->
          <tr v-else-if="filteredData.length === 0">
            <td :colspan="columns.length + ($slots.rowActions ? 1 : 0)" class="text-center py-5">
              <i class="bi bi-inbox fs-1 text-muted"></i>
              <p class="text-muted mt-2 mb-0">{{ emptyMessage }}</p>
            </td>
          </tr>
          
          <!-- Data Rows -->
          <tr v-else v-for="(row, index) in paginatedData" :key="row.id || index">
            <td v-for="column in columns" :key="column.key">
              <slot :name="`cell-${column.key}`" :row="row" :value="getCellValue(row, column.key)">
                {{ getCellValue(row, column.key) }}
              </slot>
            </td>
            <td v-if="$slots.rowActions">
              <slot name="rowActions" :row="row"></slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Pagination -->
    <div 
      class="d-flex justify-content-between align-items-center mt-3"
      v-if="paginated && !loading && filteredData.length > 0"
    >
      <div class="text-muted small">
        Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ filteredData.length }} entries
      </div>
      
      <nav>
        <ul class="pagination pagination-sm mb-0">
          <li class="page-item" :class="{ disabled: currentPage === 1 }">
            <a class="page-link" href="#" @click.prevent="currentPage--">
              <i class="bi bi-chevron-left"></i>
            </a>
          </li>
          <li 
            class="page-item" 
            v-for="page in visiblePages" 
            :key="page"
            :class="{ active: currentPage === page }"
          >
            <a class="page-link" href="#" @click.prevent="currentPage = page">
              {{ page }}
            </a>
          </li>
          <li class="page-item" :class="{ disabled: currentPage === totalPages }">
            <a class="page-link" href="#" @click.prevent="currentPage++">
              <i class="bi bi-chevron-right"></i>
            </a>
          </li>
        </ul>
      </nav>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  
  props: {
    columns: {
      type: Array,
      required: true
      // { key: 'name', label: 'Name', sortable: true, width: '200px' }
    },
    data: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    searchable: {
      type: Boolean,
      default: true
    },
    searchPlaceholder: {
      type: String,
      default: 'Search...'
    },
    paginated: {
      type: Boolean,
      default: true
    },
    perPage: {
      type: Number,
      default: 10
    },
    showHeader: {
      type: Boolean,
      default: true
    },
    emptyMessage: {
      type: String,
      default: 'No data available'
    }
  },
  
  data() {
    return {
      searchQuery: '',
      currentPage: 1,
      sortKey: null,
      sortOrder: 'asc'
    }
  },
  
  computed: {
    filteredData() {
      let result = [...this.data]
      
      // Search filter
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(row => {
          return this.columns.some(col => {
            const value = this.getCellValue(row, col.key)
            return String(value).toLowerCase().includes(query)
          })
        })
      }
      
      // Sort
      if (this.sortKey) {
        result.sort((a, b) => {
          const aVal = this.getCellValue(a, this.sortKey)
          const bVal = this.getCellValue(b, this.sortKey)
          
          if (aVal < bVal) return this.sortOrder === 'asc' ? -1 : 1
          if (aVal > bVal) return this.sortOrder === 'asc' ? 1 : -1
          return 0
        })
      }
      
      return result
    },
    
    paginatedData() {
      if (!this.paginated) return this.filteredData
      return this.filteredData.slice(this.startIndex, this.endIndex)
    },
    
    totalPages() {
      return Math.ceil(this.filteredData.length / this.perPage)
    },
    
    startIndex() {
      return (this.currentPage - 1) * this.perPage
    },
    
    endIndex() {
      return Math.min(this.startIndex + this.perPage, this.filteredData.length)
    },
    
    visiblePages() {
      const pages = []
      const start = Math.max(1, this.currentPage - 2)
      const end = Math.min(this.totalPages, start + 4)
      
      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    }
  },
  
  methods: {
    getCellValue(row, key) {
      // Support nested keys like 'company.name'
      return key.split('.').reduce((obj, k) => obj?.[k], row) ?? ''
    },
    
    handleSearch() {
      this.currentPage = 1
      this.$emit('search', this.searchQuery)
    },
    
    handleSort(key) {
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortKey = key
        this.sortOrder = 'asc'
      }
      this.$emit('sort', { key, order: this.sortOrder })
    },
    
    getSortIcon(key) {
      if (this.sortKey !== key) return 'bi-arrow-down-up text-muted'
      return this.sortOrder === 'asc' ? 'bi-arrow-up' : 'bi-arrow-down'
    }
  },
  
  watch: {
    data() {
      this.currentPage = 1
    }
  }
}
</script>

<style scoped>
.sortable {
  cursor: pointer;
}

.sortable:hover {
  background-color: #e9ecef;
}

.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>