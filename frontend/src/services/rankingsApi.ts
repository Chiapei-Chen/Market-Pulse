import axios from 'axios'
import type { MomentumSnapshot, RankingMetric, TagEditorCatalogResponse } from '../types/ranking'

// 1. 取得環境變數
const envBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();

// 2. 決定 Base URL
// 優先使用環境變數 -> 其次開發環境用 127.0.0.1 -> 最後生產環境用相對路徑
const apiBaseUrl = envBaseUrl || (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '');

// 3. 檢查警告（選用）
if (!envBaseUrl && !import.meta.env.DEV) {
  console.warn('VITE_API_BASE_URL is not set. Requests will be relative to current domain.');
}

const client = axios.create({
  baseURL: apiBaseUrl,
  timeout: 10000,
})

export async function fetchMomentumSnapshot(
  topN: number,
  includeEtf: boolean,
  rankingMetric: RankingMetric,
): Promise<MomentumSnapshot> {
  const response = await client.get<MomentumSnapshot>('/momentum', {
    params: {
      top_n: topN,
      include_etf: includeEtf,
      ranking_metric: rankingMetric,
    },
  })

  return response.data
}

export async function addCustomTag(symbol: string, tag: string, industry?: string): Promise<void> {
  await client.post(`/themes/${symbol}/tags`, {
    tag,
    industry,
  })
}

export async function removeCustomTag(symbol: string, tag: string): Promise<void> {
  await client.delete(`/themes/${symbol}/tags`, {
    data: {
      tag,
    },
  })
}

export async function fetchTagEditorCatalog(
  includeEtf: boolean,
  rankingMetric: RankingMetric,
): Promise<TagEditorCatalogResponse> {
  const response = await client.get<TagEditorCatalogResponse>('/themes/catalog', {
    params: {
      include_etf: includeEtf,
      ranking_metric: rankingMetric,
    },
  })
  return response.data
}
