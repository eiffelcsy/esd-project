<template>
  <div class="flex flex-col container mx-auto">
    <nav class="flex gap-4 p-4 justify-between items-center mb-4">
      <Button variant="link">
        <router-link :to="{ name: 'trip-finances', params: { tripId: $route.params.tripId }}">Finances</router-link>
      </Button>
      <Button variant="secondary">
        <ArrowLeft class="h-4 w-4 mr-1" />
        <router-link to="/groups">Back to Groups</router-link>
      </Button>
    </nav>
    <div class="my-8 flex flex-col gap-4 container px-8 mx-auto">
      <div class="flex justify-between items-center">
        <h1 class="text-4xl font-semibold">Trip Planning</h1>
        <Button 
          @click="refreshData" 
          variant="outline"
          class="flex items-center gap-1"
        >
          <RefreshCw class="h-4 w-4" />
          Refresh
        </Button>
      </div>
      
      <!-- Trip Summary Card -->
      <Card>
        <CardHeader>
          <CardTitle>Trip Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="font-semibold">Destination:</span>
              <span>{{ trip.city }}</span>
            </div>
            <div class="flex justify-between">
              <span class="font-semibold">Dates:</span>
              <span>{{ formatTripDate(trip.start_date) }} to {{ formatTripDate(trip.end_date) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="font-semibold">ID:</span>
              <span>{{ trip.id }}</span>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <!-- AI Recommendations Card -->
      <Card>
        <CardHeader>
          <CardTitle>Destination Recommendations</CardTitle>
          <CardDescription>Smart suggestions for your trip to {{ trip.city }}</CardDescription>
        </CardHeader>
        <CardContent>
          <TripRecommendations
            :tripId="route.params.tripId"
            :destination="trip.city"
            :loading="loadingRecommendations"
            :recommendations="parsedRecommendations"
            @add-to-itinerary="addRecommendationToItinerary"
            @refresh="fetchRecommendations"
          />
        </CardContent>
      </Card>
      
      <!-- Itinerary Card -->
      <Card>
        <CardHeader>
          <CardTitle>Your Itinerary</CardTitle>
          <CardDescription>Plan your daily activities</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="formattedItinerary.length" class="space-y-4">
            <div v-for="(day, index) in formattedItinerary" :key="index" class="border rounded-lg p-4">
              <div class="flex justify-between items-center mb-2">
                <h3 class="font-semibold">Day {{ day.dayNumber }} - {{ formatDate(day.date) }}</h3>
                <Button variant="outline" size="sm" @click="addActivity(index)">Add Activity</Button>
              </div>
              <div v-if="day.activities.length > 0" class="space-y-2">
                <div v-for="(activity, actIndex) in day.activities" :key="actIndex" 
                     class="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div class="flex items-center gap-2">
                    <span class="font-medium">{{ activity.time }}</span>
                    <span>{{ activity.description }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-500">{{ activity.location }}</span>
                    <Button variant="ghost" size="sm" @click="editActivity(index, actIndex)">
                      <PencilIcon class="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" @click="removeActivity(index, actIndex)">
                      <TrashIcon class="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
              <div v-else class="p-4 text-gray-400 text-center italic">
                No activities planned for this day
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            Loading your itinerary...
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Activity Modal -->
    <Dialog v-model:open="showActivityModal">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{{ isEditing ? 'Edit Activity' : 'Add Activity' }}</DialogTitle>
          <DialogDescription>
            {{ isEditing ? 'Update the activity details below.' : 'Fill in the activity details below.' }}
          </DialogDescription>
        </DialogHeader>
        <form @submit.prevent="saveActivity" class="space-y-4">
          <div class="space-y-2">
            <Label for="time">Time</Label>
            <Input id="time" v-model="newActivity.time" type="time" required />
          </div>
          <div class="space-y-2">
            <Label for="description">Description</Label>
            <Input id="description" v-model="newActivity.description" required />
          </div>
          <div class="space-y-2">
            <Label for="location">Location</Label>
            <Input id="location" v-model="newActivity.location" required />
          </div>
          <div class="flex justify-end gap-2">
            <Button type="button" variant="outline" @click="showActivityModal = false">
              Cancel
            </Button>
            <Button type="submit">
              {{ isEditing ? 'Update' : 'Add' }} Activity
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>

    <!-- Notification -->
    <div v-if="notification.show" 
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50 flex items-center gap-2 transition-all duration-300 max-w-xs"
      :class="{
        'bg-green-50 border border-green-200 text-green-800': notification.type === 'success',
        'bg-red-50 border border-red-200 text-red-800': notification.type === 'error',
        'bg-blue-50 border border-blue-200 text-blue-800': notification.type === 'info'
      }"
    >
      <span v-if="notification.type === 'success'" class="h-5 w-5 text-green-500">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      </span>
      <span v-if="notification.type === 'error'" class="h-5 w-5 text-red-500">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
      </span>
      <span v-if="notification.type === 'info'" class="h-5 w-5 text-blue-500">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
      </span>
      <div class="text-sm font-medium">
        {{ notification.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { PencilIcon, TrashIcon, RefreshCw, ArrowLeft } from "lucide-vue-next";
import TripRecommendations from "@/components/TripRecommendations.vue";

const route = useRoute();
const trip = ref({});
const recommendations = ref([]);
const itinerary = ref([]);
const loadingRecommendations = ref(false);
const showActivityModal = ref(false);
const isEditing = ref(false);
const currentDayIndex = ref(null);
const currentActivityIndex = ref(null);
const newActivity = ref({
  time: "",
  description: "",
  location: "",
});

// Notification states
const notification = ref({
  show: false,
  message: '',
  type: 'success', // 'success', 'error', 'info'
  timeout: null
});

// Function to show a notification
function showNotification(message, type = 'success', duration = 3000) {
  // Clear any existing timeout
  if (notification.value.timeout) {
    clearTimeout(notification.value.timeout);
  }
  
  // Set notification data
  notification.value = {
    show: true,
    message,
    type,
    timeout: setTimeout(() => {
      notification.value.show = false;
    }, duration)
  };
}

// Parsed recommendations computed property
const parsedRecommendations = computed(() => {
  // If recommendations is just a raw array, check if it contains a recommendations object
  if (Array.isArray(recommendations.value) && recommendations.value.length > 0) {
    const rec = recommendations.value.find(r => r.recommendations);
    if (rec && rec.recommendations) {
      return rec.recommendations;
    }
  }
  
  // If recommendations is an object with a recommendations property
  if (recommendations.value && recommendations.value.recommendations) {
    return recommendations.value.recommendations;
  }
  
  // If recommendations is already in the expected structure
  if (recommendations.value && (
    recommendations.value.attractions || 
    recommendations.value.activities || 
    recommendations.value.restaurants || 
    recommendations.value.events ||
    recommendations.value.tips
  )) {
    return recommendations.value;
  }
  
  return {};
});

const groupedRecommendations = computed(() => {
  const groups = {};
  recommendations.value.forEach(item => {
    if (!groups[item.type]) {
      groups[item.type] = {
        type: item.type,
        items: []
      };
    }
    groups[item.type].items.push(item);
  });
  return Object.values(groups);
});

const formattedItinerary = computed(() => {
  // If trip has no start/end dates, return empty array
  if (!trip.value.start_date || !trip.value.end_date) {
    return [];
  }
  
  // Create an array of all dates between start and end of trip
  const startDate = new Date(trip.value.start_date);
  const endDate = new Date(trip.value.end_date);
  const allDays = [];
  
  // Calculate total number of days
  const dayDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
  
  // Create array with all days
  for (let i = 0; i < dayDiff; i++) {
    const currentDate = new Date(startDate);
    currentDate.setDate(startDate.getDate() + i);
    const dateStr = currentDate.toISOString().split('T')[0];
    
    // Find if there are activities for this day in the itinerary
    const dayItinerary = itinerary.value.find(day => day.date === dateStr);
    
    allDays.push({
      date: dateStr,
      dayNumber: i + 1, // Day number is 1-based
      activities: dayItinerary ? dayItinerary.activities : []
    });
  }
  
  return allDays;
});

const fetchTripDetails = async () => {
  try {
    const response = await fetch(`http://localhost:5005/api/trips/${route.params.tripId}`);
    if (!response.ok) throw new Error('Failed to fetch trip details');
    trip.value = await response.json();
  } catch (error) {
    console.error("Error fetching trip details:", error);
    showNotification('Failed to load trip details. Please try again later.', 'error');
  }
};

async function fetchRecommendations() {
  if (!trip.value.id) return;
  
  loadingRecommendations.value = true;
  let retries = 0;
  const maxRetries = 10;
  const retryDelay = 3000; // 3 seconds

  const tryFetch = async () => {
    try {
      const response = await fetch(`http://localhost:5002/api/recommendations/${trip.value.id}`);
      
      if (response.status === 404) {
        // If recommendations don't exist yet, request them
        if (retries === 0) {
          const createResponse = await fetch(`http://localhost:5002/api/recommendations`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              trip_id: trip.value.id,
              destination: trip.value.city,
              start_date: trip.value.start_date.split('T')[0],
              end_date: trip.value.end_date.split('T')[0]
            })
          });
          
          if (!createResponse.ok) {
            throw new Error('Failed to request recommendations');
          }
        }
        
        // If we haven't exceeded max retries, try again after delay
        if (retries < maxRetries) {
          retries++;
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          return tryFetch();
        } else {
          throw new Error('Recommendations not ready after maximum retries');
        }
      } else if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }
      
      const data = await response.json();
      recommendations.value = data.recommendations;
      loadingRecommendations.value = false;
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      loadingRecommendations.value = false;
      showNotification('Failed to fetch recommendations. Please try again later.', 'error');
    }
  };

  await tryFetch();
}

