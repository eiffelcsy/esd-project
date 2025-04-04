<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const isLogin = ref(true)
const email = ref('')
const password = ref('')
const firstName = ref('')
const lastName = ref('')

const handleSubmit = async () => {
  try {
    if (isLogin.value) {
      await userStore.login(email.value, password.value)
    } else {
      await userStore.register({
        email: email.value,
        password: password.value,
        first_name: firstName.value,
        last_name: lastName.value
      })
    }

    // Redirect to dashboard after successful login/registration
    router.push('/dashboard')
  } catch (err) {
    // Error is already handled by the store
    console.error('Authentication error:', err)
  }
}

const toggleForm = () => {
  isLogin.value = !isLogin.value
  // Clear form fields when switching
  email.value = ''
  password.value = ''
  firstName.value = ''
  lastName.value = ''
}
</script>

<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">User Authentication</h1>
    <div class="mx-auto">
      <div class="bg-white rounded-lg shadow p-4">
        <h2 class="text-xl font-semibold mb-3">{{ isLogin ? 'Login' : 'Register' }}</h2>
        
        <!-- Error message -->
        <div v-if="userStore.error" class="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {{ userStore.error }}
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <!-- Registration fields -->
          <template v-if="!isLogin">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
              <Input
                v-model="firstName"
                type="text"
                required
                placeholder="Enter your first name"
                :disabled="userStore.loading"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
              <Input
                v-model="lastName"
                type="text"
                required
                placeholder="Enter your last name"
                :disabled="userStore.loading"
              />
            </div>
          </template>

          <!-- Common fields -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
            <Input
              v-model="email"
              type="email"
              required
              placeholder="Enter your email"
              :disabled="userStore.loading"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <Input
              v-model="password"
              type="password"
              required
              placeholder="Enter your password"
              :disabled="userStore.loading"
            />
          </div>

          <Button
            type="submit"
            class="w-full"
            :disabled="userStore.loading"
          >
            {{ userStore.loading ? (isLogin ? 'Signing in...' : 'Registering...') : (isLogin ? 'Sign in' : 'Register') }}
          </Button>
        </form>

        <!-- Toggle between login and register -->
        <div class="mt-4 text-center">
          <button
            type="button"
            @click="toggleForm"
            class="text-sm text-blue-600 hover:text-blue-800"
            :disabled="userStore.loading"
          >
            {{ isLogin ? "Don't have an account? Register" : "Already have an account? Sign in" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template> 