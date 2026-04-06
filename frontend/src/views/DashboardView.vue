<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'

import EtfSwitch from '../components/EtfSwitch.vue'
import RankingTable from '../components/RankingTable.vue'
import { useRankingStore } from '../stores/ranking'

const rankingStore = useRankingStore()
const showScrollTop = ref(false)

function handleScroll() {
  showScrollTop.value = window.scrollY > 320
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  void rankingStore.loadRankings()
  handleScroll()
  window.addEventListener('scroll', handleScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

watch(
  () => [rankingStore.includeEtf, rankingStore.topN, rankingStore.rankingMetric],
  () => {
    void rankingStore.loadRankings()
  },
)
</script>

<template>
  <main class="min-h-screen bg-[radial-gradient(circle_at_15%_20%,#fee2e2_0%,transparent_25%),radial-gradient(circle_at_80%_10%,#dbeafe_0%,transparent_30%),linear-gradient(145deg,#f8fafc,#eef2ff)] px-4 py-8 text-slate-800 sm:px-8">
    <section class="mx-auto max-w-6xl">
      <header class="mb-6 rounded-2xl border border-white/50 bg-white/70 p-6 shadow-lg backdrop-blur">
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Market Pulse</p>
        <h1 class="mt-2 text-2xl font-extrabold tracking-tight sm:text-4xl">股票交易量 / 值 排行榜</h1>
        <p class="mt-2 text-sm text-slate-600">即時比較昨日前 N 名與今日即時前 N 名，快速追蹤名次變化。</p>
      </header>

      <section class="mb-6 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-start sm:justify-between">
        <div class="grid gap-3 sm:grid-cols-2 sm:gap-6">
          <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">篩選條件</p>
            <EtfSwitch v-model="rankingStore.includeEtf" />
          </div>

          <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500">排行模式</p>
            <label class="inline-flex items-center gap-2 text-sm font-semibold text-slate-700">
              排行依據
              <select
                class="rounded-lg border border-slate-300 bg-white px-3 py-2"
                :value="rankingStore.rankingMetric"
                @change="rankingStore.setRankingMetric(($event.target as HTMLSelectElement).value as 'turnover_value' | 'volume')"
              >
                <option value="turnover_value">成交值</option>
                <option value="volume">成交量</option>
              </select>
            </label>
          </div>
        </div>

        <label class="inline-flex items-center gap-2 text-sm font-semibold text-slate-700">
          Top N
          <input
            type="number"
            min="1"
            max="500"
            class="w-24 rounded-lg border border-slate-300 px-3 py-2 text-right"
            :value="rankingStore.topN"
            @change="rankingStore.setTopN(Number(($event.target as HTMLInputElement).value) || 100)"
          />
        </label>
      </section>

      <section class="mb-6 grid gap-4 lg:grid-cols-2">
        <article class="rounded-2xl border border-emerald-200 bg-white p-4 shadow-sm">
          <h2 class="text-sm font-bold text-emerald-800">今日強勢族群（Top 出現頻率）</h2>
          <p class="mt-1 text-xs text-slate-500">以當前 Top N 出現次數排序</p>
          <ul class="mt-3 space-y-2">
            <li
              v-for="group in rankingStore.todayGroupFrequency.slice(0, 5)"
              :key="group.tag"
              class="flex items-center justify-between rounded-lg bg-emerald-50 px-3 py-2 text-sm"
            >
              <span class="font-semibold text-emerald-900">{{ group.tag }}</span>
              <span class="text-emerald-700">{{ group.count }} 檔</span>
            </li>
          </ul>
        </article>

        <article class="rounded-2xl border border-amber-200 bg-white p-4 shadow-sm">
          <h2 class="text-sm font-bold text-amber-800">族群性集體轉強</h2>
          <p class="mt-1 text-xs text-slate-500">相較昨日進榜數顯著增加</p>
          <ul v-if="rankingStore.groupStrengthening.length > 0" class="mt-3 space-y-2">
            <li
              v-for="signal in rankingStore.groupStrengthening.slice(0, 5)"
              :key="signal.tag"
              class="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900"
            >
              {{ signal.tag }}：{{ signal.yesterday_count }} -> {{ signal.today_count }}（+{{ signal.delta_count }}）
            </li>
          </ul>
          <p v-else class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-500">目前無明顯族群集體轉強。</p>
        </article>
      </section>

      <p v-if="rankingStore.loading" class="mb-4 rounded-lg bg-sky-100 px-4 py-2 text-sm font-medium text-sky-800">載入排行榜中...</p>
      <p v-if="rankingStore.error" class="mb-4 rounded-lg bg-rose-100 px-4 py-2 text-sm font-medium text-rose-800">{{ rankingStore.error }}</p>
      <p v-if="!rankingStore.loading && !rankingStore.error && rankingStore.rows.length === 0" class="mb-4 rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700">目前沒有符合條件的資料。</p>

      <RankingTable
        v-if="rankingStore.rows.length > 0"
        :rows="rankingStore.rows"
        :ranking-metric="rankingStore.rankingMetric"
      />
    </section>

    <button
      v-show="showScrollTop"
      type="button"
      class="fixed bottom-6 right-6 z-20 inline-flex h-11 w-11 items-center justify-center rounded-full bg-slate-900 text-sm font-bold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-slate-700"
      aria-label="回到頂部"
      @click="scrollToTop"
    >
      Top
    </button>
  </main>
</template>
