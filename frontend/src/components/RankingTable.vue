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
  <div class="overflow-x-auto rounded-2xl border border-slate-200 bg-white/90 shadow-sm">
    <div class="border-b border-slate-200 px-4 py-3 text-xs text-slate-500">
      目前排名依據：
      <span class="font-semibold text-slate-700">{{ rankingMetric === 'turnover_value' ? '成交值' : '成交量' }}</span>
    </div>
    <table class="min-w-[900px] w-full text-left text-sm">
      <thead class="bg-slate-100 text-slate-600">
        <tr>
          <th class="px-4 py-3">名次</th>
          <th class="px-4 py-3">代號</th>
          <th class="px-4 py-3">名稱</th>
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
            <span class="inline-flex rounded-full bg-indigo-100 px-2 py-1 text-xs font-bold text-indigo-700">
              {{ row.custom_group_tag }}
            </span>
            <span
              v-if="row.custom_group_tags.length > 1"
              class="ml-2 text-xs font-semibold text-slate-500"
              :title="row.custom_group_tags.join(' / ')"
            >
              +{{ row.custom_group_tags.length - 1 }}
            </span>
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
</template>
