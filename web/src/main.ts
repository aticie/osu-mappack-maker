import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

import axios from "axios";

if (import.meta.env.DEV) {
  axios.defaults.baseURL = "http://127.0.0.1:8000";
}

createApp(App).mount('#app')
