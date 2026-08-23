<script setup lang="ts">
/** 文章详情：markdown 渲染展示；url 类型自动跳转 */
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DOMPurify from 'dompurify'
import { marked } from 'marked'
import { api, type ArticleDetail } from '@/api'

const route = useRoute()
const router = useRouter()
const article = ref<ArticleDetail | null>(null)
const loading = ref(true)
const notFound = ref(false)

onMounted(async () => {
  try {
    article.value = await api.getArticle(Number(route.params.id))
    // url 类型文章：直接跳转到目标地址
    if (article.value.article_type === 'url') {
      window.location.href = article.value.content
    }
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
})

/** markdown → HTML（净化防 XSS） */
const html = computed(() => {
  if (!article.value || article.value.article_type !== 'markdown') return ''
  return DOMPurify.sanitize(marked.parse(article.value.content) as string)
})

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<template>
  <div class="detail-page">
    <header class="detail-header">
      <el-button text @click="router.push('/')">
        <el-icon style="margin-right: 4px"><ArrowLeft /></el-icon>
        返回首页
      </el-button>
    </header>

    <main v-loading="loading" class="detail-main leaf-card">
      <el-empty v-if="notFound" description="文章不存在" />
      <template v-else-if="article">
        <h1 class="detail-title font-serif">{{ article.title }}</h1>
        <div class="detail-meta">发布于 {{ formatDate(article.created_at) }}</div>
        <div class="markdown-body" v-html="html"></div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.detail-header {
  width: min(860px, 92vw);
  margin: 18px auto 0;
}

.detail-main {
  width: min(860px, 92vw);
  margin: 18px auto 48px;
  padding: 36px 44px;
}

.detail-title {
  margin: 0 0 8px;
  font-size: 26px;
  color: var(--leaf-deep);
  line-height: 1.5;
}

.detail-meta {
  color: var(--ink-light);
  font-size: 13px;
  margin-bottom: 26px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--leaf-line);
}

@media (max-width: 600px) {
  .detail-main {
    padding: 24px 18px;
  }
}
</style>
