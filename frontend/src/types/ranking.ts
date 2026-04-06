export interface RankedStock {
  symbol: string
  name: string
  industry_level_1: string
  industry_level_2: string
  custom_group_tag: string
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
  rows: RankedStockWithChange[]
  today_group_frequency: GroupFrequency[]
  group_strengthening: GroupStrengtheningSignal[]
}
