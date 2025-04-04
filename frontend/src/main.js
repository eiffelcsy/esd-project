import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import './assets/index.css'

// Set the base URL for Axios
axios.defaults.baseURL = 'http://localhost:8000';

// Create the Vue app
const app = createApp(App);
const pinia = createPinia();

// Use the router
app.use(pinia);
app.use(router);

// Initialize user session
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()
userStore.initializeSession()

// Mount the app
app.mount('#app'); 