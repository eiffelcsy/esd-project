<template>
  <div class="container mx-auto px-8">
    <h1 class="text-4xl">Trip Planning</h1>
    <nav>
      <Button variant="link"><a href="/finances">Go to Finances</a></Button>
      <Button variant="link"><a href="/memories">Go to Memories</a></Button>
    </nav>
    <br/>
    <div class="mx-auto max-w-xl">
      <form class="w-full" @submit.prevent="createTrip">
      <Input v-model="trip.destination" placeholder="Destination" required />
      <Input v-model="trip.startDate" type="date" required />
      <Input v-model="trip.endDate" type="date" required />
      <Button type="submit">Create Trip</Button>
    </form>
    </div>
    <div v-if="recommendations.length">
      <h2>Itinerary Recommendations</h2>
      <ul>
        <li v-for="item in recommendations" :key="item.id">{{ item.name }}</li>
      </ul>
    </div>
    <Button class="w-full" @click="syncWithGoogleCalendar">Sync with Google Calendar</Button>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default {
  name: 'TripPlanning',
  components: {
    Button,
    Input
  },
  setup() {
    const trip = ref({ destination: '', startDate: '', endDate: '' });
    const recommendations = ref([]);

    const createTrip = async () => {
      try {
        await axios.post('/trip', trip.value);
        const response = await axios.get('/trip/recommendations');
        recommendations.value = response.data;
      } catch (error) {
        console.error('Error creating trip:', error);
      }
    };

    const syncWithGoogleCalendar = async () => {
      try {
        await axios.post('/trip/sync');
        alert('Trip synced with Google Calendar!');
      } catch (error) {
        console.error('Error syncing with Google Calendar:', error);
      }
    };

    return { trip, recommendations, createTrip, syncWithGoogleCalendar };
  },
};
</script> 