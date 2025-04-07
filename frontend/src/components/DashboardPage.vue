<script setup>
import { useUserStore } from '@/stores/user'
import { Button } from '@/components/ui/button'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const handleLogout = () => {
  userStore.logout()
  localStorage.clear()
  router.push('/login')
}

const navigateToGroups = () => {
  router.push('/groups')
}
</script>

<template>
  <div class="container mx-auto p-4">
    <div class="max-w-2xl mx-auto">
      <!-- Header -->
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-2xl font-bold">Dashboard</h1>
        <Button variant="outline" @click="handleLogout">Logout</Button>
      </div>

      <!-- User Profile Card -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Profile Information</h2>
        <div class="space-y-3">
          <div class="flex justify-between">
            <span class="text-gray-600">Name:</span>
            <span class="font-medium">{{ userStore.userName || 'Not set' }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Email:</span>
            <span class="font-medium">{{ userStore.userEmail }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">User ID:</span>
            <span class="font-medium">{{ userStore.userId }}</span>
          </div>
        </div>
      </div>

      <!-- Navigation Card -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
        <div class="space-y-4">
          <Button class="w-full" @click="navigateToGroups">
            Go to Groups
          </Button>
        </div>
      </div>
    </div>
  </div>
</template> 