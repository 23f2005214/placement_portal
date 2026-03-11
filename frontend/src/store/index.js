import { createStore } from 'vuex'

const store = createStore({
  state: {
    token: localStorage.getItem('access_token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    profile: JSON.parse(localStorage.getItem('profile') || 'null'),
    branches: JSON.parse(localStorage.getItem('branches') || '[]'),
    toasts: []
  },

  getters: {
    isLoggedIn: state => !!state.token && !!state.user,
    userRole: state => state.user?.role || null,
    userName: state => {
      if (state.user?.role === 'admin') return 'Admin'
      if (state.profile?.company_name) return state.profile.company_name
      if (state.profile?.first_name) return state.profile.first_name
      return state.user?.email || 'User'
    }
  },

  mutations: {
    SET_AUTH(state, { token, user, profile }) {
      console.log('SET_AUTH:', { token: !!token, user: !!user })
      
      state.token = token
      state.user = user
      state.profile = profile || null
      
      if (token) {
        localStorage.setItem('access_token', token)
      } else {
        localStorage.removeItem('access_token')
      }
      
      if (user) {
        localStorage.setItem('user', JSON.stringify(user))
      } else {
        localStorage.removeItem('user')
      }
      
      if (profile) {
        localStorage.setItem('profile', JSON.stringify(profile))
      } else {
        localStorage.removeItem('profile')
      }
    },
    
    CLEAR_AUTH(state) {
      console.log('CLEAR_AUTH called')
      state.token = null
      state.user = null
      state.profile = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      localStorage.removeItem('profile')
    },
    
    ADD_TOAST(state, toast) {
      const id = Date.now()
      state.toasts.push({ ...toast, id })
      setTimeout(() => {
        state.toasts = state.toasts.filter(t => t.id !== id)
      }, 4000)
    },
    
    SET_BRANCHES(state, branches) {
      state.branches = branches
      localStorage.setItem('branches', JSON.stringify(branches))
    },
  },

  actions: {
    logout({ commit }) {
      commit('CLEAR_AUTH')
    },
    
    async fetchBranches({ commit }) {
      try {
        const response = await fetch('http://localhost:5000/api/drives/branches')
        const data = await response.json()
        commit('SET_BRANCHES', data.branches || [])
      } catch (error) {
        console.error('Failed to fetch branches:', error)
        // Fallback to some default branches
        commit('SET_BRANCHES', ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil'])
      }
    },
    
    async refreshUserData({ commit, state }) {
      if (!state.token) return
      
      try {
        // Fetch user profile based on role
        let profileResponse
        if (state.user.role === 'student') {
          profileResponse = await fetch('http://localhost:5000/api/student/profile', {
            headers: { 'Authorization': `Bearer ${state.token}` }
          })
        } else if (state.user.role === 'company') {
          profileResponse = await fetch('http://localhost:5000/api/company/profile', {
            headers: { 'Authorization': `Bearer ${state.token}` }
          })
        }
        
        if (profileResponse && profileResponse.ok) {
          const profile = await profileResponse.json()
          commit('SET_AUTH', { token: state.token, user: state.user, profile })
        }
      } catch (error) {
        console.error('Failed to refresh user data:', error)
      }
    }
  }
})

console.log('Store initialized, isLoggedIn:', store.getters.isLoggedIn)

export default store