async function fetchItinerary() {
  try {
    const response = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch itinerary');
    }
    
    const data = await response.json();
    
    // Get the daily activities - handle both formats ("dailyActivities" or "daily_activities")
    let dailyActivities = {};
    if (data.dailyActivities) {
      dailyActivities = data.dailyActivities;
    } else if (data.daily_activities) {
      dailyActivities = data.daily_activities;
    }
    
    // Transform the API response into the expected format for the UI
    const formattedItinerary = [];
    
    if (dailyActivities && Object.keys(dailyActivities).length > 0) {
      Object.keys(dailyActivities).forEach((date) => {
        const activities = dailyActivities[date];
        
        if (Array.isArray(activities) && activities.length > 0) {
          formattedItinerary.push({
            date: date,
            activities: activities.map(activity => ({
              time: activity.time || "12:00",
              description: activity.name || activity.description || "Untitled Activity",
              location: activity.location || ""
            }))
          });
        }
      });
      
      // Sort by date
      formattedItinerary.sort((a, b) => new Date(a.date) - new Date(b.date));
    }
    
    // Update itinerary state
    itinerary.value = formattedItinerary;
  } catch (error) {
    console.error("Error fetching itinerary:", error);
    showNotification('Failed to load itinerary. Please try again later.', 'error');
  }
}

