<template>
  <div class="space-y-6">
    <div v-if="loading" class="flex justify-center items-center py-8">
      <div class="animate-spin h-10 w-10 border-4 border-blue-500 rounded-full border-t-transparent"></div>
    </div>
    
    <div v-else-if="recommendations" class="space-y-8">
      <!-- Attractions -->
      <div v-if="recommendations.attractions && recommendations.attractions.length" class="space-y-4">
        <h2 class="text-xl font-semibold flex items-center gap-2">
          <Landmark class="h-5 w-5 text-blue-500" />
          Top Attractions
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="(attraction, index) in recommendations.attractions" :key="index" 
            class="border rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
            <div class="flex flex-col h-full">
              <h3 class="font-medium text-lg">{{ attraction.name }}</h3>
              <p v-if="attraction.suggested_day" class="text-sm font-medium text-blue-600 mt-1">
                Day {{ attraction.suggested_day }}
              </p>
              <p class="text-sm text-gray-600 mt-2 flex-grow">{{ attraction.description }}</p>
              <div class="mt-4 flex justify-end">
                <Button variant="outline" size="sm" @click="addToItinerary(attraction)">
                  Add to Itinerary
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Activities -->
      <div v-if="recommendations.activities && recommendations.activities.length" class="space-y-4">
        <h2 class="text-xl font-semibold flex items-center gap-2">
          <MapPin class="h-5 w-5 text-green-500" />
          Suggested Activities
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="(activity, index) in recommendations.activities" :key="index" 
            class="border rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
            <div class="flex flex-col h-full">
              <h3 class="font-medium text-lg">{{ activity.name }}</h3>
              <p v-if="activity.suggested_day" class="text-sm font-medium text-green-600 mt-1">
                Day {{ activity.suggested_day }}
              </p>
              <p class="text-sm text-gray-600 mt-2 flex-grow">{{ activity.description }}</p>
              <div class="mt-4 flex justify-end">
                <Button variant="outline" size="sm" @click="addToItinerary(activity)">
                  Add to Itinerary
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Restaurants -->
      <div v-if="recommendations.restaurants && recommendations.restaurants.length" class="space-y-4">
        <h2 class="text-xl font-semibold flex items-center gap-2">
          <UtensilsCrossed class="h-5 w-5 text-amber-500" />
          Recommended Restaurants
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="(restaurant, index) in recommendations.restaurants" :key="index" 
            class="border rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
            <div class="flex flex-col h-full">
              <div class="flex justify-between items-start">
                <h3 class="font-medium text-lg">{{ restaurant.name }}</h3>
                <span class="text-gray-500">{{ restaurant.price_range }}</span>
              </div>
              <p class="text-sm text-gray-600 mt-1">{{ restaurant.cuisine }} Cuisine</p>
              <div class="mt-4 flex justify-end">
                <Button variant="outline" size="sm" @click="addToItinerary(restaurant)">
                  Add to Itinerary
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Events -->
      <div v-if="recommendations.events && recommendations.events.length" class="space-y-4">
        <h2 class="text-xl font-semibold flex items-center gap-2">
          <Calendar class="h-5 w-5 text-purple-500" />
          Local Events
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="(event, index) in recommendations.events" :key="index" 
            class="border rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
            <div class="flex flex-col h-full">
              <h3 class="font-medium text-lg">{{ event.name }}</h3>
              <p class="text-sm font-medium text-purple-600 mt-1">
                {{ formatDate(event.date) }}
              </p>
              <p class="text-sm text-gray-600 mt-2 flex-grow">{{ event.description }}</p>
              <div class="mt-4 flex justify-end">
                <Button variant="outline" size="sm" @click="addToItinerary(event)">
                  Add to Itinerary
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Travel Tips -->
      <div v-if="recommendations.tips && recommendations.tips.length" class="space-y-4">
        <h2 class="text-xl font-semibold flex items-center gap-2">
          <LightbulbIcon class="h-5 w-5 text-yellow-500" /> 
          Insider Tips
        </h2>
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <ul class="space-y-2">
            <li v-for="(tip, index) in recommendations.tips" :key="index" 
                class="flex items-start gap-2">
              <span class="text-yellow-500 mt-1">•</span>
              <span class="text-gray-700">{{ tip }}</span>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- No recommendations state -->
      <div v-if="!hasRecommendations" class="text-center py-8">
        <div class="bg-gray-50 rounded-lg p-6 inline-block">
          <Info class="h-12 w-12 text-gray-400 mx-auto mb-3" />
          <h3 class="text-lg font-medium text-gray-700">No Recommendations Available</h3>
          <p class="text-gray-600 mt-2">We couldn't find any recommendations for your trip destination yet.</p>
          <Button class="mt-4" @click="$emit('refresh')">Refresh Recommendations</Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { 
  Landmark, 
  MapPin, 
  UtensilsCrossed,
  Calendar,
  Info,
  Lightbulb as LightbulbIcon
} from 'lucide-vue-next'

const props = defineProps({
  tripId: {
    type: [String, Number],
    required: true
  },
  destination: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  recommendations: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['add-to-itinerary', 'refresh'])

const hasRecommendations = computed(() => {
  const r = props.recommendations
  return (
    r && (
      (r.attractions && r.attractions.length > 0) ||
      (r.activities && r.activities.length > 0) ||
      (r.restaurants && r.restaurants.length > 0) ||
      (r.events && r.events.length > 0) ||
      (r.tips && r.tips.length > 0)
    )
  )
})

function addToItinerary(item) {
  emit('add-to-itinerary', {
    ...item,
    itemType: getItemType(item)
  })
}

function getItemType(item) {
  console.log("Getting item type for:", item);
  
  // Check if the item is in the attractions array
  if (props.recommendations.attractions && 
      props.recommendations.attractions.some(a => a.name === item.name)) {
    console.log(`Found "${item.name}" in attractions array`);
    return 'attraction';
  }
  
  // Check if the item is in the activities array
  if (props.recommendations.activities && 
      props.recommendations.activities.some(a => a.name === item.name)) {
    console.log(`Found "${item.name}" in activities array`);
    return 'activity';
  }
  
  // Check if the item is in the restaurants array
  if (props.recommendations.restaurants && 
      props.recommendations.restaurants.some(r => r.name === item.name)) {
    console.log(`Found "${item.name}" in restaurants array`);
    return 'restaurant';
  }
  
  // Check if the item is in the events array
  if (props.recommendations.events && 
      props.recommendations.events.some(e => e.name === item.name)) {
    console.log(`Found "${item.name}" in events array`);
    return 'event';
  }
  
  // If we can't determine the type, default to 'activity'
  console.log(`Could not determine type for "${item.name}", defaulting to activity`);
  return 'activity';
}

function formatDate(dateString) {
  if (!dateString) return ''
  
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    weekday: 'long',
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}
</script> 