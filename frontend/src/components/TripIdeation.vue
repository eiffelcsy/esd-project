<template>
  <div class="container mx-auto p-4">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold">Plan Your Trip</h1>
      <Button 
        @click="goBackToGroups" 
        variant="secondary"
      >
        <ArrowLeft class="h-4 w-4 mr-1" />
        Back to Groups
      </Button>
    </div>

    <!-- Step 1: Group Availability -->
    <div v-if="currentStep === steps.GROUP_AVAILABILITY" class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-semibold">Group Availability</h2>
        <Button 
          @click="refreshCurrentStep"
          variant="outline"
          class="flex items-center gap-1"
        >
          <RefreshCw class="h-4 w-4" />
          Refresh
        </Button>
      </div>
      
      <!-- Calendar Date Range Info -->
      <div class="mb-4 p-3 bg-blue-50 rounded-lg">
        <div class="flex justify-between items-center">
          <div class="flex items-center">
            <CalendarIcon class="h-5 w-5 text-blue-500 mr-2" />
            <div>
              <h3 class="font-medium text-gray-800">Group Calendar</h3>
              <p class="text-sm text-gray-600">
                {{ formatDateDisplay(minDate) }} - {{ formatDateDisplay(maxDate) }}
              </p>
            </div>
          </div>
          
          <!-- Group availability summary -->
          <div class="flex items-center">
            <Users class="h-5 w-5 text-blue-500 mr-2" />
            <div class="text-right">
              <h3 class="font-medium text-gray-800">Group Status</h3>
              <p class="text-sm" :class="availableMembersCount > 0 ? 'text-green-600' : 'text-amber-600'">
                {{ availableMembersCount }} of {{ groupMembers.length }} members with availability
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Member List with Availability -->
      <div class="space-y-6">
        <div v-for="member in groupMembers" :key="member.id" class="border rounded-lg p-4">
          <div class="flex justify-between items-center mb-3">
            <div class="flex items-center">
              <User class="h-5 w-5 text-gray-400 mr-2" />
              <div>
                <h3 class="font-semibold">{{ member.first_name }} {{ member.last_name }}</h3>
                <p class="text-sm text-gray-600">{{ member.email }}</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <span v-if="member.availability" class="text-sm text-green-500 font-medium">Available</span>
              <span v-else class="text-sm text-red-500 font-medium">Not Available</span>
              
              <!-- Simplified toggle for current user -->
              <Button 
                v-if="member.id === currentUserId" 
                @click="updateUserAvailability(member.id, !member.availability)"
                class="px-3 py-1 text-sm rounded-md"
                :class="member.availability ? 'bg-red-100 text-red-700 hover:bg-red-200' : 'bg-green-100 text-green-700 hover:bg-green-200'"
              >
                {{ member.availability ? 'Set Unavailable' : 'Set Available' }}
              </Button>
              
              <!-- Button to show date selector if current user is available -->
              <Button
                v-if="member.id === currentUserId && member.availability && !showDateSelector"
                @click="toggleDateSelector"
                class="px-3 py-1 text-sm rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200"
              >
                Select Dates
              </Button>
            </div>
          </div>
          
          <!-- Date Grid UI -->
          <div v-if="member.id === currentUserId && showDateSelector" class="mt-4">
            <div class="flex justify-between items-center mb-2">
              <h4 class="text-sm font-medium text-gray-700">Select Your Available Dates</h4>
              <Button 
                @click="toggleDateSelector" 
                class="px-3 py-1 text-sm rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200"
              >
                Hide Calendar
              </Button>
            </div>
            
            <!-- Calendar Date Grid -->
            <div class="border rounded-lg p-2">
              <div class="grid grid-cols-7 gap-1 mb-2">
                <div v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']" :key="day" 
                  class="text-xs font-medium text-gray-500 text-center py-1">
                  {{ day }}
                </div>
              </div>
              
              <!-- Date cells -->
              <div class="grid grid-cols-7 gap-1">
                <div v-for="date in calendarCells" :key="date.dateStr" 
                  class="relative">
                  <button 
                    @click="toggleDateAvailability(member.id, date.dateStr)" 
                    :class="[
                      'w-full h-9 rounded-md flex items-center justify-center text-sm',
                      date.inRange ? (
                        isDateSelected(member, date.dateStr) 
                          ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                          : 'bg-gray-100 hover:bg-gray-200'
                      ) : 'opacity-30 bg-gray-100 cursor-not-allowed'
                    ]"
                    :disabled="!date.inRange"
                  >
                    {{ new Date(date.dateStr).getDate() }}
                  </button>
                </div>
              </div>
              
              <div class="mt-3 flex justify-end">
                <Button 
                  @click="saveUserAvailability(member.id)"
                  class="px-3 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600"
                >
                  Save Availability
                </Button>
              </div>
              
              <!-- Success notification -->
              <div v-if="saveSuccess" class="mt-2 p-2 bg-green-100 text-green-800 rounded-md text-center text-sm">
                Availability updated successfully!
              </div>
            </div>
          </div>
          
          <!-- View other member's availability dates -->
          <div v-if="member.id !== currentUserId && member.availableDates.length > 0" class="mt-3">
            <h4 class="text-sm font-medium text-gray-700 mb-1">Available Dates:</h4>
            <div class="flex flex-wrap gap-1">
              <span 
                v-for="date in sortDates(member.availableDates)" 
                :key="date" 
                class="text-xs bg-green-50 text-green-700 px-2 py-1 rounded"
              >
                {{ formatDateDisplay(date) }}
              </span>
            </div>
          </div>
        </div>

        <!-- Proceed to select trip dates button -->
        <div v-if="availableMembersCount > 0" class="mt-6">
          <Button
            @click="currentStep = steps.SELECT_DATES"
            class="w-full"
          >
            Proceed to Select Trip Dates
          </Button>
        </div>
      </div>
    </div>

    <!-- Step 2: Trip Date Selection -->
    <div v-if="currentStep === steps.SELECT_DATES" class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-semibold">Select Trip Dates</h2>
        <Button 
          @click="refreshCurrentStep"
          variant="outline"
          class="flex items-center gap-1"
        >
          <RefreshCw class="h-4 w-4" />
          Refresh
        </Button>
      </div>

      <!-- Duration selector -->
      <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-1">Trip Duration (days)</label>
        <div class="flex items-center gap-2">
          <Button 
            v-for="days in [3, 5, 7, 10, 14]" 
            :key="days"
            @click="updateDateRangeDuration(days)"
            :class="dateRangeDuration === days ? 'bg-blue-500 text-white' : 'bg-gray-100 text-gray-700'"
          >
            {{ days }}
          </Button>
          <input 
            type="number" 
            v-model="dateRangeDuration" 
            min="1" 
            max="30" 
            class="w-16 px-2 py-1 border rounded-md"
            @change="findBestDateRanges()"
          />
        </div>
      </div>

      <!-- Availability heatmap visualization (simple version) -->
      <div class="mb-6">
        <h3 class="font-medium text-gray-700 mb-2">Group Availability Overview</h3>
        <div class="border rounded-lg p-3 overflow-x-auto">
          <div class="flex flex-nowrap min-w-fit">
            <div 
              v-for="date in Object.keys(availabilityHeatmap).sort()" 
              :key="date"
              class="flex-shrink-0 w-8 flex flex-col items-center"
            >
              <div 
                class="w-6 h-6 rounded-full mb-1 flex items-center justify-center text-xs"
                :class="getHeatmapColorClass(availabilityHeatmap[date], groupMembers.length)"
              >
                {{ availabilityHeatmap[date] }}
              </div>
              <div class="text-xs text-gray-500 whitespace-nowrap">
                {{ new Date(date).getDate() }}
              </div>
              <div class="text-xs text-gray-400 whitespace-nowrap">
                {{ new Date(date).toLocaleString('default', { month: 'short' }) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommended date ranges -->
      <div class="mb-6">
        <h3 class="font-medium text-gray-700 mb-2">Recommended Trip Dates</h3>
        <div class="space-y-2">
          <div 
            v-for="(range, index) in bestDateRanges" 
            :key="index"
            class="border rounded-lg p-3 cursor-pointer hover:border-blue-500"
            :class="{ 'border-blue-500 bg-blue-50': selectedDateRange === range }"
            @click="selectDateRange(range)"
          >
            <div class="flex justify-between items-center">
              <div>
                <span class="font-medium">{{ formatDateDisplay(range.startDate) }} - {{ formatDateDisplay(range.endDate) }}</span>
                <span class="text-sm text-gray-500 ml-2">({{ dateRangeDuration }} days)</span>
              </div>
              <div class="flex items-center">
                <span 
                  class="text-sm px-2 py-1 rounded-full"
                  :class="getAvailabilityClass(range.percentAvailable)"
                >
                  {{ Math.round(range.percentAvailable) }}% available
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Manual date selection -->
      <div class="mb-4">
        <h3 class="font-medium text-gray-700 mb-2">Or Select Custom Dates</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Start Date</label>
            <input
              v-model="tripDates.start"
              type="date"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              :min="minDate"
              :max="maxDate"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">End Date</label>
            <input
              v-model="tripDates.end"
              type="date"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              :min="tripDates.start || minDate"
              :max="maxDate"
            />
          </div>
        </div>
      </div>

      <div class="flex gap-3">
        <button
          @click="currentStep = steps.GROUP_AVAILABILITY"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          Back
        </button>
        <button
          @click="confirmTripDates"
          class="flex-1 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          :disabled="!tripDates.start || !tripDates.end"
        >
          Confirm Trip Dates
        </button>
      </div>
    </div>

    <!-- Step 3: Destination Selection -->
    <div v-if="currentStep === steps.SELECT_DESTINATION" class="bg-white rounded-lg shadow p-4 mb-6">
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-semibold">Choose Destination</h2>
        <Button 
          @click="refreshCurrentStep"
          variant="outline"
          class="flex items-center gap-1"
        >
          <RefreshCw class="h-4 w-4" />
          Refresh
        </Button>
      </div>
      
      <!-- Trip date summary -->
      <div class="mb-4 p-3 bg-blue-50 rounded-lg">
        <div class="flex items-center">
          <CalendarIcon class="h-5 w-5 text-blue-500 mr-2" />
          <div>
            <h3 class="font-medium text-gray-800">Selected Trip Dates</h3>
            <p class="text-sm text-gray-600">
              {{ formatDateDisplay(tripDates.start) }} - {{ formatDateDisplay(tripDates.end) }}
            </p>
          </div>
        </div>
      </div>
      
      <div class="space-y-4">
        <div>
          <h3 class="font-medium text-gray-700 mb-2">Enter Your Destination</h3>
          <div class="space-y-3">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Destination (City or Country)</label>
              <input
                v-model="destinationInput"
                type="text"
                placeholder="e.g., Paris, Japan, New York"
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                @input="destinationError = ''"
              />
              <p v-if="destinationError" class="mt-1 text-sm text-red-600">{{ destinationError }}</p>
              <p v-if="isValidatingDestination" class="mt-1 text-sm text-blue-600">Validating destination...</p>
              <p v-if="isValidDestination" class="mt-1 text-sm text-green-600">✓ Valid destination</p>
            </div>
            
            <Button
              @click="validateDestination"
              class="w-full"
              :disabled="!destinationInput || isValidatingDestination"
            >
              Validate Destination
            </Button>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <Button
            @click="currentStep = steps.SELECT_DATES"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Back
          </Button>
          <Button
            @click="confirmDestination"
            class="flex-1 px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
            :disabled="!isValidDestination"
          >
            Confirm Destination: {{ destinationInput }}
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useUserStore } from '@/stores/user'
import { Calendar as CalendarIcon, User, Users, ArrowLeft, RefreshCw } from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const tripDates = reactive({
  start: '',
  end: ''
})

// New steps sequence for flow
const steps = {
  GROUP_AVAILABILITY: 'group_availability',
  SELECT_DATES: 'select_dates',
  SELECT_DESTINATION: 'select_destination'
}
const currentStep = ref(steps.GROUP_AVAILABILITY)

const destinationConfirmed = ref(false)
const selectedDestination = ref(null)
const searchQuery = ref('')
const aiRecommendations = ref([])
const groupMembers = ref([])
const minDate = ref(new Date().toISOString().split('T')[0])
const maxDate = ref('')
const currentUserId = ref(null)
const calendar = ref(null)
const showDateSelector = ref(false)
const tempSelectedDates = ref([])
const saveSuccess = ref(false)

// New variables for availability visualization
const availabilityHeatmap = ref({})
const bestDateRanges = ref([])
const selectedDateRange = ref(null)
const dateRangeDuration = ref(7) // Default trip duration in days

const destinationInput = ref('')
const destinationError = ref('')
const isValidatingDestination = ref(false)
const isValidDestination = ref(false)

// Get current user ID from auth store/localStorage when component mounts
onMounted(async () => {
  try {
    // Get current user from auth store
    currentUserId.value = userStore.user.id
    
    // Get groupId from route params
    const groupId = route.params.groupId
    
    // Call refreshCurrentStep to initialize data
    await refreshCurrentStep()

    // Fetch the calendar for this group
    const calendarResponse = await fetch(`http://localhost:5004/api/calendars/group/${groupId}`);
    if (calendarResponse.ok) {
      const calendarData = await calendarResponse.json();
      calendar.value = calendarData;
      
      // Set min/max dates based on the calendar's date range
      minDate.value = calendarData.start_date_range.split('T')[0];
      maxDate.value = calendarData.end_date_range.split('T')[0];
      
      // Store calendar ID for later use
      localStorage.setItem('currentCalendarId', calendarData.id);
      
      // Fetch group members with their availability right away
      await fetchGroupMembers();
    }
  } catch (error) {
    console.error('Error fetching data on mount:', error);
  }
});

// Function to refresh data based on current step
async function refreshCurrentStep() {
  try {
    if (currentStep.value === steps.GROUP_AVAILABILITY) {
      await fetchGroupMembers()
      calculateAvailabilityHeatmap()
    } else if (currentStep.value === steps.SELECT_DATES) {
      calculateAvailabilityHeatmap()
      findBestDateRanges()
    } else if (currentStep.value === steps.SELECT_DESTINATION) {
      // Reset validation state when refreshing
      isValidDestination.value = false
      destinationError.value = ''
    }
  } catch (error) {
    console.error('Error refreshing data:', error)
  }
}

const allMembersAvailable = computed(() => {
  return groupMembers.value.every(member => member.availability)
})

// Count how many members are available
const availableMembersCount = computed(() => {
  return groupMembers.value.filter(member => member.availability).length
})

// Computed property to generate calendar cells for date selection
const calendarCells = computed(() => {
  if (!minDate.value || !maxDate.value) return [];
  
  const start = new Date(minDate.value);
  const end = new Date(maxDate.value);
  
  // Find the first Sunday before the start date to align the calendar grid
  const firstDay = new Date(start);
  const startDayOfWeek = firstDay.getDay(); // 0 = Sunday, 1 = Monday, etc.
  firstDay.setDate(firstDay.getDate() - startDayOfWeek);
  
  // Create an array to hold the days
  const cells = [];
  const lastDay = new Date(end);
  const endDayOfWeek = lastDay.getDay();
  lastDay.setDate(lastDay.getDate() + (6 - endDayOfWeek));
  
  // Calculate how many days to display
  const totalDays = Math.ceil((lastDay - firstDay) / (1000 * 60 * 60 * 24)) + 1;
  
  // Generate calendar cells
  const currentDate = new Date(firstDay);
  for (let i = 0; i < totalDays; i++) {
    const dateStr = currentDate.toISOString().split('T')[0];
    const inRange = currentDate >= start && currentDate <= end;
    
    cells.push({
      dateStr,
      inRange
    });
    
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return cells;
});

// Get color class for heatmap cell based on availability percentage
function getHeatmapColorClass(count, total) {
  const percentage = (count / total) * 100;
  
  if (percentage === 0) {
    return 'bg-gray-100 text-gray-500';
  } else if (percentage < 30) {
    return 'bg-red-100 text-red-800';
  } else if (percentage < 60) {
    return 'bg-yellow-100 text-yellow-800';
  } else if (percentage < 90) {
    return 'bg-blue-100 text-blue-800';
  } else {
    return 'bg-green-100 text-green-800';
  }
}

// Get class for availability percentage text
function getAvailabilityClass(percentage) {
  if (percentage < 30) {
    return 'bg-red-100 text-red-800';
  } else if (percentage < 60) {
    return 'bg-yellow-100 text-yellow-800';
  } else if (percentage < 90) {
    return 'bg-blue-100 text-blue-800';
  } else {
    return 'bg-green-100 text-green-800';
  }
}

// Format date for display
function formatDateDisplay(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Sort dates
function sortDates(dates) {
  return [...dates].sort((a, b) => new Date(a) - new Date(b));
}

// Toggle date selector visibility
function toggleDateSelector() {
  showDateSelector.value = !showDateSelector.value;
  
  // Initialize the temp selected dates when showing the selector
  if (showDateSelector.value) {
    const currentUser = groupMembers.value.find(m => m.id === currentUserId.value);
    if (currentUser) {
      tempSelectedDates.value = [...currentUser.availableDates];
    }
  }
}

// Check if a date is selected for a member
function isDateSelected(member, dateStr) {
  if (member.id === currentUserId.value) {
    return tempSelectedDates.value.includes(dateStr);
  }
  return member.availableDates.includes(dateStr);
}

// Toggle a single date's availability
function toggleDateAvailability(userId, dateStr) {
  if (tempSelectedDates.value.includes(dateStr)) {
    tempSelectedDates.value = tempSelectedDates.value.filter(d => d !== dateStr);
  } else {
    tempSelectedDates.value.push(dateStr);
  }
}

// Save the user's selected availability dates
async function saveUserAvailability(userId) {
  try {
    const calendarId = localStorage.getItem('currentCalendarId');
    if (!calendarId) {
      console.error('No calendar ID found');
      return;
    }
    
    const response = await fetch(`http://localhost:5004/api/calendars/${calendarId}/availability`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        available_dates: tempSelectedDates.value
      })
    });
    
    if (response.ok) {
      // Update local state
      const member = groupMembers.value.find(m => m.id === userId);
      if (member) {
        member.availability = tempSelectedDates.value.length > 0;
        member.availableDates = [...tempSelectedDates.value];
      }
      // Show success message
      saveSuccess.value = true;
      setTimeout(() => {
        saveSuccess.value = false;
        showDateSelector.value = false; // Hide the selector after saving
      }, 1500);
    } else {
      console.error('Failed to update availability');
    }
  } catch (error) {
    console.error('Error updating availability:', error);
  }
}

