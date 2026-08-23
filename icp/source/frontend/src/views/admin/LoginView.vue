<script setup lang="ts">
/** 管理员登录页 */
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const form = ref({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

/** 登录成功后跳回来源页或后台首页 */
async function submit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await auth.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push((route.query.redirect as string) ?? '/admin')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card leaf-card">
      <div class="login-title font-serif">🌿 拾叶集 · 后台管理</div>
      <div class="login-sub">仅管理员可登录</div>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        @keyup.enter="submit"
      >
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            class="login-btn"
            type="primary"
            :loading="loading"
            round
            @click="submit"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-back">
        <router-link to="/">← 回到首页</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(900px 400px at 70% 20%, rgba(127, 162, 137, 0.25), transparent 60%),
    radial-gradient(700px 380px at 20% 85%, rgba(127, 162, 137, 0.18), transparent 60%),
    var(--paper-bg);
}

.login-card {
  width: 380px;
  padding: 40px 36px 28px;
}

.login-title {
  font-size: 21px;
  color: var(--leaf-deep);
  text-align: center;
  font-weight: 700;
}

.login-sub {
  text-align: center;
  color: var(--ink-light);
  font-size: 13px;
  margin: 6px 0 26px;
}

.login-btn {
  width: 100%;
}

.login-back {
  text-align: center;
  font-size: 13px;
  margin-top: 4px;
}
</style>
