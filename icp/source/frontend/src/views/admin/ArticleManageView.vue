<script setup lang="ts">
/** 文章管理：搜索 + 分页列表 + 新增/编辑（最简 Markdown 编辑器）/ 删除 */
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { api, type ArticleBrief, type ArticleType } from '@/api'
import MarkdownEditor from '@/components/MarkdownEditor.vue'

const items = ref<ArticleBrief[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const search = ref('')
const loading = ref(false)

// 新增 / 编辑弹窗
const dialogVisible = ref(false)
const editingId = ref<number | null>(null) // null 表示新增
const formRef = ref<FormInstance>()
const form = reactive({
  title: '',
  article_type: 'markdown' as ArticleType,
  content: '',
})

/** url 类型必须以 http(s):// 开头 */
const rules: FormRules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { max: 200, message: '标题最长 200 字', trigger: 'blur' },
  ],
  content: [
    {
      validator: (_rule, value: string, callback) => {
        if (form.article_type === 'url' && !/^https?:\/\/\S+/.test(value ?? '')) {
          callback(new Error('请输入以 http(s):// 开头的链接'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

async function load() {
  loading.value = true
  try {
    const res = await api.getArticles({
      skip: (page.value - 1) * pageSize,
      limit: pageSize,
      search: search.value,
    })
    // 防御：API 异常时 res.items 可能为 undefined，避免列表渲染崩溃
    items.value = res.items ?? []
    total.value = res.total ?? 0
  } finally {
    loading.value = false
  }
}
onMounted(load)

function openCreate() {
  editingId.value = null
  form.title = ''
  form.article_type = 'markdown'
  form.content = ''
  dialogVisible.value = true
}

/** 编辑：先拉取详情填充表单 */
async function openEdit(row: ArticleBrief) {
  const detail = await api.getArticle(row.id)
  editingId.value = row.id
  form.title = detail.title
  form.article_type = detail.article_type
  form.content = detail.content
  dialogVisible.value = true
}

/** 保存（新增或更新） */
async function save() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (editingId.value == null) {
    await api.createArticle({ ...form })
    ElMessage.success('文章已创建')
  } else {
    await api.updateArticle(editingId.value, { ...form })
    ElMessage.success('文章已更新')
  }
  dialogVisible.value = false
  load()
}

async function remove(row: ArticleBrief) {
  await ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '删除确认', {
    type: 'warning',
  })
  await api.deleteArticle(row.id)
  ElMessage.success('已删除')
  load()
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="manage-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <el-input
        v-model="search"
        placeholder="按标题搜索"
        clearable
        style="width: 240px"
        @keyup.enter="load"
        @clear="load"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-button type="primary" @click="openCreate">
        <el-icon style="margin-right: 4px"><Plus /></el-icon>新增文章
      </el-button>
    </div>

    <!-- 列表 -->
    <el-table v-loading="loading" :data="items" class="leaf-card data-table">
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
      <el-table-column label="类型" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.article_type === 'url'" size="small" effect="plain" type="success">
            外链
          </el-tag>
          <el-tag v-else size="small" effect="plain" type="primary">原创</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="120">
        <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        v-model:current-page="page"
        layout="total, prev, pager, next"
        :page-size="pageSize"
        :total="total"
        background
        @current-change="load"
      />
    </div>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId == null ? '新增文章' : '编辑文章'"
      width="860px"
      top="6vh"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="70px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="文章标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="类型">
          <el-radio-group v-model="form.article_type">
            <el-radio value="markdown">原创文章（Markdown）</el-radio>
            <el-radio value="url">外链跳转</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="正文" prop="content">
          <!-- markdown 类型：最简编辑器；url 类型：链接输入 -->
          <MarkdownEditor
            v-if="form.article_type === 'markdown'"
            v-model="form.content"
            placeholder="在这里写下你的文章，支持 Markdown 语法…"
            style="width: 100%"
          />
          <el-input
            v-else
            v-model="form.content"
            placeholder="https://example.com/post"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.data-table {
  width: 100%;
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 18px;
}
</style>
