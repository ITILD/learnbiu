/** API 封装：axios 实例 + 类型定义 + 接口函数 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// ---------- 类型定义 ----------

/** 文章类型：markdown 原创文章 / url 外链 */
export type ArticleType = 'markdown' | 'url'

export interface ArticleBrief {
  id: number
  title: string
  article_type: ArticleType
  url: string | null
  excerpt: string
  created_at: string
  updated_at: string
}

export interface ArticleDetail {
  id: number
  title: string
  article_type: ArticleType
  content: string
  created_at: string
  updated_at: string
}

export interface ArticlePage {
  items: ArticleBrief[]
  total: number
}

export interface Memo {
  id: number
  title: string
  content: string
  memo_date: string // YYYY-MM-DD
  created_at: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  username: string
  role: string
}

// ---------- axios 实例 ----------

export const http = axios.create({ baseURL: '/api', timeout: 20000 })

// 请求拦截：自动附带登录凭证
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// 响应拦截：统一错误提示；登录过期时清除凭证并对 GET 自动以游客身份重试一次
http.interceptors.response.use(
  (res) => res,
  async (err) => {
    const { config, response } = err
    if (response?.status === 401 && config && !config._retried) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('role')
      if (config.method === 'get') {
        config._retried = true
        delete config.headers.Authorization
        return http(config)
      }
    }
    const detail = response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : '请求失败，请稍后再试')
    return Promise.reject(err)
  },
)

// ---------- 接口函数 ----------

export const api = {
  /** 管理员登录 */
  async login(username: string, password: string): Promise<LoginResult> {
    const res = await http.post<LoginResult>('/auth/login', { username, password })
    return res.data
  },

  /** 当前访问者信息 */
  async me(): Promise<{ username: string; role: string }> {
    const res = await http.get('/auth/me')
    return res.data
  },

  /** 文章分页列表 */
  async getArticles(params: {
    skip?: number
    limit?: number
    search?: string
  }): Promise<ArticlePage> {
    const res = await http.get<ArticlePage>('/articles', { params })
    return res.data
  },

  /** 文章详情 */
  async getArticle(id: number): Promise<ArticleDetail> {
    const res = await http.get<ArticleDetail>(`/articles/${id}`)
    return res.data
  },

  /** 新建文章（管理员） */
  async createArticle(data: {
    title: string
    article_type: ArticleType
    content: string
  }): Promise<ArticleDetail> {
    const res = await http.post<ArticleDetail>('/articles', data)
    return res.data
  },

  /** 更新文章（管理员） */
  async updateArticle(
    id: number,
    data: { title?: string; article_type?: ArticleType; content?: string },
  ): Promise<ArticleDetail> {
    const res = await http.put<ArticleDetail>(`/articles/${id}`, data)
    return res.data
  },

  /** 删除文章（管理员） */
  async deleteArticle(id: number): Promise<void> {
    await http.delete(`/articles/${id}`)
  },

  /** 备忘查询（start/end 为 YYYY-MM-DD） */
  async getMemos(params?: {
    start?: string
    end?: string
    limit?: number
  }): Promise<Memo[]> {
    const res = await http.get<Memo[]>('/memos', { params })
    return res.data
  },

  /** 新建备忘（管理员） */
  async createMemo(data: {
    title: string
    content: string
    memo_date: string
  }): Promise<Memo> {
    const res = await http.post<Memo>('/memos', data)
    return res.data
  },

  /** 更新备忘（管理员） */
  async updateMemo(
    id: number,
    data: { title?: string; content?: string; memo_date?: string },
  ): Promise<Memo> {
    const res = await http.put<Memo>(`/memos/${id}`, data)
    return res.data
  },

  /** 删除备忘（管理员） */
  async deleteMemo(id: number): Promise<void> {
    await http.delete(`/memos/${id}`)
  },
}
