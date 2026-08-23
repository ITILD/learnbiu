<script setup lang="ts">
/** 后台布局：侧边导航 + 顶栏 + 内容区 */
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

/** 退出登录（确认后清除凭证） */
async function logout() {
  await ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
  auth.logout()
  router.push('/admin/login')
}
</script>

<template>
  <el-container class="admin-layout">
    <el-aside width="200px" class="admin-aside">
      <div class="admin-brand font-serif">🌿 拾叶集</div>
      <el-menu router :default-active="$route.path" class="admin-menu">
        <el-menu-item index="/admin/articles">
          <el-icon><Document /></el-icon>
          <span>文章管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/memos">
          <el-icon><Calendar /></el-icon>
          <span>备忘管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="admin-header">
        <div class="admin-title">后台管理</div>
        <div class="admin-user">
          <span class="admin-username">{{ auth.username }}</span>
          <el-button text type="danger" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="admin-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.admin-aside {
  background: var(--paper-card);
  border-right: 1px solid var(--leaf-line);
}

.admin-brand {
  font-size: 19px;
  font-weight: 700;
  color: var(--leaf-deep);
  padding: 20px 16px;
}

.admin-menu {
  border-right: none;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--paper-card);
  border-bottom: 1px solid var(--leaf-line);
  height: 56px;
}

.admin-title {
  font-weight: 600;
  color: var(--leaf-deep);
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.admin-username {
  color: var(--ink-light);
  font-size: 14px;
}

.admin-main {
  background: var(--paper-bg);
}
</style>
