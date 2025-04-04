import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/stores/user';
import GroupManagement from '../components/GroupManagement.vue';
import TripIdeation from '../components/TripIdeation.vue';
import TripPlanning from '../components/TripPlanning.vue';
import Finances from '../components/Finances.vue';

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/components/AuthPage.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/components/DashboardPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/groups',
    name: 'groups',
    component: () => import('@/components/GroupManagement.vue'),
    meta: { requiresAuth: true }
  },
  { path: '/groups/:groupId/trip-ideation', component: TripIdeation, name: 'trip-ideation' },
  { path: '/trips/:tripId/planning', component: TripPlanning, name: 'trip-planning' },
  { path: '/trips/:tripId/finances', component: Finances, name: 'trip-finances' }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && userStore.isAuthenticated) {
    next('/dashboard');
  } else {
    next();
  }
});

export default router; 