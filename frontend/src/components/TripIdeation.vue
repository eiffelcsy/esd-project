<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Plan Your Trip</h1>

    <!-- Date Selection -->
    <div class="bg-white rounded-lg shadow p-4 mb-6">
      <h2 class="text-xl font-semibold mb-3">Select Trip Dates</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Start Date</label>
          <input
            v-model="tripDates.start"
            type="date"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            :min="minDate"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700">End Date</label>
          <input
            v-model="tripDates.end"
            type="date"
            class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            :min="tripDates.start"
          />
        </div>
      </div>
      <div class="mt-4">
        <button
          @click="submitDates"
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          :disabled="!tripDates.start || !tripDates.end"
        >
          Confirm Dates
        </button>
      </div>
    </div>

    <!-- Destination Selection -->
    <div v-if="datesConfirmed" class="bg-white rounded-lg shadow p-4 mb-6">
      <h2 class="text-xl font-semibold mb-3">Choose Destination</h2>
      <div class="space-y-4">
        <div v-if="aiRecommendations.length > 0">
          <h3 class="font-medium text-gray-700">AI Recommended Destinations</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-2">
            <div
              v-for="destination in aiRecommendations"
              :key="destination.id"
              class="border rounded-lg p-4 cursor-pointer hover:border-blue-500"
              :class="{ 'border-blue-500': selectedDestination?.id === destination.id }"
              @click="selectDestination(destination)"
            >
              <h4 class="font-semibold">{{ destination.name }}</h4>
              <p class="text-sm text-gray-600">{{ destination.description }}</p>
              <div class="mt-2 text-sm text-gray-500">
                <p>Weather: {{ destination.weather }}</p>
                <p>Best time to visit: {{ destination.bestTime }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4">
          <h3 class="font-medium text-gray-700">Or Search for a Destination</h3>
          <div class="flex gap-2">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Enter destination name"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            <button
              @click="searchDestination"
              class="mt-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              Search
            </button>
          </div>
        </div>

        <div v-if="selectedDestination" class="mt-4">
          <button
            @click="confirmDestination"
            class="w-full px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
          >
            Confirm Destination: {{ selectedDestination.name }}
          </button>
        </div>
      </div>
    </div>

    <!-- Group Availability -->
    <div v-if="destinationConfirmed" class="bg-white rounded-lg shadow p-4">
      <h2 class="text-xl font-semibold mb-3">Group Availability</h2>
      <div class="space-y-4">
        <div v-for="member in groupMembers" :key="member.id" class="border rounded-lg p-4">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="font-semibold">{{ member.name }}</h3>
              <p class="text-sm text-gray-600">{{ member.email }}</p>
            </div>
            <div class="text-sm">
              <span v-if="member.availability" class="text-green-500">Available</span>
              <span v-else class="text-red-500">Not Available</span>
            </div>
          </div>
        </div>

        <div v-if="allMembersAvailable" class="mt-4">
          <button
            @click="createTrip"
            class="w-full px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
          >
            Create Trip
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TripIdeation',
  data() {
    return {
      tripDates: {
        start: '',
        end: ''
      },
      datesConfirmed: false,
      destinationConfirmed: false,
      selectedDestination: null,
      searchQuery: '',
      aiRecommendations: [],
      groupMembers: [],
      minDate: new Date().toISOString().split('T')[0]
    }
  },
  computed: {
    allMembersAvailable() {
      return this.groupMembers.every(member => member.availability)
    }
  },
  methods: {
    async submitDates() {
      try {
        // TODO: Implement API call to save dates
        const response = await fetch(`/api/groups/${this.$route.params.groupId}/dates`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.tripDates)
        })
        
        if (response.ok) {
          this.datesConfirmed = true
          this.fetchAIRecommendations()
        }
      } catch (error) {
        console.error('Error submitting dates:', error)
      }
    },
    async fetchAIRecommendations() {
      try {
        // TODO: Implement API call to get AI recommendations
        const response = await fetch(`/api/recommendations?start=${this.tripDates.start}&end=${this.tripDates.end}`)
        if (response.ok) {
          this.aiRecommendations = await response.json()
        }
      } catch (error) {
        console.error('Error fetching recommendations:', error)
      }
    },
    selectDestination(destination) {
      this.selectedDestination = destination
    },
    async searchDestination() {
      try {
        // TODO: Implement API call to search destinations
        const response = await fetch(`/api/destinations/search?q=${this.searchQuery}`)
        if (response.ok) {
          const results = await response.json()
          this.aiRecommendations = results
        }
      } catch (error) {
        console.error('Error searching destinations:', error)
      }
    },
    async confirmDestination() {
      try {
        // TODO: Implement API call to save destination
        const response = await fetch(`/api/groups/${this.$route.params.groupId}/destination`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.selectedDestination)
        })
        
        if (response.ok) {
          this.destinationConfirmed = true
          this.fetchGroupMembers()
        }
      } catch (error) {
        console.error('Error confirming destination:', error)
      }
    },
    async fetchGroupMembers() {
      try {
        // TODO: Implement API call to fetch group members
        const response = await fetch(`/api/groups/${this.$route.params.groupId}/members`)
        if (response.ok) {
          this.groupMembers = await response.json()
        }
      } catch (error) {
        console.error('Error fetching group members:', error)
      }
    },
    async createTrip() {
      try {
        // TODO: Implement API call to create trip
        const response = await fetch('/api/trips', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            groupId: this.$route.params.groupId,
            dates: this.tripDates,
            destination: this.selectedDestination
          })
        })
        
        if (response.ok) {
          const trip = await response.json()
          this.$router.push({
            name: 'trip-planning',
            params: { tripId: trip.id }
          })
        }
      } catch (error) {
        console.error('Error creating trip:', error)
      }
    }
  }
}
</script> 