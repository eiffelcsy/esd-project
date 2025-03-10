import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import './assets/index.css'

// Set the base URL for Axios
axios.defaults.baseURL = 'http://localhost:8000';

// Create the Vue app
const app = createApp(App);

// Use the router
app.use(router);

// Mount the app
app.mount('#app'); 