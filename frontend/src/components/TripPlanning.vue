<template>
  <div class="flex flex-col">
    <nav>
      <Button variant="link"><a href="/finances">Go to Finances</a></Button>
      <Button variant="link"><a href="/memories">Go to Memories</a></Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Trip Planning</h1>
      
      <!-- Create Trip Card - Only shown if no trip has been created -->
      <Card v-if="!tripCreated">
        <CardHeader>
          <CardTitle>Add a new trip</CardTitle>
        </CardHeader>
        <CardContent>
          <form class="w-full gap-4 flex flex-col" @submit.prevent="createTrip">
            <Input
              v-model="trip.destination"
              placeholder="Destination"
              required
            />
            <div class="flex gap-4">
              <Input v-model="trip.startDate" type="date" required />
              <Input v-model="trip.endDate" type="date" required />
            </div>
            <Button type="submit">Create Trip</Button>
          </form>
        </CardContent>
      </Card>
      
      <!-- Trip Summary Card - Shown after trip has been created -->
      <Card v-if="tripCreated" class="mt-4">
        <CardHeader>
          <CardTitle>Your Trip</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="font-semibold">Destination:</span>
              <span>{{ trip.destination }}</span>
            </div>
            <div class="flex justify-between">
              <span class="font-semibold">Dates:</span>
              <span>{{ trip.startDate }} to {{ trip.endDate }}</span>
            </div>
          </div>
          <div class="mt-4 flex justify-end">
            <Button variant="outline" size="sm" @click="resetTrip">Start New Trip</Button>
          </div>
        </CardContent>
      </Card>
      
      <!-- Itinerary Card -->
      <Card v-if="itinerary.length" class="mt-4">
        <CardHeader>
          <CardTitle>Your Itinerary</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div v-for="(item, index) in itinerary" :key="index" class="p-3 border rounded">
              <div class="font-semibold">Day {{ index + 1 }} - {{ item.date }}</div>
              <div class="ml-4 space-y-1">
                <div v-for="(activity, actIndex) in item.activities" :key="actIndex" class="flex justify-between">
                  <span>{{ activity.time }}: {{ activity.description }}</span>
                  <span class="text-gray-500">{{ activity.location }}</span>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-4">
            <Button @click="addCustomActivity">Add Custom Activity</Button>
          </div>
        </CardContent>
      </Card>
      
      <!-- Recommendations Card -->
      <Card v-if="recommendations.length" class="mt-4">
        <CardHeader>
          <CardTitle>Recommendations</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div v-for="(item, index) in recommendations" :key="index" class="p-3 border rounded">
              <div class="font-semibold">{{ item.type }}</div>
              <div class="ml-4">{{ item.name }} - {{ item.description }}</div>
              <div class="flex justify-end mt-2">
                <Button size="sm" variant="outline" @click="addToItinerary(item)">Add to Itinerary</Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Button class="w-full mt-4" @click="syncWithGoogleCalendar">Sync with Google Calendar</Button>
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

// Mock data for offline development
const mockRecommendations = [
  {
    id: 1,
    type: "Attraction",
    name: "Eiffel Tower",
    description: "Iconic iron tower with stunning city views",
    location: "Champ de Mars, Paris"
  },
  {
    id: 2,
    type: "Restaurant",
    name: "Le Jules Verne",
    description: "High-end French cuisine with panoramic views",
    location: "Eiffel Tower, 2nd floor"
  },
  {
    id: 3,
    type: "Museum",
    name: "Louvre Museum",
    description: "World's largest art museum & historic monument",
    location: "Rue de Rivoli, Paris"
  }
];

const mockItinerary = [
  {
    date: "2023-10-15",
    activities: [
      { time: "09:00", description: "Breakfast at hotel", location: "Hotel" },
      { time: "11:00", description: "Visit Louvre Museum", location: "Rue de Rivoli" },
      { time: "15:00", description: "Coffee break", location: "Café de Flore" }
    ]
  },
  {
    date: "2023-10-16",
    activities: [
      { time: "10:00", description: "Visit Eiffel Tower", location: "Champ de Mars" },
      { time: "13:00", description: "Lunch at local bistro", location: "Le Petit Parisien" }
    ]
  }
];

