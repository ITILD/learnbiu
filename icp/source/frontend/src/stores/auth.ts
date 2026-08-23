/** 认证状态：JWT 持久化到 localStorage */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { api } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') ?? '')
  const username = ref(localStorage.getItem('username') ?? '')
  const role = ref(localStorage.getItem('role') ?? 'guest')

  /** 是否已登录（管理员） */
  const isLoggedIn = computed(() => token.value !== '')

  /** 登录并持久化凭证 */
  async function login(user: string, password: string) {
    const res = await api.login(user, password)
    token.value = res.access_token
    username.value = res.username
    role.value = res.role
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('username', res.username)
    localStorage.setItem('role', res.role)
  }

  /** 退出登录并清除凭证 */
  function logout() {
    token.value = ''
    username.value = ''
    role.value = 'guest'
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('role')
  }

  return { token, username, role, isLoggedIn, login, logout }
})