const refreshData = async () => {
  await Promise.all([
    fetchTripDetails(),
    fetchRecommendations(),
    fetchItinerary()
  ]);
};

const addToItinerary = async (item) => {
  try {
    const response = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}/add_recommended_activity`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        recommendation_id: item.id,
        date: new Date().toISOString().split('T')[0],
        time: "12:00",
        end_time: "14:00"
      }),
    });
    
    if (!response.ok) throw new Error('Failed to add activity to itinerary');
    await fetchItinerary();
  } catch (error) {
    console.error("Error adding activity to itinerary:", error);
    showNotification('Failed to add activity to itinerary. Please try again later.', 'error');
  }
};

const addActivity = (dayIndex) => {
  // Use the correct day date from the formattedItinerary
  const dayDate = formattedItinerary.value[dayIndex].date;
  
  // Find the matching day in the itinerary array, or create it if it doesn't exist
  let actualDayIndex = itinerary.value.findIndex(day => day.date === dayDate);
  
  if (actualDayIndex === -1) {
    // This day doesn't exist in the itinerary array yet, so add it
    itinerary.value.push({
      date: dayDate,
      activities: []
    });
    actualDayIndex = itinerary.value.length - 1;
  }
  
  currentDayIndex.value = actualDayIndex;
  isEditing.value = false;
  newActivity.value = {
    time: "",
    description: "",
    location: "",
  };
  showActivityModal.value = true;
};

const editActivity = (dayIndex, activityIndex) => {
  // Get the actual day from formattedItinerary
  const dayDate = formattedItinerary.value[dayIndex].date;
  const actualDayIndex = itinerary.value.findIndex(day => day.date === dayDate);
  
  if (actualDayIndex === -1) {
    console.error("Cannot edit activity: day not found in itinerary");
    return;
  }
  
  currentDayIndex.value = actualDayIndex;
  currentActivityIndex.value = activityIndex;
  isEditing.value = true;
  newActivity.value = { ...itinerary.value[actualDayIndex].activities[activityIndex] };
  showActivityModal.value = true;
};

const removeActivity = async (dayIndex, activityIndex) => {
  try {
    const dayDate = formattedItinerary.value[dayIndex].date;
    const actualDayIndex = itinerary.value.findIndex(day => day.date === dayDate);
    
    if (actualDayIndex === -1) {
      console.error("Cannot remove activity: day not found in itinerary");
      return;
    }
    
    const activity = itinerary.value[actualDayIndex].activities[activityIndex];
    const response = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}/activities`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        date: itinerary.value[actualDayIndex].date,
        time: activity.time,
        name: activity.description
      })
    });
    
    if (!response.ok) throw new Error('Failed to remove activity');
    await fetchItinerary();
  } catch (error) {
    console.error("Error removing activity:", error);
    showNotification('Failed to remove activity. Please try again later.', 'error');
  }
};

