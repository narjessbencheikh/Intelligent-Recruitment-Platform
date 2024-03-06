import Vue from 'vue';
import VueRouter from 'vue-router';
import ResumesComponent from '../components/ResumesComponent.vue';
import ResumeDetailsComponent from '../components/ResumeDetailsComponent.vue';
import HomeComponent from '../components/HomeComponent.vue';
import UploadComponent from '../components/UploadComponent.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeComponent,
  },
  {
    path: '/Resumes',
    name: 'Resumes',
    component: ResumesComponent,
  },
  {
    path: '/Details/:id',
    name: 'Details',
    component: ResumeDetailsComponent,
  },
  {
    path: '/upload',
    name: 'Upload',
    component: UploadComponent,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
