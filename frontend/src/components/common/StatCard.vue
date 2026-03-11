<template>
  <div class="card stat-card h-100">
    <div class="card-body">
      <div class="d-flex align-items-center">
        <div 
          class="stat-icon rounded-circle d-flex align-items-center justify-content-center me-3"
          :class="iconBgClass"
        >
          <i :class="[icon, iconTextClass]" class="fs-4"></i>
        </div>
        <div class="flex-grow-1">
          <p class="text-muted small mb-1">{{ title }}</p>
          <h3 class="mb-0 fw-bold">
            <span v-if="loading" class="placeholder-glow">
              <span class="placeholder col-6"></span>
            </span>
            <span v-else>{{ formattedValue }}</span>
          </h3>
        </div>
      </div>
      
      <!-- Trend indicator -->
      <div class="mt-3 d-flex align-items-center" v-if="trend !== null && !loading">
        <span 
          class="badge me-2"
          :class="trendBadgeClass"
        >
          <i :class="trendIconClass"></i>
          {{ Math.abs(trend) }}%
        </span>
        <span class="text-muted small">{{ trendLabel }}</span>
      </div>
      
      <!-- Additional info slot -->
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [Number, String],
      required: true
    },
    icon: {
      type: String,
      default: 'bi bi-graph-up'
    },
    color: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'success', 'warning', 'danger', 'info'].includes(value)
    },
    trend: {
      type: Number,
      default: null
    },
    trendLabel: {
      type: String,
      default: 'vs last month'
    },
    loading: {
      type: Boolean,
      default: false
    },
    format: {
      type: String,
      default: 'number' // 'number', 'currency', 'percentage'
    }
  },
  
  computed: {
    iconBgClass() {
      const classes = {
        primary: 'bg-primary bg-opacity-10',
        success: 'bg-success bg-opacity-10',
        warning: 'bg-warning bg-opacity-10',
        danger: 'bg-danger bg-opacity-10',
        info: 'bg-info bg-opacity-10'
      }
      return classes[this.color] || classes.primary
    },
    
    iconTextClass() {
      const classes = {
        primary: 'text-primary',
        success: 'text-success',
        warning: 'text-warning',
        danger: 'text-danger',
        info: 'text-info'
      }
      return classes[this.color] || classes.primary
    },
    
    trendBadgeClass() {
      return this.trend >= 0 
        ? 'bg-success-subtle text-success' 
        : 'bg-danger-subtle text-danger'
    },
    
    trendIconClass() {
      return this.trend >= 0 ? 'bi bi-arrow-up' : 'bi bi-arrow-down'
    },
    
    formattedValue() {
      if (typeof this.value === 'string') return this.value
      
      switch (this.format) {
        case 'currency':
          return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
          }).format(this.value)
        case 'percentage':
          return `${this.value}%`
        default:
          return new Intl.NumberFormat('en-IN').format(this.value)
      }
    }
  }
}
</script>

<style scoped>
.stat-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
}

.bg-success-subtle {
  background-color: rgba(6, 214, 160, 0.15);
}

.bg-danger-subtle {
  background-color: rgba(239, 71, 111, 0.15);
}
</style>