async function submitDates() {
  try {
    if (!calendar.value) {
      console.error('No calendar found for this group');
      return;
    }

    // Validate selected dates are within calendar range
    const calendarStart = new Date(calendar.value.start_date_range);
    const calendarEnd = new Date(calendar.value.end_date_range);
    const tripStart = new Date(tripDates.start);
    const tripEnd = new Date(tripDates.end);

    if (tripStart < calendarStart || tripEnd > calendarEnd) {
      console.error('Selected dates must be within the group calendar range');
      return;
    }

    // Store the trip dates in localStorage
    localStorage.setItem('tripStartDate', tripDates.start);
    localStorage.setItem('tripEndDate', tripDates.end);
    
    // Calendar ID should already be set in onMounted, but set it again to be safe
    localStorage.setItem('currentCalendarId', calendar.value.id);
    
    // Move to destination selection step
    currentStep.value = steps.SELECT_DESTINATION;
    fetchAIRecommendations();
  } catch (error) {
    console.error('Error confirming trip dates:', error);
  }
}

function selectDestination(destination) {
  selectedDestination.value = destination
}

async function searchDestination() {
  try {
    // TODO: Implement API call to search destinations
    const response = await fetch(`/api/destinations/search?q=${searchQuery.value}`)
    if (response.ok) {
      const results = await response.json()
      aiRecommendations.value = results
    }
  } catch (error) {
    console.error('Error searching destinations:', error)
  }
}

