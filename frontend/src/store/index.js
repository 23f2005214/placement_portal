import { createStore } from 'vuex'

const store = createStore({
  state: {
    token: localStorage.getItem('access_token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    profile: JSON.parse(localStorage.getItem('profile') || 'null'),
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
    
    REMOVE_TOAST(state, id) {
      state.toasts = state.toasts.filter(t => t.id !== id)
    }
  },

  actions: {
    logout({ commit }) {
      commit('CLEAR_AUTH')
    }
  }
})

console.log('Store initialized, isLoggedIn:', store.getters.isLoggedIn)

export default store