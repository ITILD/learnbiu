<script setup lang="ts">
/** 备忘管理：列表 + 新增/编辑/删除（按日期组织） */
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { api, type Memo } from '@/api'

const items = ref<Memo[]>([])
const loading = ref(false)

// 新增 / 编辑弹窗
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const form = reactive({
  title: '',
  content: '',
  memo_date: '',
})

const rules: FormRules = {
  title: [
    { required: true, message: '请输入备忘标题', trigger: 'blur' },
    { max: 200, message: '标题最长 200 字', trigger: 'blur' },
  ],
  memo_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
}

async function load() {
  loading.value = true
  try {
    items.value = await api.getMemos({ limit: 500 })
  } finally {
    loading.value = false
  }
}
onMounted(load)

/** 今天的日期（本地时区） */
function todayStr(): string {
  const d = new Date()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

function openCreate() {
  editingId.value = null
  form.title = ''
  form.content = ''
  form.memo_date = todayStr()
  dialogVisible.value = true
}

function openEdit(row: Memo) {
  editingId.value = row.id
  form.title = row.title
  form.content = row.content
  form.memo_date = row.memo_date
  dialogVisible.value = true
}

/** 保存（新增或更新） */
async function save() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  if (editingId.value == null) {
    await api.createMemo({ ...form })
    ElMessage.success('备忘已创建')
  } else {
    await api.updateMemo(editingId.value, { ...form })
    ElMessage.success('备忘已更新')
  }
  dialogVisible.value = false
  load()
}

async function remove(row: Memo) {
  await ElMessageBox.confirm(`确定删除「${row.title}」吗？`, '删除确认', {
    type: 'warning',
  })
  await api.deleteMemo(row.id)
  ElMessage.success('已删除')
  load()
}
</script>

<template>
  <div class="manage-page">
    <!-- 工具栏 -->
    <div class="toolbar">
      <span class="toolbar-tip">备忘按日期组织，会展示在首页的备忘日历中</span>
      <el-button type="primary" @click="openCreate">
        <el-icon style="margin-right: 4px"><Plus /></el-icon>新增备忘
      </el-button>
    </div>

    <!-- 列表 -->
    <el-table v-loading="loading" :data="items" class="leaf-card data-table">
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="content" label="内容" min-width="260" show-overflow-tooltip />
      <el-table-column prop="memo_date" label="日期" width="130" sortable />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增 / 编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="editingId == null ? '新增备忘' : '编辑备忘'"
      width="560px"
      destroy-on-close
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="70px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="备忘标题" maxlength="200" />
        </el-form-item>
        <el-form-item label="日期" prop="memo_date">
          <el-date-picker
            v-model="form.memo_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="5"
            maxlength="20000"
            placeholder="备忘详情（可选），日历周视图中会展示"
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

.toolbar-tip {
  color: var(--ink-light);
  font-size: 13px;
}

.data-table {
  width: 100%;
}
</style>