const saveActivity = async () => {
  try {
    const activityData = {
      name: newActivity.value.description,
      date: itinerary.value[currentDayIndex.value].date,
      time: newActivity.value.time,
      end_time: newActivity.value.time.split(':')[0] + ':' + (parseInt(newActivity.value.time.split(':')[1]) + 30).toString().padStart(2, '0'),
      location: newActivity.value.location,
      description: newActivity.value.description
    };

    if (isEditing.value) {
      const deleteResponse = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}/activities`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          date: itinerary.value[currentDayIndex.value].date,
          time: itinerary.value[currentDayIndex.value].activities[currentActivityIndex.value].time,
          name: itinerary.value[currentDayIndex.value].activities[currentActivityIndex.value].description
        })
      });
      
      if (!deleteResponse.ok) throw new Error('Failed to update activity');
      
      const addResponse = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}/activities`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(activityData)
      });
      
      if (!addResponse.ok) throw new Error('Failed to update activity');
    } else {
      const response = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}/activities`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(activityData)
      });
      
      if (!response.ok) throw new Error('Failed to add activity');
    }
    
    showActivityModal.value = false;
    await fetchItinerary();
  } catch (error) {
    console.error("Error saving activity:", error);
    showNotification('Failed to save activity. Please try again later.', 'error');
  }
};

const exportToGoogleCalendar = async () => {
  try {
    // This would need to be implemented on the backend
    alert("Export to Google Calendar functionality would need to be implemented on the backend");
  } catch (error) {
    console.error("Error exporting to Google Calendar:", error);
  }
};

const exportToPDF = async () => {
  try {
    // This would need to be implemented on the backend
    alert("Export to PDF functionality would need to be implemented on the backend");
  } catch (error) {
    console.error("Error exporting to PDF:", error);
  }
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString();
};

const formatTripDate = (date) => {
  if (!date) return 'N/A';
  return new Date(date).toLocaleDateString();
};

// Method to add recommendation to itinerary
async function addRecommendationToItinerary(item) {
  try {
    // Add a debug notification to identify what we're trying to add
    showNotification(`Adding ${item.name} to your itinerary...`, 'info');
    console.log("Adding recommendation to itinerary:", item);
    
    // Get the type of item first, as it affects date handling
    let type = item.itemType || 'attraction';
    
    // Get date from suggested_day if available, otherwise use the first day of the trip
    let date = '';
    if (item.suggested_day) {
      // Extract day number from "Day X" format
      const dayMatch = item.suggested_day.match(/Day (\d+)/);
      if (dayMatch && dayMatch[1]) {
        const dayNum = parseInt(dayMatch[1]) - 1;
        
        // Calculate the actual date based on trip start date
        if (trip.value.start_date) {
          const startDate = new Date(trip.value.start_date);
          startDate.setDate(startDate.getDate() + dayNum);
          date = startDate.toISOString().split('T')[0];
          console.log(`Calculated date from Day ${dayNum + 1}: ${date}`);
        }
      }
    } else if (type === 'event' && item.date) {
      // For events, use their specific date
      date = new Date(item.date).toISOString().split('T')[0];
      console.log(`Using event date: ${date}`);
    } else if (itinerary.value.length > 0) {
      // Fallback: Use the first day of the itinerary
      date = itinerary.value[0].date;
      console.log(`Using first day of itinerary: ${date}`);
    } else if (trip.value.start_date) {
      // Fallback: Use trip start date
      date = new Date(trip.value.start_date).toISOString().split('T')[0];
      console.log(`Using trip start date: ${date}`);
    } else {
      // Last resort: Use today
      date = new Date().toISOString().split('T')[0];
      console.log(`Using today's date: ${date}`);
    }

    // Find the index of this item in the recommendations array
    let index = -1;
    
    if (type === 'attraction' && parsedRecommendations.value.attractions) {
      index = parsedRecommendations.value.attractions.findIndex(a => a.name === item.name);
      console.log(`Found attraction at index: ${index}`);
    } else if (type === 'activity' && parsedRecommendations.value.activities) {
      index = parsedRecommendations.value.activities.findIndex(a => a.name === item.name);
      console.log(`Found activity at index: ${index}`);
    } else if (type === 'restaurant' && parsedRecommendations.value.restaurants) {
      index = parsedRecommendations.value.restaurants.findIndex(r => r.name === item.name);
      console.log(`Found restaurant at index: ${index}`);
    } else if (type === 'event' && parsedRecommendations.value.events) {
      index = parsedRecommendations.value.events.findIndex(e => e.name === item.name);
      console.log(`Found event at index: ${index}`);
    }
    
    // If we couldn't find the index, log a warning but still try with index 0
    if (index === -1) {
      console.warn(`Could not find index for ${item.name} of type ${type}. Using index 0 as fallback.`);
      console.log("Available items:", parsedRecommendations.value);
      index = 0;
    }

    // Prepare data for API call
    const activityData = {
      type: type,
      index: index,
      date: date,
      time: "12:00", // Default to noon
      end_time: "14:00" // Default 2-hour activity
    };
    
    console.log("Sending request data:", activityData);

    // Call the API
    const addActivityResponse = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}/add_recommended_activity`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(activityData)
    });

    const responseData = await addActivityResponse.json();
    console.log("API response:", responseData);

    if (!addActivityResponse.ok) {
      throw new Error(responseData.error || 'Failed to add recommendation to itinerary');
    }

    // Refresh the itinerary with a slight delay to ensure the backend has updated
    setTimeout(async () => {
      await fetchItinerary();
    }, 500);
    
    // Show success notification
    showNotification(`${item.name} added to your itinerary!`, 'success');
  } catch (error) {
    console.error('Error adding recommendation to itinerary:', error);
    showNotification(`Error: ${error.message}`, 'error');
  }
}

// Ensure itinerary has enough days
function ensureItineraryDays(requiredDays) {
  // If itinerary is empty, initialize it with days between trip start and end dates
  if (itinerary.value.length === 0 && trip.value.start_date && trip.value.end_date) {
    const startDate = new Date(trip.value.start_date);
    const endDate = new Date(trip.value.end_date);
    const dayDiff = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1;
    
    for (let i = 0; i < dayDiff; i++) {
      const date = new Date(startDate);
      date.setDate(date.getDate() + i);
      itinerary.value.push({
        date: date.toISOString().split('T')[0],
        activities: []
      });
    }
  }
  
  // If we still need more days
  if (itinerary.value.length < requiredDays) {
    const lastDate = itinerary.value.length > 0 
      ? new Date(itinerary.value[itinerary.value.length - 1].date)
      : new Date();
    
    for (let i = itinerary.value.length; i < requiredDays; i++) {
      const date = new Date(lastDate);
      date.setDate(date.getDate() + (i - itinerary.value.length + 1));
      itinerary.value.push({
        date: date.toISOString().split('T')[0],
        activities: []
      });
    }
  }
}

const saveItinerary = async () => {
  try {
    // Format itinerary data as expected by the backend
    const itineraryData = {
      trip_id: route.params.tripId,
      daily_activities: {}
    };
    
    // Convert the itinerary array to the expected format
    itinerary.value.forEach((day, index) => {
      itineraryData.daily_activities[day.date] = day.activities.map(activity => ({
        time: activity.time,
        name: activity.description,
        location: activity.location,
        notes: activity.notes || ''
      }));
    });
    
    // Send to the backend
    const saveResponse = await fetch(`http://localhost:5006/api/itinerary/${route.params.tripId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(itineraryData)
    });
    
    if (!saveResponse.ok) {
      throw new Error('Failed to save itinerary');
    }
    
    console.log('Itinerary saved successfully');
    showNotification('Itinerary saved successfully', 'success');
  } catch (error) {
    console.error('Error saving itinerary:', error);
    showNotification('Failed to save itinerary. Please try again later.', 'error');
  }
};

onMounted(async () => {
  await refreshData();
});
</script>
