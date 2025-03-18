<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Group Management</h1>
    
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
      <h2 class="text-xl font-semibold mb-3">Your Groups</h2>
      <div v-if="groups.length === 0" class="text-gray-500">
        No groups created yet. Create one above!
      </div>
      <div v-else class="space-y-4">
        <div v-for="group in groups" :key="group.id" class="border rounded-lg p-4">
          <h3 class="font-semibold">{{ group.name }}</h3>
          <div class="mt-2">
            <h4 class="text-sm font-medium text-gray-700">Members:</h4>
            <ul class="list-disc list-inside">
              <li v-for="member in group.members" :key="member">{{ member }}</li>
            </ul>
          </div>
          <div class="mt-4">
            <Button
              @click="startTripPlanning(group.id)"
            >
              Start Trip Planning
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

const router = useRouter()

const newGroup = ref({
  name: '',
  members: []
})
const newMemberEmail = ref('')
const groups = ref([])

const addMember = () => {
  if (newMemberEmail.value && !newGroup.value.members.includes(newMemberEmail.value)) {
    newGroup.value.members.push(newMemberEmail.value)
    newMemberEmail.value = ''
  }
}

const removeMember = (index) => {
  newGroup.value.members.splice(index, 1)
}

const createGroup = async () => {
  try {
    // TODO: Implement API call to create group
    const response = await fetch('/api/groups', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newGroup.value)
    })
    
    if (response.ok) {
      const group = await response.json()
      groups.value.push(group)
      newGroup.value = { name: '', members: [] }
    }
  } catch (error) {
    console.error('Error creating group:', error)
  }
}

const fetchGroups = async () => {
  try {
    // TODO: Implement API call to fetch groups
    const response = await fetch('/api/groups')
    if (response.ok) {
      groups.value = await response.json()
    }
  } catch (error) {
    console.error('Error fetching groups:', error)
  }
}

const startTripPlanning = (groupId) => {
  router.push({
    name: 'trip-ideation',
    params: { groupId }
  })
}

onMounted(() => {
  fetchGroups()
})
</script> 