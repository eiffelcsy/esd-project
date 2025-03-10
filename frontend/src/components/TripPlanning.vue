<template>
  <div class="flex flex-col">
    <nav>
      <Button variant="link"><a href="/finances">Go to Finances</a></Button>
      <Button variant="link"><a href="/memories">Go to Memories</a></Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Trip Planning</h1>
      <Card>
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
      <div v-if="recommendations.length">
        <h2>Itinerary Recommendations</h2>
        <ul>
          <li v-for="item in recommendations" :key="item.id">
            {{ item.name }}
          </li>
        </ul>
      </div>
      <Button class="w-full" @click="syncWithGoogleCalendar"
        >Sync with Google Calendar</Button
      >
    </div>
  </div>
</template>

<script>
import { ref } from "vue";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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

    const createTrip = async () => {
      try {
        await axios.post("/trip", trip.value);
        const response = await axios.get("/trip/recommendations");
        recommendations.value = response.data;
      } catch (error) {
        console.error("Error creating trip:", error);
      }
    };

    const syncWithGoogleCalendar = async () => {
      try {
        await axios.post("/trip/sync");
        alert("Trip synced with Google Calendar!");
      } catch (error) {
        console.error("Error syncing with Google Calendar:", error);
      }
    };

    return { trip, recommendations, createTrip, syncWithGoogleCalendar };
  },
};
</script>
