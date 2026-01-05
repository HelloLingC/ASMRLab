import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/audio',
      name: 'audio',
      component: () => import('../views/AudioProcessView.vue'),
    },
    {
      path: '/player',
      name: 'player',
      component: () => import('../views/AudioPlayerView.vue'),
    },
    {
      path: '/srt-translator',
      name: 'srt-translator',
      component: () => import('../views/SrtTranslatorView.vue'),
    },
    {
      path: '/config',
      name: 'config',
      component: () => import('../views/ConfigView.vue'),
    },
  ],
})

export default router
