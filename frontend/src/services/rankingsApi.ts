import axios from 'axios'
import type { MomentumSnapshot, RankingMetric } from '../types/ranking'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/rankings',
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
