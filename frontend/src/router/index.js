import { createRouter, createWebHistory } from 'vue-router';
import GroupManagement from '../components/GroupManagement.vue';
import TripIdeation from '../components/TripIdeation.vue';
import TripPlanning from '../components/TripPlanning.vue';
import Finances from '../components/Finances.vue';
import Memories from '../components/Memories.vue';
import AuthPage from '../components/AuthPage.vue';

const routes = [
  { path: '/login', component: AuthPage },
  { path: '/', redirect: '/groups' },
  { path: '/groups', component: GroupManagement },
  { 
    path: '/groups/:groupId/trip-ideation', 
    component: TripIdeation,
    name: 'trip-ideation'
  },
  { 
    path: '/trips/:tripId/planning', 
    component: TripPlanning,
    name: 'trip-planning'
  },
  { 
    path: '/trips/:tripId/finances', 
    component: Finances,
    name: 'trip-finances'
  },
  { 
    path: '/trips/:tripId/memories', 
    component: Memories,
    name: 'trip-memories'
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router; 