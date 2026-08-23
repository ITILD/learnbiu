<script setup lang="ts">
/** 备忘日历：年 / 月 / 周三种视图，展示对应范围内的备忘
 *  年视图按月显示备忘标题；月视图按天显示备忘标题；周视图按天显示备忘详情（超出省略） */
import { computed, ref, watch } from 'vue'
import { api, type Memo } from '@/api'

type ViewMode = 'year' | 'month' | 'week'

const mode = ref<ViewMode>('month')
const cursor = ref(new Date()) // 当前定位日期
const memos = ref<Memo[]>([])

/** 本地时区安全的日期格式化（YYYY-MM-DD） */
function fmt(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function addDays(d: Date, n: number): Date {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n)
}

const todayKey = fmt(new Date())

/** 当前视图对应的查询范围 */
const range = computed<[string, string]>(() => {
  const d = cursor.value
  if (mode.value === 'year') {
    return [fmt(new Date(d.getFullYear(), 0, 1)), fmt(new Date(d.getFullYear(), 11, 31))]
  }
  if (mode.value === 'month') {
    return [
      fmt(new Date(d.getFullYear(), d.getMonth(), 1)),
      fmt(new Date(d.getFullYear(), d.getMonth() + 1, 0)),
    ]
  }
  const day = d.getDay() === 0 ? 7 : d.getDay()
  const monday = addDays(d, 1 - day)
  return [fmt(monday), fmt(addDays(monday, 6))]
})

// 范围变化时自动拉取备忘
watch(
  range,
  async ([start, end]) => {
    memos.value = await api.getMemos({ start, end })
  },
  { immediate: true },
)

/** 备忘按日期分组 */
const grouped = computed(() => {
  const map = new Map<string, Memo[]>()
  for (const m of memos.value) {
    const list = map.get(m.memo_date) ?? []
    list.push(m)
    map.set(m.memo_date, list)
  }
  return map
})

const weekdays = ['一', '二', '三', '四', '五', '六', '日']

