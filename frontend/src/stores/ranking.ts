import { defineStore } from 'pinia'
import { ref } from 'vue'

import { fetchMomentumSnapshot } from '../services/rankingsApi'
import type {
  GroupFrequency,
  GroupStrengtheningSignal,
  RankedStockWithChange,
  RankingMetric,
} from '../types/ranking'

export const useRankingStore = defineStore('ranking', () => {
  const rows = ref<RankedStockWithChange[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const includeEtf = ref(true)
  const topN = ref(100)
  const rankingMetric = ref<RankingMetric>('turnover_value')
  const todayGroupFrequency = ref<GroupFrequency[]>([])
  const groupStrengthening = ref<GroupStrengtheningSignal[]>([])

  async function loadRankings() {
    loading.value = true
    error.value = null
    try {
      const snapshot = await fetchMomentumSnapshot(topN.value, includeEtf.value, rankingMetric.value)
      rows.value = snapshot.rows
      todayGroupFrequency.value = snapshot.today_group_frequency
      groupStrengthening.value = snapshot.group_strengthening.filter((item) => item.is_collective_strengthening)
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

  return {
    rows,
    loading,
    error,
    includeEtf,
    topN,
    rankingMetric,
    todayGroupFrequency,
    groupStrengthening,
    loadRankings,
    setIncludeEtf,
    setTopN,
    setRankingMetric,
  }
})
