<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const email = ref('')
const password = ref('')

const handleSubmit = () => {
  // TODO: Implement authentication logic
  console.log('Login attempt:', { email: email.value, password: password.value })
}
</script>

<template>
  <div class="container mx-auto p-4">
      <h1 class="text-2xl font-bold mb-4">User Authentication</h1>
    <div class="mx-auto">
      <div class="bg-white rounded-lg shadow p-4">
      <h2 class="text-xl font-semibold mb-3">Login</h2>
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
            <Input
              v-model="email"
              type="email"
              required
              placeholder="Enter your email"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <Input
              v-model="password"
              type="password"
              required
              placeholder="Enter your password"
            />
          </div>

          <Button
            type="submit"
            class="w-full"
          >
            Sign in
          </Button>
        </form>
      </div>
    </div>
  </div>
</template> 