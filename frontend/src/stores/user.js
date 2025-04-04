import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null
  }),

  getters: {
    userId: (state) => state.user?.id,
    userEmail: (state) => state.user?.email,
    userName: (state) => {
      if (!state.user) return ''
      return `${state.user.first_name || ''} ${state.user.last_name || ''}`.trim()
    }
  },

  actions: {
    setUser(userData) {
      this.user = userData
      this.isAuthenticated = !!userData
      this.error = null
    },

    setLoading(loading) {
      this.loading = loading
    },

    setError(error) {
      this.error = error
      this.isAuthenticated = false
    },

    async login(email, password) {
      try {
        this.setLoading(true)
        const response = await fetch('http://localhost:5001/api/users/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || 'Authentication failed')
        }

        this.setUser(data.user)
        
        // Store user data in localStorage for persistence
        localStorage.setItem('user', JSON.stringify(data.user))
        
        return data
      } catch (error) {
        this.setError(error.message)
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    async register(userData) {
      try {
        this.setLoading(true)
        const response = await fetch('http://localhost:5001/api/users/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData),
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || 'Registration failed')
        }

        this.setUser(data.user)
        
        // Store user data in localStorage for persistence
        localStorage.setItem('user', JSON.stringify(data.user))
        
        return data
      } catch (error) {
        this.setError(error.message)
        throw error
      } finally {
        this.setLoading(false)
      }
    },

    logout() {
      this.setUser(null)
      this.isAuthenticated = false
      this.error = null
      
      // Clear localStorage
      localStorage.clear()
    },

    // Initialize user session from localStorage on app start
    initializeSession() {
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        try {
          this.setUser(JSON.parse(storedUser))
        } catch (error) {
          this.logout()
        }
      }
    }
  }
}) 