/** 路由配置：前台 + 管理后台 */
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    {
      path: '/articles/:id',
      name: 'article-detail',
      component: () => import('@/views/ArticleDetailView.vue'),
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('@/views/admin/LoginView.vue'),
    },
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/articles' },
        {
          path: 'articles',
          name: 'admin-articles',
          component: () => import('@/views/admin/ArticleManageView.vue'),
        },
        {
          path: 'memos',
          name: 'admin-memos',
          component: () => import('@/views/admin/MemoManageView.vue'),
        },
      ],
    },
    // 其余路径回首页
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

// 守卫：管理后台需要登录
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return { name: 'admin-login', query: { redirect: to.fullPath } }
  }
})

export default router