/** 视图标题 */
const title = computed(() => {
  const d = cursor.value
  if (mode.value === 'year') return `${d.getFullYear()} 年`
  if (mode.value === 'month') return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月`
  const firstDay = new Date(d.getFullYear(), 0, 1)
  const dayOfYear = Math.floor((d.getTime() - firstDay.getTime()) / 86400000)
  const week = Math.ceil((dayOfYear + firstDay.getDay() + 1) / 7)
  return `${d.getFullYear()} 年 第 ${week} 周`
})

/** el-segmented 的 v-model 适配（类型收窄） */
const modeValue = computed({
  get: () => mode.value as string,
  set: (v: string) => {
    mode.value = v as ViewMode
  },
})
const viewOptions = [
  { label: '年', value: 'year' },
  { label: '月', value: 'month' },
  { label: '周', value: 'week' },
]

/** 月视图单元格（周一开头，前置空白补齐） */
const monthCells = computed(() => {
  const d = cursor.value
  const first = new Date(d.getFullYear(), d.getMonth(), 1)
  const offset = first.getDay() === 0 ? 6 : first.getDay() - 1
  const daysInMonth = new Date(d.getFullYear(), d.getMonth() + 1, 0).getDate()
  const cells: { key: string; day: number; isToday: boolean }[] = []
  for (let i = 0; i < offset; i++) cells.push({ key: `pad-${i}`, day: 0, isToday: false })
  for (let i = 1; i <= daysInMonth; i++) {
    const key = fmt(new Date(d.getFullYear(), d.getMonth(), i))
    cells.push({ key, day: i, isToday: key === todayKey })
  }
  return cells
})

/** 周视图：7 天及其备忘（含内容详情） */
const weekDays = computed(() => {
  const start = new Date(`${range.value[0]}T00:00:00`)
  return Array.from({ length: 7 }, (_, i) => {
    const date = addDays(start, i)
    const key = fmt(date)
    return {
      key,
      label: `周${weekdays[i]}`,
      dayNum: date.getDate(),
      isToday: key === todayKey,
      memos: grouped.value.get(key) ?? [],
    }
  })
})

/** 年视图：12 个月及其备忘 */
const yearMonths = computed(() => {
  const y = cursor.value.getFullYear()
  return Array.from({ length: 12 }, (_, i) => ({
    month: i + 1,
    memos: memos.value.filter((m) => {
      const d = new Date(`${m.memo_date}T00:00:00`)
      return d.getFullYear() === y && d.getMonth() === i
    }),
  }))
})

/** 上一期 / 下一期 */
function shift(n: number) {
  const d = cursor.value
  if (mode.value === 'year') cursor.value = new Date(d.getFullYear() + n, 0, 1)
  else if (mode.value === 'month')
    cursor.value = new Date(d.getFullYear(), d.getMonth() + n, 1)
  else cursor.value = addDays(d, n * 7)
}

/** 回到今天 */
function goToday() {
  cursor.value = new Date()
}
</script>

<template>
  <div class="memo-calendar">
    <!-- 顶部：视图切换 + 期次导航 -->
    <div class="cal-toolbar">
      <el-segmented v-model="modeValue" :options="viewOptions" />
      <div class="cal-nav">
        <el-button circle size="small" @click="shift(-1)">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span class="cal-title font-serif">{{ title }}</span>
        <el-button circle size="small" @click="shift(1)">
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button size="small" text type="primary" @click="goToday">今天</el-button>
      </div>
    </div>

    <!-- 年视图：按月显示备忘标题 -->
    <div v-if="mode === 'year'" class="year-view">
      <div v-for="m in yearMonths" :key="m.month" class="month-card">
        <div class="month-name">{{ m.month }} 月</div>
        <ul v-if="m.memos.length" class="month-memo-list">
          <li v-for="memo in m.memos" :key="memo.id" :title="memo.title">
            {{ memo.title }}
          </li>
        </ul>
        <span v-else class="cal-empty">—</span>
      </div>
    </div>

    <!-- 月视图：按天显示备忘标题 -->
    <div v-else-if="mode === 'month'" class="month-view">
      <div class="weekday-row">
        <span v-for="w in weekdays" :key="w">{{ w }}</span>
      </div>
      <div class="month-grid">
        <div
          v-for="cell in monthCells"
          :key="cell.key"
          class="day-cell"
          :class="{ 'is-today': cell.isToday, 'is-pad': cell.day === 0 }"
        >
          <template v-if="cell.day > 0">
            <div class="day-num" :class="{ 'today-badge': cell.isToday }">{{ cell.day }}</div>
            <div
              v-for="memo in grouped.get(cell.key) ?? []"
              :key="memo.id"
              class="memo-chip"
              :title="memo.title"
            >
              {{ memo.title }}
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 周视图：按天显示备忘详情（超出省略） -->
    <div v-else class="week-view">
      <div
        v-for="d in weekDays"
        :key="d.key"
        class="week-day"
        :class="{ 'is-today': d.isToday }"
      >
        <div class="week-day-head">
          <span class="week-day-label">{{ d.label }}</span>
          <span class="week-day-num">{{ d.dayNum }} 日</span>
          <span v-if="d.memos.length" class="week-day-count">{{ d.memos.length }} 条</span>
        </div>
        <div v-if="d.memos.length" class="week-memos">
          <div
            v-for="memo in d.memos"
            :key="memo.id"
            class="week-memo"
            :title="`${memo.title}\n${memo.content}`"
          >
            <div class="week-memo-title">{{ memo.title }}</div>
            <div v-if="memo.content" class="week-memo-content">{{ memo.content }}</div>
          </div>
        </div>
        <div v-else class="cal-empty">无备忘</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cal-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.cal-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cal-title {
  min-width: 118px;
  text-align: center;
  font-size: 15px;
  color: var(--leaf-deep);
}

.cal-empty {
  color: #b9c2ba;
  font-size: 13px;
}

/* ---- 年视图 ---- */
.year-view {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(145px, 1fr));
  gap: 10px;
}

.month-card {
  background: var(--paper-card);
  border: 1px solid var(--leaf-line);
  border-radius: 8px;
  padding: 10px;
  min-height: 92px;
}

.month-name {
  color: var(--leaf-primary);
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 14px;
}

.month-memo-list {
  margin: 0;
  padding-left: 1.1em;
}

.month-memo-list li {
  font-size: 13px;
  line-height: 1.9;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---- 月视图 ---- */
.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  color: var(--ink-light);
  font-size: 13px;
  margin-bottom: 6px;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.day-cell {
  background: var(--paper-card);
  border: 1px solid var(--leaf-line);
  border-radius: 6px;
  min-height: 86px;
  padding: 4px;
  overflow: hidden;
}

.day-cell.is-pad {
  background: transparent;
  border-color: transparent;
}

.day-cell.is-today {
  border-color: var(--leaf-primary);
  background: var(--el-color-primary-light-9);
}

.day-num {
  font-size: 13px;
  color: var(--ink-light);
  margin-bottom: 2px;
}

.today-badge {
  display: inline-block;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  background: var(--leaf-primary);
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
}

.memo-chip {
  font-size: 12px;
  background: var(--leaf-pale);
  color: var(--leaf-deep);
  border-radius: 4px;
  padding: 1px 5px;
  margin-top: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---- 周视图 ---- */
.week-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.week-day {
  background: var(--paper-card);
  border: 1px solid var(--leaf-line);
  border-radius: 8px;
  padding: 8px 12px;
}

.week-day.is-today {
  border-color: var(--leaf-primary);
  background: var(--el-color-primary-light-9);
}

.week-day-head {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.week-day-label {
  color: var(--leaf-primary);
  font-weight: 600;
}

.week-day-count {
  color: var(--ink-light);
  font-size: 12px;
  margin-left: auto;
}

.week-memos {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 8px;
  margin-top: 6px;
}

.week-memo {
  background: var(--leaf-pale);
  border-radius: 6px;
  padding: 6px 10px;
  overflow: hidden;
}

.week-memo-title {
  font-weight: 600;
  font-size: 13.5px;
  color: var(--leaf-deep);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 内容超出两行省略 */
.week-memo-content {
  font-size: 12.5px;
  color: var(--ink-light);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 小屏适配 */
@media (max-width: 600px) {
  .day-cell {
    min-height: 64px;
  }
}
</style>
