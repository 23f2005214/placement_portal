import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// Import components directly (not lazy loaded for debugging)
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// Lazy load dashboard components
const AdminLayout = () => import('../components/admin/AdminLayout.vue')
const AdminDashboard = () => import('../components/admin/AdminDashboard.vue')
const CompanyManagement = () => import('../components/admin/CompanyManagement.vue')
const StudentManagement = () => import('../components/admin/StudentManagement.vue')
const DriveManagement = () => import('../components/admin/DriveManagement.vue')

const CompanyLayout = () => import('../components/company/CompanyLayout.vue')
const CompanyDashboard = () => import('../components/company/CompanyDashboard.vue')
const CompanyProfile = () => import('../components/company/CompanyProfile.vue')
const CreateDrive = () => import('../components/company/CreateDrive.vue')
const ManageDrives = () => import('../components/company/ManageDrives.vue')

const StudentLayout = () => import('../components/student/StudentLayout.vue')
const StudentDashboard = () => import('../components/student/StudentDashboard.vue')
const StudentProfile = () => import('../components/student/StudentProfile.vue')
const DrivesList = () => import('../components/student/DrivesList.vue')
const MyApplications = () => import('../components/student/MyApplications.vue')

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login, meta: { guest: true } },
  { path: '/register', name: 'Register', component: Register, meta: { guest: true } },
  
  // Admin
  {
    path: '/admin',
    component: AdminLayout,
    meta: { auth: true, role: 'admin' },
    children: [
      { path: '', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'companies', name: 'CompanyManagement', component: CompanyManagement },
      { path: 'students', name: 'StudentManagement', component: StudentManagement },
      { path: 'drives', name: 'DriveManagement', component: DriveManagement }
    ]
  },
  
  // Company
  {
    path: '/company',
    component: CompanyLayout,
    meta: { auth: true, role: 'company' },
    children: [
      { path: '', name: 'CompanyDashboard', component: CompanyDashboard },
      { path: 'profile', name: 'CompanyProfile', component: CompanyProfile },
      { path: 'drives', name: 'ManageDrives', component: ManageDrives },
      { path: 'drives/create', name: 'CreateDrive', component: CreateDrive }
    ]
  },
  
  // Student
  {
    path: '/student',
    component: StudentLayout,
    meta: { auth: true, role: 'student' },
    children: [
      { path: '', name: 'StudentDashboard', component: StudentDashboard },
      { path: 'profile', name: 'StudentProfile', component: StudentProfile },
      { path: 'drives', name: 'DrivesList', component: DrivesList },
      { path: 'applications', name: 'MyApplications', component: MyApplications }
    ]
  },
  
  // Catch all
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Simple navigation guard
router.beforeEach((to, from, next) => {
  console.log('Router: navigating to', to.path)
  
  const isLoggedIn = store.getters.isLoggedIn
  const userRole = store.getters.userRole
  
  // Check if route requires auth
  const requiresAuth = to.matched.some(r => r.meta.auth)
  const requiredRole = to.matched.find(r => r.meta.role)?.meta.role
  const guestOnly = to.matched.some(r => r.meta.guest)
  
  console.log('Router: isLoggedIn=', isLoggedIn, 'requiresAuth=', requiresAuth, 'role=', userRole)
  
  // Protected route, not logged in
  if (requiresAuth && !isLoggedIn) {
    console.log('Router: redirecting to login (not authenticated)')
    return next('/login')
  }
  
  // Wrong role
  if (requiresAuth && requiredRole && userRole !== requiredRole) {
    console.log('Router: wrong role, redirecting to correct dashboard')
    if (userRole === 'admin') return next('/admin')
    if (userRole === 'company') return next('/company')
    if (userRole === 'student') return next('/student')
    return next('/')
  }
  
  // Guest only (login/register) but already logged in
  if (guestOnly && isLoggedIn) {
    console.log('Router: already logged in, redirecting to dashboard')
    if (userRole === 'admin') return next('/admin')
    if (userRole === 'company') return next('/company')
    if (userRole === 'student') return next('/student')
    return next('/')
  }
  
  next()
})

console.log('Router initialized')

export default router