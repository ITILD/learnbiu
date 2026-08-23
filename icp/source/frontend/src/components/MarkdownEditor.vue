<script setup lang="ts">
/** 最简 Markdown 编辑器：轻量工具栏 + 文本域 + 实时预览 */
import { computed, nextTick, ref } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps<{ modelValue: string; placeholder?: string }>()
const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

const preview = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const value = computed({
  get: () => props.modelValue,
  set: (v: string) => emit('update:modelValue', v),
})

/** 在光标处插入语法（包裹选中文本） */
function insert(before: string, after = '', placeholder = '') {
  const el = textareaRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const selected = el.value.slice(start, end) || placeholder
  value.value = el.value.slice(0, start) + before + selected + after + el.value.slice(end)
  nextTick(() => {
    el.focus()
    el.selectionStart = start + before.length
    el.selectionEnd = start + before.length + selected.length
  })
}

/** 在光标所在行行首插入（标题 / 引用 / 列表） */
function insertLineStart(prefix: string) {
  const el = textareaRef.value
  if (!el) return
  const start = el.selectionStart
  const lineStart = el.value.lastIndexOf('\n', start - 1) + 1
  value.value = el.value.slice(0, lineStart) + prefix + el.value.slice(lineStart)
  nextTick(() => {
    el.focus()
    el.selectionStart = el.selectionEnd = start + prefix.length
  })
}

/** 工具栏动作 */
const actions = [
  { label: 'B', title: '粗体', handler: () => insert('**', '**', '粗体') },
  { label: 'I', title: '斜体', handler: () => insert('*', '*', '斜体') },
  { label: 'H', title: '标题', handler: () => insertLineStart('## ') },
  { label: '❝', title: '引用', handler: () => insertLineStart('> ') },
  { label: '•', title: '列表', handler: () => insertLineStart('- ') },
  { label: '</>', title: '行内代码', handler: () => insert('`', '`', 'code') },
  { label: '{}', title: '代码块', handler: () => insert('\n```\n', '\n```\n', '代码块') },
  { label: '🔗', title: '链接', handler: () => insert('[', '](https://)', '链接文字') },
  { label: '🖼', title: '图片', handler: () => insert('![', '](图片地址)', '描述') },
]

/** 预览 HTML（DOMPurify 净化防 XSS） */
const previewHtml = computed(() =>
  DOMPurify.sanitize(marked.parse(props.modelValue ?? '') as string),
)
</script>

<template>
  <div class="md-editor">
    <!-- 工具栏 -->
    <div class="md-toolbar">
      <button
        v-for="a in actions"
        :key="a.title"
        type="button"
        class="md-btn"
        :title="a.title"
        @click="a.handler"
      >
        {{ a.label }}
      </button>
      <button
        type="button"
        class="md-btn md-preview-btn"
        :class="{ active: preview }"
        @click="preview = !preview"
      >
        {{ preview ? '继续编辑' : '预览' }}
      </button>
    </div>

    <!-- 编辑区 / 预览区 -->
    <div class="md-body" :class="{ 'has-preview': preview }">
      <textarea
        ref="textareaRef"
        v-model="value"
        class="md-textarea"
        :placeholder="placeholder ?? '支持 Markdown 语法…'"
      ></textarea>
      <div v-if="preview" class="md-preview markdown-body" v-html="previewHtml"></div>
    </div>
  </div>
</template>

<style scoped>
.md-editor {
  border: 1px solid var(--leaf-line);
  border-radius: 8px;
  overflow: hidden;
  background: var(--paper-card);
}

.md-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 6px 8px;
  border-bottom: 1px solid var(--leaf-line);
  background: var(--el-color-primary-light-9);
}

.md-btn {
  border: 1px solid transparent;
  background: transparent;
  border-radius: 4px;
  min-width: 28px;
  height: 26px;
  padding: 0 6px;
  font-size: 13px;
  color: var(--leaf-deep);
  cursor: pointer;
}

.md-btn:hover {
  background: var(--leaf-pale);
}

.md-preview-btn {
  margin-left: auto;
}

.md-preview-btn.active {
  background: var(--leaf-primary);
  color: #fff;
}

.md-body {
  display: flex;
}

.md-body.has-preview .md-textarea {
  border-right: 1px solid var(--leaf-line);
}

.md-textarea {
  flex: 1;
  min-height: 260px;
  padding: 12px 14px;
  border: none;
  outline: none;
  resize: vertical;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.7;
  color: var(--ink);
  background: transparent;
  box-sizing: border-box;
  width: 100%;
}

.md-preview {
  flex: 1;
  padding: 12px 16px;
  overflow-y: auto;
  max-height: 480px;
  background: #fff;
}
</style>
