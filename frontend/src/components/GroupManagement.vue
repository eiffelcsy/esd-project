<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Group Management</h1>
    
    <!-- Success Notification -->
    <div v-if="showNotification" class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4 flex items-center justify-between" role="alert">
      <div>
        <span class="font-bold">Success!</span>
        <span class="block sm:inline"> {{ notificationMessage }}</span>
      </div>
      <button @click="showNotification = false" class="ml-4">
        <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
        </svg>
      </button>
    </div>
    
    <!-- Create New Group -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <h2 class="text-xl font-semibold mb-3">Create New Group</h2>
      <form @submit.prevent="createGroup" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Group Name</label>
          <Input
            v-model="newGroup.name"
            type="text"
            class="mt-1"
            required
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">Add Members</label>
          <div class="flex gap-2">
            <Input
              v-model="newMemberEmail"
              type="email"
              placeholder="Enter email address"
              class="mt-1"
            />
            <Button
              type="button"
              @click="addMember"
              class="mt-1"
            >
              Add
            </Button>
          </div>
          <div class="mt-2">
            <div v-for="(member, index) in newGroup.members" :key="index" class="flex items-center gap-2">
              <span>{{ member }}</span>
              <Button
                type="button"
                variant="ghost"
                @click="removeMember(index)"
                class="text-red-500 hover:text-red-700"
              >
                Remove
              </Button>
            </div>
          </div>
        </div>
        <!-- Status Visualization -->
        <div class="mt-4 border-t pt-4">
          <h3 class="text-sm font-medium mb-2">Group Creation Status</h3>
          <div class="flex items-center w-full mb-4">
            <div class="flex flex-col items-center w-1/3">
              <div class="w-8 h-8 flex items-center justify-center rounded-full bg-green-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <span class="text-xs mt-1 text-center">User Validation</span>
            </div>
            <div class="h-1 w-full bg-green-200">
              <div class="h-1 bg-green-500 w-full"></div>
            </div>
            <div class="flex flex-col items-center w-1/3">
              <div class="w-8 h-8 flex items-center justify-center rounded-full" 
                :class="[
                  creationStatus.groupCreation ? 'bg-green-500 text-white' : 'bg-gray-200 text-gray-500',
                  isSubmitting ? 'pulse-animation' : ''
                ]">
                <svg v-if="creationStatus.groupCreation" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
                <svg v-else-if="isSubmitting" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span v-else>2</span>
              </div>
              <span class="text-xs mt-1 text-center">Group Creation</span>
            </div>
            <div class="h-1 w-full bg-green-200">
              <div class="h-1 bg-green-500 transition-all duration-300" :class="creationStatus.groupCreation ? 'w-full' : isSubmitting ? 'w-1/2' : 'w-0'"></div>
            </div>
            <div class="flex flex-col items-center w-1/3">
              <div class="w-8 h-8 flex items-center justify-center rounded-full bg-green-500 text-white">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
              <span class="text-xs mt-1 text-center">Calendar Creation</span>
            </div>
          </div>
          <div class="text-xs text-gray-500">
            <p>Note: User Validation and Calendar Creation are mock services at the moment.</p>
          </div>
        </div>
        <!-- Display testing info -->
        <div class="text-xs text-gray-500 border-t pt-2 mt-2">
          <p>Testing Mode: Using User ID {{ newGroup.createdBy }}</p>
          <p>Start Date Range: {{ new Date(newGroup.startDateRange).toLocaleDateString() }}</p>
          <p>End Date Range: {{ new Date(newGroup.endDateRange).toLocaleDateString() }}</p>
        </div>
        <Button
          type="submit"
          class="w-full"
        >
          Create Group
        </Button>
      </form>
    </div>

    <!-- Existing Groups -->
    <div class="bg-white rounded-lg shadow p-4">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-semibold">Your Groups</h2>
        <Button 
          variant="outline" 
          size="sm"
          @click="fetchGroups"
          class="flex items-center gap-1"
          :disabled="isRefreshing"
        >
          <svg v-if="isRefreshing" class="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
          </svg>
          <span>{{ isRefreshing ? 'Refreshing...' : 'Refresh' }}</span>
        </Button>
      </div>
      <div v-if="groups.length === 0" class="text-gray-500">
        No groups created yet. Create one above!
      </div>
      <div v-else class="space-y-4">
        <div v-for="group in groups" :key="group.id" 
          :class="[
            'border rounded-lg p-4 transition-all', 
            group.id === newlyCreatedGroupId ? 'border-green-500 shadow-md animate-pulse-light' : ''
          ]">
          <div class="flex justify-between items-start">
            <h3 class="font-semibold">{{ group.name }}</h3>
            <div class="flex gap-2 items-center">
              <div class="text-sm px-2 py-1 rounded" :class="{
                'bg-green-100 text-green-800': group.status === 'completed',
                'bg-yellow-100 text-yellow-800': group.status === 'pending' || group.status === 'partial',
                'bg-red-100 text-red-800': group.status === 'failed'
              }">
                {{ group.status }}
              </div>
              <button 
                @click.stop="confirmDeleteGroup(group)"
                class="text-red-500 hover:text-red-700 p-1 rounded-full hover:bg-red-50"
                title="Delete Group"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <p v-if="group.description" class="text-sm text-gray-600 mt-1">{{ group.description }}</p>
          
          <div class="mt-2">
            <h4 class="text-sm font-medium text-gray-700">Members:</h4>
            <ul class="list-disc list-inside">
              <li v-for="member in group.members" :key="member">{{ member }}</li>
            </ul>
          </div>
          <div class="mt-4">
            <Button
              @click="startTripPlanning(group.id)"
              :disabled="group.status !== 'completed'"
              :class="{ 'opacity-50 cursor-not-allowed': group.status !== 'completed' }"
            >
              Start Trip Planning
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-medium mb-4">Confirm Deletion</h3>
        <p v-if="deleteError" class="mb-4 text-red-500 text-sm bg-red-50 p-2 rounded">
          {{ deleteError }}
        </p>
        <p class="mb-6">Are you sure you want to delete the group "{{ groupToDelete.name }}"? This action cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <Button
            variant="outline"
            @click="showDeleteModal = false"
            :disabled="isDeletingGroup"
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            @click="deleteGroup"
            :disabled="isDeletingGroup"
          >
            <span v-if="isDeletingGroup" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Deleting...
            </span>
            <span v-else>Delete</span>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { userService } from '@/services/userService'