export default {
  name: "TripPlanning",
  components: {
    Button,
    Input,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
  },
  setup() {
    const trip = ref({ destination: "", startDate: "", endDate: "" });
    const recommendations = ref([]);
    const itinerary = ref([]);
    const isOfflineMode = ref(true); // Set to true to use mock data instead of API calls
    const tripCreated = ref(false); // Track whether a trip has been created

    const createTrip = async () => {
      try {
        if (!isOfflineMode.value) {
          // Real API call (when API is available)
          await axios.post("/trip", trip.value);
          const recResponse = await axios.get("/trip/recommendations");
          recommendations.value = recResponse.data;
          const itinResponse = await axios.get("/trip/itinerary");
          itinerary.value = itinResponse.data;
        } else {
          // Use mock data for offline development
          console.log("Using mock data (offline mode)");
          console.log("Trip created:", trip.value);
          
          // Simulate API delay
          await new Promise(resolve => setTimeout(resolve, 500));
          
          // Set mock recommendations
          recommendations.value = mockRecommendations;
          
          // Set mock itinerary
          itinerary.value = mockItinerary;
        }
        
        // Set tripCreated to true after successful creation
        tripCreated.value = true;
      } catch (error) {
        console.error("Error creating trip:", error);
        // Fallback to mock data if API call fails
        console.log("API call failed, falling back to mock data");
        recommendations.value = mockRecommendations;
        itinerary.value = mockItinerary;
        tripCreated.value = true; // Still consider trip created in offline mode
      }
    };

    const resetTrip = () => {
      // Reset all trip data and show the create trip form again
      trip.value = { destination: "", startDate: "", endDate: "" };
      recommendations.value = [];
      itinerary.value = [];
      tripCreated.value = false;
    };

    const addToItinerary = (item) => {
      if (!isOfflineMode.value) {
        // In a real app, this would call the itinerary service
        axios.post("/itinerary/add", item).catch(error => {
          console.error("Error adding to itinerary:", error);
        });
      }
      
      // Add to local itinerary data (works in both online and offline mode)
      if (itinerary.value.length > 0) {
        itinerary.value[0].activities.push({
          time: "12:00", // Default time
          description: `Visit ${item.name}`,
          location: item.location
        });
      }
    };

    const addCustomActivity = () => {
      // Add locally (works in both online and offline mode)
      if (itinerary.value.length > 0) {
        const newActivity = {
          time: "18:00",
          description: "Custom Activity",
          location: "Custom Location"
        };
        
        itinerary.value[0].activities.push(newActivity);
        
        // In a real app with API available, we would also sync with the backend
        if (!isOfflineMode.value) {
          axios.post("/itinerary/add-activity", newActivity).catch(error => {
            console.error("Error adding custom activity:", error);
          });
        }
      }
    };

    const syncWithGoogleCalendar = async () => {
      try {
        if (!isOfflineMode.value) {
          await axios.post("/trip/sync", itinerary.value);
        } else {
          // Mock response for offline mode
          console.log("Simulating sync with Google Calendar");
          await new Promise(resolve => setTimeout(resolve, 500));
        }
        alert("Trip synced with Google Calendar!");
      } catch (error) {
        console.error("Error syncing with Google Calendar:", error);
        alert("Offline mode: Trip would be synced with Google Calendar if API was available");
      }
    };

    return { 
      trip, 
      recommendations, 
      itinerary, 
      tripCreated, // Expose the new state to the template
      createTrip,
      resetTrip, // Add the new reset method to clear trip data
      syncWithGoogleCalendar, 
      addToItinerary, 
      addCustomActivity 
    };
  },
};
</script>
