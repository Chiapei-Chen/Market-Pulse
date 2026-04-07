export type RankingMetric = 'turnover_value' | 'volume'

export interface RankedStock {
  symbol: string
  name: string
  industry_level_1: string
  industry_level_2: string
  custom_group_tag: string
  custom_group_tags: string[]
  volume: number
  turnover_value: number
  rank: number
}

export interface RankedStockWithChange extends RankedStock {
  rank_change: number
  is_new_entry: boolean
}

export interface GroupFrequency {
  tag: string
  count: number
}

export interface GroupStrengtheningSignal {
  tag: string
  yesterday_count: number
  today_count: number
  delta_count: number
  is_collective_strengthening: boolean
}

export interface MomentumSnapshot {
  ranking_metric: RankingMetric
  rows: RankedStockWithChange[]
  today_group_frequency: GroupFrequency[]
  group_strengthening: GroupStrengtheningSignal[]
}

export interface TagEditorStock {
  symbol: string
  name: string
  industry_level_1: string
  industry_level_2: string
  custom_group_tag: string
  custom_group_tags: string[]
  first_seen_date: string
  last_seen_date: string
  seen_days_count: number
  last_rank: number
  is_new_today: boolean
}

export interface TagEditorCatalogResponse {
  generated_date: string
  tracked_top_n: number
  total_symbols: number
  new_symbols_today: string[]
  rows: TagEditorStock[]
}
