import { createRouter, createWebHistory } from 'vue-router';
import TripPlanning from '../components/TripPlanning.vue';
import Finances from '../components/Finances.vue';
import Memories from '../components/Memories.vue';

const routes = [
  { path: '/', redirect: '/trip' },
  { path: '/trip', component: TripPlanning },
  { path: '/finances', component: Finances },
  { path: '/memories', component: Memories },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router; 