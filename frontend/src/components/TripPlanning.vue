<template>
  <div>
    <h1>Trip Planning</h1>
    <form @submit.prevent="createTrip">
      <input v-model="trip.destination" placeholder="Destination" required />
      <input v-model="trip.startDate" type="date" required />
      <input v-model="trip.endDate" type="date" required />
      <button type="submit">Create Trip</button>
    </form>
    <div v-if="recommendations.length">
      <h2>Itinerary Recommendations</h2>
      <ul>
        <li v-for="item in recommendations" :key="item.id">{{ item.name }}</li>
      </ul>
    </div>
    <button @click="syncWithGoogleCalendar">Sync with Google Calendar</button>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

export default {
  name: 'TripPlanning',
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