async function validateDestination() {
  if (!destinationInput.value.trim()) {
    destinationError.value = 'Please enter a destination'
    return
  }
  
  isValidatingDestination.value = true
  destinationError.value = ''
  isValidDestination.value = false
  
  try {
    // Call an API or service to validate if the input is a valid city or country
    // For this example, we'll use a geocoding API
    const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(destinationInput.value)}`)
    
    if (response.ok) {
      const data = await response.json()
      
      if (data.length > 0) {
        // Check if the result is a city or country
        const validTypes = ['city', 'town', 'village', 'country', 'state']
        const isValid = data.some(item => {
          if (item.type && validTypes.includes(item.type)) return true
          if (item.class === 'place' || item.class === 'boundary') return true
          return false
        })
        
        if (isValid) {
          isValidDestination.value = true
          // Create a destination object similar to what we would have had with AI recommendations
          selectedDestination.value = {
            id: new Date().getTime(), // Generate a unique ID
            name: destinationInput.value,
            description: `Trip to ${destinationInput.value}`,
            type: data[0].type || 'location'
          }
        } else {
          destinationError.value = 'Please enter a valid city or country'
        }
      } else {
        destinationError.value = 'Destination not found. Please enter a valid city or country'
      }
    } else {
      destinationError.value = 'Error validating destination. Please try again'
    }
  } catch (error) {
    console.error('Error validating destination:', error)
    destinationError.value = 'Error validating destination. Please try again'
  } finally {
    isValidatingDestination.value = false
  }
}

async function confirmDestination() {
  if (!isValidDestination.value) {
    destinationError.value = 'Please validate your destination first'
    return
  }
  
  try {
    // Get groupId from route params
    const groupId = route.params.groupId
    
    // Get stored trip dates
    const tripStartDate = localStorage.getItem('tripStartDate')
    const tripEndDate = localStorage.getItem('tripEndDate')
    
    if (!tripStartDate || !tripEndDate) {
      destinationError.value = 'Trip dates are missing'
      return
    }
    
    // Get user ID from local storage or other source
    const userId = localStorage.getItem('userId') || currentUserId.value
    
    if (!userId) {
      destinationError.value = 'User ID is missing'
      return
    }
    
    // Create the trip using the trip-management service
    const response = await fetch('http://localhost:5005/api/trips', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        city: selectedDestination.value.name,
        start_date: tripStartDate,
        end_date: tripEndDate,
        group_id: groupId
      })
    })
    
    if (response.ok) {
      const tripData = await response.json()
      console.log('Trip created successfully:', tripData)
      
      // Store trip ID for use in the planning page
      localStorage.setItem('currentTripId', tripData.id)
      
      // Update UI confirmation state if needed
      if (typeof destinationConfirmed !== 'undefined') {
        destinationConfirmed.value = true
      }
      
      // Redirect to the trip planning page
      router.push({
        name: 'trip-planning',
        params: { tripId: tripData.id }
      })
    } else {
      const errorData = await response.json()
      console.error('Error creating trip:', errorData)
      destinationError.value = `Error creating trip: ${errorData.error || 'Please try again'}`
    }
  } catch (error) {
    console.error('Error confirming destination:', error)
    destinationError.value = 'Error creating trip. Please try again'
  }
}

async function fetchGroupMembers() {
  try {
    // Get groupId from route params
    const groupId = route.params.groupId
    
    // First, fetch the group details to get user IDs
    const groupResponse = await fetch(`http://localhost:5003/api/groups/${groupId}`);
    if (!groupResponse.ok) {
      throw new Error('Failed to fetch group details');
    }
    
    const groupData = await groupResponse.json();
    const userIds = groupData.UserIds || [];
    
    if (!userIds.length) {
      console.error('No users found in the group');
      groupMembers.value = [];
      return;
    }
    
    // Fetch user details for each user ID in the group
    const memberPromises = userIds.map(userId => 
      fetch(`http://localhost:5001/api/users/${userId}`).then(res => {
        if (!res.ok) {
          throw new Error(`Failed to fetch user with ID ${userId}`);
        }
        return res.json();
      })
    );
    
    const members = await Promise.all(memberPromises);
    
    // Get the calendar for this group
    const calendarResponse = await fetch(`http://localhost:5004/api/calendars/group/${groupId}`);
    
    if (calendarResponse.ok) {
      const calendarData = await calendarResponse.json();
      // Store calendar ID for later use
      const calendarId = calendarData.id;
      localStorage.setItem('currentCalendarId', calendarId);
      
      // Get availability data from the calendar
      const availabilityData = {
        availabilities: calendarData.user_availabilities || []
      };
      
      // Map availability data to group members
      groupMembers.value = members.map(member => {
        const memberAvailability = availabilityData.availabilities.find(
          a => a.user_id === member.id
        );
        
        return {
          ...member,
          availability: memberAvailability ? true : false,
          availableDates: memberAvailability ? memberAvailability.available_dates : []
        };
      });
      
      // Calculate availability heatmap after fetching members
      calculateAvailabilityHeatmap();
    } else {
      // If there's no calendar data yet, just use the member data
      groupMembers.value = members.map(member => ({
        ...member,
        availability: false,
        availableDates: []
      }));
    }
  } catch (error) {
    console.error('Error fetching group members:', error);
  }
}

