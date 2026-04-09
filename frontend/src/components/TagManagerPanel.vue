<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { TagEditorStock } from '../types/ranking'

const props = defineProps<{
  rows: TagEditorStock[]
  generatedDate?: string
  totalSymbols?: number
  newSymbolsToday?: string[]
  savingTags?: boolean
}>()

const emit = defineEmits<{
  (e: 'add-tag', payload: { symbol: string; industry: string; tag: string }): void
  (e: 'remove-tag', payload: { symbol: string; tag: string }): void
}>()

const keyword = ref('')
const pendingTags = reactive<Record<string, string>>({})

const filteredRows = computed(() => {
  const needle = keyword.value.trim().toLowerCase()
  if (!needle) {
    return props.rows
  }

  return props.rows.filter((row) => {
    const tags = row.custom_group_tags.length > 0 ? row.custom_group_tags : [row.custom_group_tag]
    const haystack = [row.symbol, row.name, row.industry_level_1, ...tags].join(' ').toLowerCase()
    return haystack.includes(needle)
  })
})

function submitTag(symbol: string, industry: string) {
  const tag = (pendingTags[symbol] ?? '').trim()
  if (!tag) {
    return
  }
  emit('add-tag', { symbol, industry, tag })
  pendingTags[symbol] = ''
}
</script>

<template>
  <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
    <div class="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div class="min-w-0">
        <h2 class="text-base font-bold text-slate-800">自定義標籤管理</h2>
        <p class="text-xs text-slate-500">資料來源：每日前 100 名累積。對標籤的新增/刪除會永久儲存。</p>
        <p class="mt-1 text-xs text-slate-500">
          同步日期：{{ props.generatedDate || '-' }}，累積股票數：{{ props.totalSymbols ?? props.rows.length }}，今日新進：{{ props.newSymbolsToday?.length ?? 0 }}
        </p>
      </div>
      <label class="text-sm font-semibold text-slate-700 sm:text-right">
        關鍵字搜尋
        <input
          v-model="keyword"
          type="text"
          class="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm sm:mt-0 sm:ml-2 sm:w-56"
          placeholder="代號 / 名稱 / 標籤"
        />
      </label>
    </div>

    <div class="grid gap-3 md:hidden">
      <article
        v-for="row in filteredRows"
        :key="row.symbol"
        class="rounded-xl border border-slate-200 p-4 shadow-sm"
        :class="row.is_new_today ? 'bg-rose-50/80' : 'bg-white'"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0">
            <h3 class="text-base font-bold text-slate-900">{{ row.name }}</h3>
            <p class="mt-1 font-mono text-sm text-slate-600">{{ row.symbol }}</p>
          </div>
          <span v-if="row.is_new_today" class="shrink-0 rounded-full bg-rose-100 px-2 py-1 text-xs font-bold text-rose-700">今日新進</span>
          <span v-else class="shrink-0 text-xs text-slate-500">累積</span>
        </div>

        <div class="mt-4 rounded-lg bg-slate-50 p-3">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">產業</p>
          <p class="mt-1 text-sm font-semibold text-slate-900">{{ row.industry_level_1 }}</p>
        </div>

        <div class="mt-4">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">目前標籤</p>
          <div class="mt-2 flex flex-wrap gap-1.5">
            <span
              v-for="(tag, index) in (row.custom_group_tags.length ? row.custom_group_tags : [row.custom_group_tag])"
              :key="`${row.symbol}-${tag}-${index}`"
              class="inline-flex items-center gap-1 rounded-full bg-indigo-100 px-2 py-1 text-xs font-bold text-indigo-700"
            >
              {{ tag }}
              <button
                type="button"
                class="rounded-full px-1 leading-none text-indigo-700 transition hover:bg-indigo-200 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="props.savingTags"
                title="刪除標籤"
                @click="emit('remove-tag', { symbol: row.symbol, tag })"
              >
                ×
              </button>
            </span>
          </div>
        </div>

        <div class="mt-4 flex flex-col gap-2 sm:flex-row sm:items-center">
          <input
            :value="pendingTags[row.symbol] ?? ''"
            type="text"
            class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm sm:flex-1"
            placeholder="新增標籤"
            :disabled="props.savingTags"
            @input="pendingTags[row.symbol] = ($event.target as HTMLInputElement).value"
            @keydown.enter.prevent="submitTag(row.symbol, row.industry_level_1)"
          />
          <button
            type="button"
            class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-300"
            :disabled="props.savingTags"
            @click="submitTag(row.symbol, row.industry_level_1)"
          >
            新增
          </button>
        </div>
      </article>
    </div>

    <div class="hidden overflow-x-auto rounded-xl border border-slate-100 md:block">
      <table class="min-w-[960px] w-full text-left text-sm">
        <thead class="bg-slate-50 text-slate-600">
          <tr>
            <th class="px-3 py-2">代號</th>
            <th class="px-3 py-2">名稱</th>
            <th class="px-3 py-2">狀態</th>
            <th class="px-3 py-2">產業</th>
            <th class="px-3 py-2">目前標籤</th>
            <th class="px-3 py-2">新增標籤</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in filteredRows"
            :key="row.symbol"
            class="border-t border-slate-100"
            :class="row.is_new_today ? 'bg-rose-50/80' : ''"
          >
            <td class="px-3 py-2 font-mono text-slate-700">{{ row.symbol }}</td>
            <td class="px-3 py-2 font-medium text-slate-800">{{ row.name }}</td>
            <td class="px-3 py-2">
              <span v-if="row.is_new_today" class="rounded-full bg-rose-100 px-2 py-1 text-xs font-bold text-rose-700">今日新進</span>
              <span v-else class="text-xs text-slate-500">累積</span>
            </td>
            <td class="px-3 py-2 text-slate-700">{{ row.industry_level_1 }}</td>
            <td class="px-3 py-2">
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="(tag, index) in (row.custom_group_tags.length ? row.custom_group_tags : [row.custom_group_tag])"
                  :key="`${row.symbol}-${tag}-${index}`"
                  class="inline-flex items-center gap-1 rounded-full bg-indigo-100 px-2 py-1 text-xs font-bold text-indigo-700"
                >
                  {{ tag }}
                  <button
                    type="button"
                    class="rounded-full px-1 leading-none text-indigo-700 transition hover:bg-indigo-200 disabled:cursor-not-allowed disabled:opacity-50"
                    :disabled="props.savingTags"
                    title="刪除標籤"
                    @click="emit('remove-tag', { symbol: row.symbol, tag })"
                  >
                    ×
                  </button>
                </span>
              </div>
            </td>
            <td class="px-3 py-2">
              <div class="flex items-center gap-2">
                <input
                  :value="pendingTags[row.symbol] ?? ''"
                  type="text"
                  class="w-40 rounded-md border border-slate-300 px-2 py-1 text-xs"
                  placeholder="新增標籤"
                  :disabled="props.savingTags"
                  @input="pendingTags[row.symbol] = ($event.target as HTMLInputElement).value"
                  @keydown.enter.prevent="submitTag(row.symbol, row.industry_level_1)"
                />
                <button
                  type="button"
                  class="rounded-md bg-indigo-600 px-2 py-1 text-xs font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-indigo-300"
                  :disabled="props.savingTags"
                  @click="submitTag(row.symbol, row.industry_level_1)"
                >
                  新增
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="filteredRows.length === 0" class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-500">
      查無符合條件的股票。
    </p>
  </section>
</template>
