<script setup lang="ts">
/** 首页：最近文章列表 + 右上角备忘日历入口 */
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, type ArticleBrief } from '@/api'
import { useAuthStore } from '@/stores/auth'
import MemoCalendar from '@/components/MemoCalendar.vue'
import ghsIcon from '@/assets/ghs.png'

const router = useRouter()
const auth = useAuthStore()

const articles = ref<ArticleBrief[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const memoVisible = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await api.getArticles({
      skip: (page.value - 1) * pageSize,
      limit: pageSize,
    })
    // 防御：/api 未反代/后端未启动时，SPA fallback 会返回 200 + HTML，
    // 此时 res.items 为 undefined，直接赋值会让模板 articles.length 崩溃白屏
    articles.value = res.items ?? []
    total.value = res.total ?? 0
  } finally {
    loading.value = false
  }
}
onMounted(load)

/** 点击文章：markdown 进详情页，url 新窗口跳转 */
function open(article: ArticleBrief) {
  if (article.article_type === 'url' && article.url) {
    window.open(article.url, '_blank', 'noopener')
  } else {
    router.push({ name: 'article-detail', params: { id: article.id } })
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/** 外链只展示域名，更雅观 */
function hostOf(url: string | null): string {
  if (!url) return ''
  try {
    return new URL(url).hostname
  } catch {
    return url
  }
}
</script>

<template>
  <div class="home">
    <!-- 顶栏：站名 + 备忘日历入口 -->
    <header class="site-header">
      <div class="site-brand font-serif" @click="router.push('/')">
        <span class="brand-mark">🌿</span>
        <span class="brand-name">拾叶集</span>
        <span class="brand-sub">技术小站 · 备忘手帐</span>
      </div>
      <div class="header-actions">
        <el-button round class="memo-btn" @click="memoVisible = true">
          <el-icon style="margin-right: 4px"><Calendar /></el-icon>
          备忘日历
        </el-button>
        <router-link v-if="auth.isLoggedIn" to="/admin" class="admin-link">管理</router-link>
        <router-link v-else to="/admin/login" class="admin-link">登录</router-link>
      </div>
    </header>

    <!-- 文章列表 -->
    <main class="article-area">
      <div class="section-head">
        <h2 class="font-serif">最近文章</h2>
        <span class="section-sub">拾一片叶，记一段事</span>
      </div>

      <div v-loading="loading" class="article-list">
        <el-empty
          v-if="!loading && articles.length === 0"
          description="还没有文章，去后台写一篇吧～"
        />
        <article
          v-for="a in articles"
          :key="a.id"
          class="article-item leaf-card"
          @click="open(a)"
        >
          <div class="item-title-row">
            <h3 class="item-title font-serif">{{ a.title }}</h3>
            <el-tag v-if="a.article_type === 'url'" size="small" effect="plain" type="success">
              外链
            </el-tag>
            <el-tag v-else size="small" effect="plain" type="primary">原创</el-tag>
          </div>
          <p class="item-excerpt">{{ a.article_type === 'url' ? hostOf(a.url) : a.excerpt }}</p>
          <div class="item-meta">{{ formatDate(a.created_at) }}</div>
        </article>
      </div>

      <div v-if="total > pageSize" class="pager">
        <el-pagination
          v-model:current-page="page"
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="total"
          background
          @current-change="load"
        />
      </div>
    </main>

    <!-- 页脚：左侧版权，右侧备案号 -->
    <footer class="site-footer">
      <span class="footer-copy">© 2026 拾叶集</span>
      <div class="footer-records">
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener">
          辽ICP备2026000762号-2
        </a>
        <!-- 公安备案号：登录后隐藏 -->
        <a
          v-if="!auth.isLoggedIn"
          href="https://beian.mps.gov.cn/#/query/webSearch?code=21029602001300"
          target="_blank"
          rel="noreferrer"
          class="police-record"
        >
          <img :src="ghsIcon" alt="公安备案徽标" class="police-record-icon" />
          辽公网安备21029602001300号
        </a>
      </div>
    </footer>

    <!-- 备忘日历抽屉 -->
    <el-drawer v-model="memoVisible" title="备忘日历" size="640px">
      <MemoCalendar />
    </el-drawer>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ---- 顶栏 ---- */
.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  padding: 14px 24px;
  background: rgba(246, 243, 234, 0.9);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--leaf-line);
}

.site-brand {
  display: flex;
  align-items: baseline;
  gap: 8px;
  cursor: pointer;
  color: var(--leaf-deep);
}

.brand-mark {
  font-size: 22px;
}

.brand-name {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 2px;
}

.brand-sub {
  font-size: 13px;
  color: var(--ink-light);
  letter-spacing: 1px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-link {
  font-size: 14px;
  color: var(--leaf-primary);
}

/* ---- 文章区 ---- */
.article-area {
  flex: 1;
  width: min(860px, 92vw);
  margin: 28px auto 40px;
}

.section-head {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
  font-size: 22px;
  color: var(--leaf-deep);
}

.section-sub {
  color: var(--ink-light);
  font-size: 13px;
  letter-spacing: 1px;
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 200px;
}

.article-item {
  padding: 18px 22px;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.article-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(45, 81, 57, 0.12);
}

.item-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-title {
  margin: 0;
  font-size: 18px;
  color: var(--leaf-deep);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-excerpt {
  margin: 8px 0 10px;
  color: var(--ink-light);
  font-size: 14px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-meta {
  font-size: 12.5px;
  color: var(--ink-light);
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* ---- 页脚 ---- */
.site-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px 16px;
  padding: 16px 24px;
  color: var(--ink-light);
  font-size: 13px;
  border-top: 1px solid var(--leaf-line);
  background: rgba(246, 243, 234, 0.6);
}

.footer-copy {
  letter-spacing: 1px;
}

.footer-records {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px 18px;
}

.site-footer a {
  color: var(--ink-light);
  text-decoration: none;
  transition: color 0.15s ease;
}

.police-record {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.police-record-icon {
  width: 14px;
  height: 14px;
  display: block;
}

.site-footer a:hover {
  color: var(--leaf-primary);
}

@media (max-width: 600px) {
  .brand-sub {
    display: none;
  }
}
</style>
