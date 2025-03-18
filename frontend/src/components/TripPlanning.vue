<template>
  <div class="flex flex-col">
    <nav class="flex gap-4 p-4">
      <Button variant="link">
        <router-link :to="{ name: 'trip-finances', params: { tripId: $route.params.tripId }}">Finances</router-link>
      </Button>
      <Button variant="link">
        <router-link :to="{ name: 'trip-memories', params: { tripId: $route.params.tripId }}">Memories</router-link>
      </Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Trip Planning</h1>
      
      <!-- Trip Summary Card -->
      <Card>
        <CardHeader>
          <CardTitle>Trip Details</CardTitle>
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
            <div class="flex justify-between">
              <span class="font-semibold">Group Size:</span>
              <span>{{ trip.groupSize }} members</span>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <!-- AI Recommendations Card -->
      <Card>
        <CardHeader>
          <CardTitle>AI Recommendations</CardTitle>
          <CardDescription>Based on your trip dates and destination</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="loadingRecommendations" class="text-center py-4">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
          </div>
          <div v-else-if="recommendations.length" class="space-y-4">
            <div v-for="category in groupedRecommendations" :key="category.type" class="space-y-2">
              <h3 class="font-semibold text-lg">{{ category.type }}</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div v-for="item in category.items" :key="item.id" class="border rounded-lg p-4">
                  <h4 class="font-medium">{{ item.name }}</h4>
                  <p class="text-sm text-gray-600 mt-1">{{ item.description }}</p>
                  <div class="mt-2 text-sm text-gray-500">
                    <p>Location: {{ item.location }}</p>
                    <p>Duration: {{ item.duration }}</p>
                    <p>Price Range: {{ item.priceRange }}</p>
                  </div>
                  <div class="mt-4 flex justify-end">
                    <Button size="sm" @click="addToItinerary(item)">Add to Itinerary</Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            No recommendations available yet. Try refreshing the page.
          </div>
        </CardContent>
      </Card>
      
      <!-- Itinerary Card -->
      <Card>
        <CardHeader>
          <CardTitle>Your Itinerary</CardTitle>
          <CardDescription>Plan your daily activities</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="itinerary.length" class="space-y-4">
            <div v-for="(day, index) in itinerary" :key="index" class="border rounded-lg p-4">
              <div class="flex justify-between items-center mb-2">
                <h3 class="font-semibold">Day {{ index + 1 }} - {{ formatDate(day.date) }}</h3>
                <Button variant="outline" size="sm" @click="addActivity(index)">Add Activity</Button>
              </div>
              <div class="space-y-2">
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
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            No activities planned yet. Add some from the recommendations above!
          </div>
        </CardContent>
      </Card>
      
      <!-- Export Options -->
      <div class="flex gap-4 justify-end mt-4">
        <Button variant="outline" @click="exportToGoogleCalendar">
          Export to Google Calendar
        </Button>
        <Button variant="outline" @click="exportToPDF">
          Export to PDF
        </Button>
      </div>
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
  </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { PencilIcon, TrashIcon } from "lucide-vue-next";

export default {
  name: "TripPlanning",
  components: {
    Button,
    Input,
    Label,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    CardDescription,
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    PencilIcon,
    TrashIcon,
  },
  setup() {
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

    const fetchTripDetails = async () => {
      try {
        const response = await axios.get(`/api/trips/${route.params.tripId}`);
        trip.value = response.data;
        await fetchRecommendations();
        await fetchItinerary();
      } catch (error) {
        console.error("Error fetching trip details:", error);
      }
    };

    const fetchRecommendations = async () => {
      loadingRecommendations.value = true;
      try {
        const response = await axios.get(`/api/trips/${route.params.tripId}/recommendations`);
        recommendations.value = response.data;
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      } finally {
        loadingRecommendations.value = false;
      }
    };

    const fetchItinerary = async () => {
      try {
        const response = await axios.get(`/api/trips/${route.params.tripId}/itinerary`);
        itinerary.value = response.data;
      } catch (error) {
        console.error("Error fetching itinerary:", error);
      }
    };

    const addToItinerary = async (item) => {
      try {
        const response = await axios.post(`/api/trips/${route.params.tripId}/itinerary/activities`, {
          ...item,
          time: "12:00", // Default time
        });
        await fetchItinerary();
      } catch (error) {
        console.error("Error adding activity to itinerary:", error);
      }
    };

    const addActivity = (dayIndex) => {
      currentDayIndex.value = dayIndex;
      isEditing.value = false;
      newActivity.value = {
        time: "",
        description: "",
        location: "",
      };
      showActivityModal.value = true;
    };

    const editActivity = (dayIndex, activityIndex) => {
      currentDayIndex.value = dayIndex;
      currentActivityIndex.value = activityIndex;
      isEditing.value = true;
      newActivity.value = { ...itinerary.value[dayIndex].activities[activityIndex] };
      showActivityModal.value = true;
    };

    const removeActivity = async (dayIndex, activityIndex) => {
      try {
        await axios.delete(`/api/trips/${route.params.tripId}/itinerary/activities/${activityIndex}`);
        await fetchItinerary();
      } catch (error) {
        console.error("Error removing activity:", error);
      }
    };

    const saveActivity = async () => {
      try {
        if (isEditing.value) {
          await axios.put(
            `/api/trips/${route.params.tripId}/itinerary/activities/${currentActivityIndex.value}`,
            newActivity.value
          );
        } else {
          await axios.post(
            `/api/trips/${route.params.tripId}/itinerary/activities`,
            newActivity.value
          );
        }
        showActivityModal.value = false;
        await fetchItinerary();
      } catch (error) {
        console.error("Error saving activity:", error);
      }
    };

    const exportToGoogleCalendar = async () => {
      try {
        await axios.post(`/api/trips/${route.params.tripId}/export/google-calendar`);
        // Handle success (e.g., show success message)
      } catch (error) {
        console.error("Error exporting to Google Calendar:", error);
      }
    };

    const exportToPDF = async () => {
      try {
        const response = await axios.get(`/api/trips/${route.params.tripId}/export/pdf`, {
          responseType: 'blob'
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `itinerary-${route.params.tripId}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (error) {
        console.error("Error exporting to PDF:", error);
      }
    };

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString();
    };

    onMounted(() => {
      fetchTripDetails();
    });

    return {
      trip,
      recommendations,
      itinerary,
      loadingRecommendations,
      groupedRecommendations,
      showActivityModal,
      isEditing,
      newActivity,
      addToItinerary,
      addActivity,
      editActivity,
      removeActivity,
      saveActivity,
      exportToGoogleCalendar,
      exportToPDF,
      formatDate,
    };
  },
};
</script>