const router = useRouter()
const isSubmitting = ref(false)
const showNotification = ref(false)
const lastCreatedGroup = ref({})
const newlyCreatedGroupId = ref(null)
const notificationType = ref('create') // 'create' or 'delete'
const isRefreshing = ref(false)
const currentUserId = ref(null)

const notificationMessage = computed(() => {
  if (notificationType.value === 'create') {
    return `Group "${lastCreatedGroup.value.name}" has been created successfully.`
  } else if (notificationType.value === 'delete') {
    return `Group "${lastCreatedGroup.value.name}" has been deleted successfully.`
  } else if (notificationType.value === 'error') {
    return lastCreatedGroup.value.name
  }
  return ''
})

const creationStatus = ref({
  userValidation: true,
  groupCreation: false,
  calendarCreation: true
})

const newGroup = ref({
  name: '',
  members: [],
  createdBy: null,
  startDateRange: new Date().toISOString(),
  endDateRange: new Date(new Date().setMonth(new Date().getMonth() + 1)).toISOString()
})
const newMemberEmail = ref('')
const groups = ref([])

const showDeleteModal = ref(false)
const groupToDelete = ref({})
const isDeletingGroup = ref(false)
const deleteError = ref('')

const addMember = () => {
  if (newMemberEmail.value && !newGroup.value.members.includes(newMemberEmail.value)) {
    newGroup.value.members.push(newMemberEmail.value)
    newMemberEmail.value = ''
  }
}

const removeMember = (index) => {
  newGroup.value.members.splice(index, 1)
}

const initializeUser = async () => {
  try {
    // Try to get user with ID 1
    try {
      const user = await userService.getUser(1)
      currentUserId.value = user.user_id
      newGroup.value.createdBy = user.user_id
      console.log('Found existing user:', user)
    } catch (error) {
      if (error.message === 'USER_NOT_FOUND') {
        // If user doesn't exist, create a new one with email
        console.log('User not found, creating new user...')
        const username = 'testuser'
        const email = 'test@example.com'
        const newUser = await userService.registerUser(username, email)
        currentUserId.value = newUser.user_id
        newGroup.value.createdBy = newUser.user_id
        console.log('Created new user:', newUser)
      } else {
        // If it's a different error, throw it
        throw error
      }
    }
  } catch (error) {
    console.error('Error initializing user:', error)
    // Show error in UI
    showNotification.value = true
    notificationType.value = 'error'
    lastCreatedGroup.value = { name: `Error: ${error.message}` }
  }
}

