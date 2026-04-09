<script setup lang="ts">
import type { RankedStockWithChange, RankingMetric } from '../types/ranking'

defineProps<{
  rows: RankedStockWithChange[]
  rankingMetric: RankingMetric
}>()

function formatNumber(value: number): string {
  return new Intl.NumberFormat('zh-TW').format(value)
}

function changeColorClass(change: number): string {
  if (change > 0) {
    return 'text-rose-600'
  }
  if (change < 0) {
    return 'text-emerald-600'
  }
  return 'text-slate-500'
}
</script>

<template>
  <div class="rounded-2xl border border-slate-200 bg-white/90 shadow-sm">
    <div class="border-b border-slate-200 px-4 py-3 text-xs text-slate-500">
      目前排名依據：
      <span class="font-semibold text-slate-700">{{ rankingMetric === 'turnover_value' ? '成交值' : '成交量' }}</span>
    </div>
    <div class="grid gap-3 p-3 md:hidden">
      <article
        v-for="row in rows"
        :key="row.symbol"
        class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">#{{ row.rank }}</p>
            <h3 class="mt-1 text-base font-bold text-slate-900">{{ row.name }}</h3>
            <p class="mt-1 font-mono text-sm text-slate-600">{{ row.symbol }}</p>
          </div>
          <div class="shrink-0 text-right">
            <span v-if="row.is_new_entry" class="rounded-full bg-amber-100 px-2 py-1 text-xs font-bold text-amber-700">New</span>
            <span v-else class="inline-flex items-center gap-1 text-sm font-semibold" :class="changeColorClass(row.rank_change)">
              <span v-if="row.rank_change > 0">▲</span>
              <span v-else-if="row.rank_change < 0">▼</span>
              <span v-else>•</span>
              <span>{{ Math.abs(row.rank_change) }}</span>
            </span>
          </div>
        </div>

        <div class="mt-4 grid gap-3 rounded-lg bg-slate-50 p-3 text-sm text-slate-700 sm:grid-cols-2">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">產業</p>
            <p class="mt-1 font-semibold text-slate-900">{{ row.industry_level_1 }}</p>
            <p
              v-if="row.industry_level_2 && row.industry_level_2 !== 'Unknown'"
              class="mt-0.5 text-xs text-slate-500"
            >
              {{ row.industry_level_2 }}
            </p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">成交量</p>
            <p class="mt-1 font-semibold text-slate-900">{{ formatNumber(row.volume) }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">成交值</p>
            <p class="mt-1 font-semibold text-slate-900">{{ formatNumber(row.turnover_value) }}</p>
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">名次變動</p>
            <p class="mt-1 font-semibold" :class="changeColorClass(row.rank_change)">
              {{ row.is_new_entry ? 'New' : `${row.rank_change > 0 ? '上升' : row.rank_change < 0 ? '下降' : '持平'} ${Math.abs(row.rank_change)}` }}
            </p>
          </div>
        </div>

        <div class="mt-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">自定義標籤</p>
          <div class="mt-2 flex flex-wrap gap-1.5">
            <span
              v-for="(tag, index) in (row.custom_group_tags.length ? row.custom_group_tags : [row.custom_group_tag])"
              :key="`${row.symbol}-${tag}-${index}`"
              class="inline-flex rounded-full bg-indigo-100 px-2 py-1 text-xs font-bold text-indigo-700"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </article>
    </div>

    <div class="hidden overflow-x-auto md:block">
      <table class="min-w-[1100px] w-full text-left text-sm">
        <thead class="bg-slate-100 text-slate-600">
          <tr>
            <th class="px-4 py-3">名次</th>
            <th class="px-4 py-3">代號</th>
            <th class="px-4 py-3">名稱</th>
            <th class="px-4 py-3">產業</th>
            <th class="px-4 py-3">自定義標籤</th>
            <th class="px-4 py-3 text-right">成交量</th>
            <th class="px-4 py-3 text-right">成交值</th>
            <th class="px-4 py-3">名次變動</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.symbol" class="border-t border-slate-100 hover:bg-slate-50/80">
            <td class="px-4 py-3 font-semibold text-slate-800">#{{ row.rank }}</td>
            <td class="px-4 py-3 font-mono text-slate-800">{{ row.symbol }}</td>
            <td class="px-4 py-3 font-medium text-slate-800">{{ row.name }}</td>
            <td class="px-4 py-3">
              <div class="flex flex-col gap-1">
                <span class="text-sm font-semibold text-slate-800">{{ row.industry_level_1 }}</span>
                <span
                  v-if="row.industry_level_2 && row.industry_level_2 !== 'Unknown'"
                  class="text-xs text-slate-500"
                >
                  {{ row.industry_level_2 }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="(tag, index) in (row.custom_group_tags.length ? row.custom_group_tags : [row.custom_group_tag])"
                  :key="`${row.symbol}-${tag}-${index}`"
                  class="inline-flex rounded-full bg-indigo-100 px-2 py-1 text-xs font-bold text-indigo-700"
                >
                  {{ tag }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3 text-right text-slate-700">{{ formatNumber(row.volume) }}</td>
            <td class="px-4 py-3 text-right text-slate-700">{{ formatNumber(row.turnover_value) }}</td>
            <td class="px-4 py-3">
              <span v-if="row.is_new_entry" class="rounded-full bg-amber-100 px-2 py-1 text-xs font-bold text-amber-700">New</span>
              <span v-else class="inline-flex items-center gap-1 font-semibold" :class="changeColorClass(row.rank_change)">
                <span v-if="row.rank_change > 0">▲</span>
                <span v-else-if="row.rank_change < 0">▼</span>
                <span v-else>•</span>
                <span>{{ Math.abs(row.rank_change) }}</span>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