// Calculate availability heatmap from all members' available dates
function calculateAvailabilityHeatmap() {
  const heatmap = {};
  
  // Initialize the heatmap with the calendar date range
  if (calendar.value) {
    const startDate = new Date(minDate.value);
    const endDate = new Date(maxDate.value);
    
    const currentDate = new Date(startDate);
    while (currentDate <= endDate) {
      const dateStr = currentDate.toISOString().split('T')[0];
      heatmap[dateStr] = 0;
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    // Count how many members are available for each date
    groupMembers.value.forEach(member => {
      if (member.availableDates && member.availableDates.length > 0) {
        member.availableDates.forEach(date => {
          if (heatmap[date] !== undefined) {
            heatmap[date]++;
          }
        });
      }
    });
    
    availabilityHeatmap.value = heatmap;
    findBestDateRanges();
  }
}

// Find the best continuous date ranges where most members are available
function findBestDateRanges() {
  const heatmap = availabilityHeatmap.value;
  const totalMembers = groupMembers.value.length;
  const duration = dateRangeDuration.value;
  
  if (!heatmap || Object.keys(heatmap).length === 0) return;
  
  const dates = Object.keys(heatmap).sort();
  if (dates.length < duration) return;
  
  const ranges = [];
  
  // Loop through possible start dates
  for (let i = 0; i <= dates.length - duration; i++) {
    const startDate = dates[i];
    const endDate = dates[i + duration - 1];
    
    // Calculate average availability for this range
    let total = 0;
    for (let j = i; j < i + duration; j++) {
      total += heatmap[dates[j]];
    }
    const averageAvailability = total / duration;
    const percentAvailable = (averageAvailability / totalMembers) * 100;
    
    ranges.push({
      startDate,
      endDate,
      averageAvailability,
      percentAvailable,
      score: averageAvailability // We can make this more complex if needed
    });
  }
  
  // Sort by score in descending order
  ranges.sort((a, b) => b.score - a.score);
  
  // Take top 5 or less
  bestDateRanges.value = ranges.slice(0, 5);
  
  // If we have ranges, select the first one by default
  if (bestDateRanges.value.length > 0) {
    selectedDateRange.value = bestDateRanges.value[0];
  }
}

// Update date range duration and recalculate best ranges
function updateDateRangeDuration(days) {
  dateRangeDuration.value = days;
  findBestDateRanges();
}

// Select a recommended date range
function selectDateRange(range) {
  selectedDateRange.value = range;
  tripDates.start = range.startDate;
  tripDates.end = range.endDate;
}

// Set trip dates based on selected range and move to next step
function confirmTripDates() {
  if (!tripDates.start || !tripDates.end) return;
  
  localStorage.setItem('tripStartDate', tripDates.start);
  localStorage.setItem('tripEndDate', tripDates.end);
  
  currentStep.value = steps.SELECT_DESTINATION;
  fetchAIRecommendations();
}

async function updateUserAvailability(userId, isAvailable) {
  try {
    const calendarId = localStorage.getItem('currentCalendarId');
    if (!calendarId) {
      console.error('No calendar ID found');
      return;
    }
    
    // Get date range from calendar's range
    const availableDates = isAvailable
      ? generateDateRange(new Date(minDate.value), new Date(maxDate.value))
      : [];
    
    // Update tempSelectedDates for the UI
    tempSelectedDates.value = [...availableDates];
    
    const response = await fetch(`http://localhost:5004/api/calendars/${calendarId}/availability`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        available_dates: availableDates
      })
    });
    
    if (response.ok) {
      // Update local state
      const member = groupMembers.value.find(m => m.id === userId);
      if (member) {
        member.availability = isAvailable;
        member.availableDates = availableDates;
      }
      
      // If we've just set availability to true, show the date selector
      if (isAvailable) {
        showDateSelector.value = true;
      } else {
        showDateSelector.value = false;
      }
    } else {
      console.error('Failed to update availability');
    }
  } catch (error) {
    console.error('Error updating availability:', error);
  }
}

// Helper function to generate array of dates within range
function generateDateRange(startDate, endDate) {
  const dates = [];
  const currentDate = new Date(startDate);
  
  while (currentDate <= endDate) {
    dates.push(new Date(currentDate).toISOString().split('T')[0]);
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
}

function goBackToGroups() {
  router.push({ name: 'groups' });
}
</script>