const createGroup = async () => {
  try {
    isSubmitting.value = true
    
    // Ensure we have a user
    if (!currentUserId.value) {
      await initializeUser()
      // Double check we got a user ID
      if (!currentUserId.value) {
        throw new Error('Failed to initialize user')
      }
    }
    
    // Update group creation status
    setTimeout(() => {
      creationStatus.value.groupCreation = true
    }, 1000)
    
    const payload = {
      name: newGroup.value.name,
      members: newGroup.value.members,
      createdBy: currentUserId.value,
      startDateRange: newGroup.value.startDateRange,
      endDateRange: newGroup.value.endDateRange,
      description: 'Created for testing purposes'
    }

    console.log('Creating group with payload:', payload)

    const response = await fetch('http://localhost:5003/api/groups', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    
    if (response.ok) {
      const group = await response.json()
      
      // Refresh the groups list instead of manually adding
      await fetchGroups()
      
      // Store the new group for notification
      lastCreatedGroup.value = {
        name: group.name,
        id: group.id || group.group_id
      }
      
      // Set notification type
      notificationType.value = 'create'
      
      // Set the newly created group ID to highlight it
      newlyCreatedGroupId.value = group.id || group.group_id
      
      // Show success notification
      showNotification.value = true
      
      // Auto-dismiss notification after 5 seconds
      setTimeout(() => {
        showNotification.value = false
      }, 5000)
      
      // Auto-remove highlight after 3 seconds
      setTimeout(() => {
        newlyCreatedGroupId.value = null
      }, 3000)
      
      // Reset form and status after successful creation
      newGroup.value = {
        name: '',
        members: [],
        createdBy: null,
        startDateRange: new Date().toISOString(),
        endDateRange: new Date(new Date().setMonth(new Date().getMonth() + 1)).toISOString()
      }
      // Keep success status visible for a moment before resetting
      setTimeout(() => {
        isSubmitting.value = false
        setTimeout(() => {
          creationStatus.value.groupCreation = false
        }, 2000)
      }, 500)
      console.log('Group created successfully:', group)
    } else {
      isSubmitting.value = false
      creationStatus.value.groupCreation = false
      console.error('Failed to create group:', await response.text())
    }
  } catch (error) {
    isSubmitting.value = false
    creationStatus.value.groupCreation = false
    console.error('Error creating group:', error)
  }
}

const fetchGroups = async () => {
  try {
    isRefreshing.value = true
    const response = await fetch('http://localhost:5003/api/groups/requests')
    if (response.ok) {
      const data = await response.json()
      groups.value = data.map(item => ({
        id: item.group_id || item.id,
        name: item.name,
        members: item.users || [],
        description: item.description,
        status: item.status
      }))
    } else {
      console.error('Failed to fetch groups:', await response.text())
    }
  } catch (error) {
    console.error('Error fetching groups:', error)
  } finally {
    isRefreshing.value = false
  }
}

const startTripPlanning = (groupId) => {
  router.push({
    name: 'trip-ideation',
    params: { groupId }
  })
}

const confirmDeleteGroup = (group) => {
  groupToDelete.value = group
  deleteError.value = ''
  showDeleteModal.value = true
}

const deleteGroup = async () => {
  try {
    isDeletingGroup.value = true
    deleteError.value = ''
    
    const response = await fetch(`http://localhost:5003/api/groups/${groupToDelete.value.id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    if (response.ok) {
      // Remove the group from the list
      groups.value = groups.value.filter(g => g.id !== groupToDelete.value.id)
      
      // Close modal and show success notification
      showDeleteModal.value = false
      isDeletingGroup.value = false
      
      // Update the notification to show delete success
      lastCreatedGroup.value = {
        name: groupToDelete.value.name
      }
      notificationType.value = 'delete'
      showNotification.value = true
      
      // Auto-dismiss notification after 5 seconds
      setTimeout(() => {
        showNotification.value = false
      }, 5000)
      
      console.log('Group deleted successfully')
    } else {
      isDeletingGroup.value = false
      const errorText = await response.text()
      deleteError.value = `Failed to delete group: ${errorText || 'Unknown error'}`
      console.error('Failed to delete group:', errorText)
    }
  } catch (error) {
    isDeletingGroup.value = false
    deleteError.value = `Error: ${error.message || 'Unknown error'}`
    console.error('Error deleting group:', error)
  }
}

onMounted(async () => {
  await initializeUser()
  await fetchGroups()
})
</script>

<style scoped>
.pulse-animation {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}

.animate-pulse-light {
  animation: pulse-light 2s 1;
}

@keyframes pulse-light {
  0% {
    background-color: rgba(34, 197, 94, 0.2);
  }
  50% {
    background-color: rgba(34, 197, 94, 0.1);
  }
  100% {
    background-color: transparent;
  }
}
</style> 