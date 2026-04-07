import { defineStore } from 'pinia'
import { ref } from 'vue'

import { addCustomTag, fetchMomentumSnapshot, fetchTagEditorCatalog, removeCustomTag } from '../services/rankingsApi'
import type {
  GroupFrequency,
  GroupStrengtheningSignal,
  RankedStockWithChange,
  RankingMetric,
  TagEditorStock,
} from '../types/ranking'

export const useRankingStore = defineStore('ranking', () => {
  const rows = ref<RankedStockWithChange[]>([])
  const tagEditorRows = ref<TagEditorStock[]>([])
  const tagCatalogDate = ref('')
  const tagCatalogTotalSymbols = ref(0)
  const tagCatalogNewSymbolsToday = ref<string[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const includeEtf = ref(true)
  const topN = ref(100)
  const rankingMetric = ref<RankingMetric>('turnover_value')
  const todayGroupFrequency = ref<GroupFrequency[]>([])
  const groupStrengthening = ref<GroupStrengtheningSignal[]>([])
  const savingTags = ref(false)

  async function loadRankings() {
    loading.value = true
    error.value = null
    try {
      const snapshot = await fetchMomentumSnapshot(topN.value, includeEtf.value, rankingMetric.value)
      rows.value = snapshot.rows
      todayGroupFrequency.value = snapshot.today_group_frequency
      groupStrengthening.value = snapshot.group_strengthening.filter((item) => item.is_collective_strengthening)

      const catalog = await fetchTagEditorCatalog(includeEtf.value, rankingMetric.value)
      tagEditorRows.value = catalog.rows
      tagCatalogDate.value = catalog.generated_date
      tagCatalogTotalSymbols.value = catalog.total_symbols
      tagCatalogNewSymbolsToday.value = catalog.new_symbols_today
    } catch (err) {
      error.value = err instanceof Error ? err.message : '載入排行榜失敗'
    } finally {
      loading.value = false
    }
  }

  function setIncludeEtf(value: boolean) {
    includeEtf.value = value
  }

  function setTopN(value: number) {
    topN.value = value
  }

  function setRankingMetric(value: RankingMetric) {
    rankingMetric.value = value
  }

  async function addTag(symbol: string, tag: string, industry?: string) {
    savingTags.value = true
    error.value = null
    try {
      await addCustomTag(symbol, tag, industry)
      await loadRankings()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '新增標籤失敗'
    } finally {
      savingTags.value = false
    }
  }

  async function deleteTag(symbol: string, tag: string) {
    savingTags.value = true
    error.value = null
    try {
      await removeCustomTag(symbol, tag)
      await loadRankings()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '刪除標籤失敗'
    } finally {
      savingTags.value = false
    }
  }

  return {
    rows,
    tagEditorRows,
    tagCatalogDate,
    tagCatalogTotalSymbols,
    tagCatalogNewSymbolsToday,
    loading,
    error,
    includeEtf,
    topN,
    rankingMetric,
    todayGroupFrequency,
    groupStrengthening,
    savingTags,
    loadRankings,
    setIncludeEtf,
    setTopN,
    setRankingMetric,
    addTag,
    deleteTag,
  }
})
