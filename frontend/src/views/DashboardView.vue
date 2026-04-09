<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import EtfSwitch from "../components/EtfSwitch.vue";
import RankingTable from "../components/RankingTable.vue";
import TagManagerPanel from "../components/TagManagerPanel.vue";
import { useRankingStore } from "../stores/ranking";

const rankingStore = useRankingStore();
const showScrollTop = ref(false);
const activeSection = ref<"ranking" | "tag-manager">("ranking");
const selectedTag = ref("");
const tagKeyword = ref("");
const showTagOptions = ref(false);
const selectedIndustry = ref("");
const industryKeyword = ref("");
const showIndustryOptions = ref(false);

const availableTags = computed(() =>
  (rankingStore.todayGroupFrequency || []).map((item) => item.tag),
);
const availableIndustries = computed(() => {
  const industries = new Set<string>();
  for (const row of rankingStore.rows) {
    if (row.industry_level_1) {
      industries.add(row.industry_level_1);
    }
  }
  return [...industries].sort((a, b) => a.localeCompare(b, "zh-Hant"));
});

const matchedTags = computed(() => {
  const keyword = tagKeyword.value.trim();
  if (!keyword) {
    return availableTags.value;
  }
  return availableTags.value.filter((tag) =>
    tag.toLowerCase().includes(keyword.toLowerCase()),
  );
});

const matchedIndustries = computed(() => {
  const keyword = industryKeyword.value.trim();
  if (!keyword) {
    return availableIndustries.value;
  }
  return availableIndustries.value.filter((industry) =>
    industry.toLowerCase().includes(keyword.toLowerCase()),
  );
});

const filteredRows = computed(() => {
  return rankingStore.rows.filter((row) => {
    const tags =
      row.custom_group_tags.length > 0
        ? row.custom_group_tags
        : [row.custom_group_tag];
    const passTag = !selectedTag.value || tags.includes(selectedTag.value);
    const passIndustry =
      !selectedIndustry.value ||
      row.industry_level_1 === selectedIndustry.value;
    return passTag && passIndustry;
  });
});

function handleScroll() {
  showScrollTop.value = window.scrollY > 320;
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

onMounted(() => {
  void rankingStore.loadRankings();
  handleScroll();
  window.addEventListener("scroll", handleScroll, { passive: true });
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});

watch(
  () => [
    rankingStore.includeEtf,
    rankingStore.topN,
    rankingStore.rankingMetric,
  ],
  () => {
    void rankingStore.loadRankings();
  },
);

watch(availableTags, (tags) => {
  if (selectedTag.value && !tags.includes(selectedTag.value)) {
    selectedTag.value = "";
    tagKeyword.value = "";
  }
});

watch(availableIndustries, (industries) => {
  if (selectedIndustry.value && !industries.includes(selectedIndustry.value)) {
    selectedIndustry.value = "";
    industryKeyword.value = "";
  }
});

function applyTagFilter(tag: string) {
  selectedTag.value = tag;
  tagKeyword.value = tag;
  showTagOptions.value = false;
}

function clearTagFilter() {
  selectedTag.value = "";
  tagKeyword.value = "";
  showTagOptions.value = false;
}

function applyIndustryFilter(industry: string) {
  selectedIndustry.value = industry;
  industryKeyword.value = industry;
  showIndustryOptions.value = false;
}

function clearIndustryFilter() {
  selectedIndustry.value = "";
  industryKeyword.value = "";
  showIndustryOptions.value = false;
}

function hideTagOptionsWithDelay() {
  window.setTimeout(() => {
    showTagOptions.value = false;
  }, 120);
}

function hideIndustryOptionsWithDelay() {
  window.setTimeout(() => {
    showIndustryOptions.value = false;
  }, 120);
}

async function handleAddTag(payload: {
  symbol: string;
  industry: string;
  tag: string;
}) {
  await rankingStore.addTag(payload.symbol, payload.tag, payload.industry);
}

async function handleRemoveTag(payload: { symbol: string; tag: string }) {
  await rankingStore.deleteTag(payload.symbol, payload.tag);
}
</script>

<template>
  <main
    class="min-h-screen bg-[radial-gradient(circle_at_15%_20%,#fee2e2_0%,transparent_25%),radial-gradient(circle_at_80%_10%,#dbeafe_0%,transparent_30%),linear-gradient(145deg,#f8fafc,#eef2ff)] px-3 py-5 text-slate-800 sm:px-6 sm:py-8 lg:px-8"
  >
    <section class="mx-auto max-w-6xl">
      <header
        class="mb-6 rounded-2xl border border-white/50 bg-white/70 p-4 shadow-lg backdrop-blur sm:p-6"
      >
        <p
          class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500"
        >
          Market Pulse
        </p>
        <h1 class="mt-2 text-2xl font-extrabold tracking-tight sm:text-4xl">
          股票交易量 / 值 排行榜
        </h1>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
          即時比較昨日前 N 名與今日即時前 N 名，快速追蹤名次變化。
        </p>
      </header>

      <nav
        class="mb-6 flex flex-wrap gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm"
      >
        <button
          type="button"
          class="min-w-0 flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition sm:flex-none"
          :class="
            activeSection === 'ranking'
              ? 'bg-slate-900 text-white'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          "
          @click="activeSection = 'ranking'"
        >
          排行榜
        </button>
        <button
          type="button"
          class="min-w-0 flex-1 rounded-xl px-4 py-2 text-sm font-semibold transition sm:flex-none"
          :class="
            activeSection === 'tag-manager'
              ? 'bg-slate-900 text-white'
              : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
          "
          @click="activeSection = 'tag-manager'"
        >
          自定義標籤管理
        </button>
      </nav>

      <section
        v-if="activeSection === 'ranking'"
        class="mb-6 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm xl:flex-row xl:items-start xl:justify-between"
      >
        <div class="grid flex-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:gap-6">
          <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p
              class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500"
            >
              篩選條件
            </p>
            <EtfSwitch v-model="rankingStore.includeEtf" />
          </div>

          <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p
              class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500"
            >
              排行模式
            </p>
            <label
              class="flex flex-col gap-2 text-sm font-semibold text-slate-700 sm:inline-flex sm:flex-row sm:items-center"
            >
              排行依據
              <select
                class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 sm:w-auto"
                :value="rankingStore.rankingMetric"
                @change="
                  rankingStore.setRankingMetric(
                    ($event.target as HTMLSelectElement).value as
                      | 'turnover_value'
                      | 'volume',
                  )
                "
              >
                <option value="turnover_value">成交值</option>
                <option value="volume">成交量</option>
              </select>
            </label>
          </div>

          <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p
              class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500"
            >
              標籤查詢
            </p>
            <div class="relative w-full max-w-full sm:max-w-xs lg:max-w-sm">
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                <input
                  v-model="tagKeyword"
                  type="text"
                  class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                  placeholder="輸入標籤關鍵字"
                  @focus="showTagOptions = true"
                  @input="showTagOptions = true"
                  @keydown.enter.prevent="
                    matchedTags.length > 0
                      ? applyTagFilter(matchedTags[0])
                      : clearTagFilter()
                  "
                  @blur="hideTagOptionsWithDelay"
                />
                <button
                  type="button"
                  class="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100"
                  @click="clearTagFilter"
                >
                  全部
                </button>
              </div>

              <ul
                v-if="showTagOptions"
                class="absolute z-20 mt-1 max-h-[210px] w-full overflow-y-auto overflow-x-hidden rounded-lg border border-slate-200 bg-white shadow-lg"
              >
                <li
                  v-for="tag in matchedTags"
                  :key="tag"
                  class="cursor-pointer px-3 py-2 text-sm text-slate-700 hover:bg-indigo-50"
                  @mousedown.prevent="applyTagFilter(tag)"
                >
                  {{ tag }}
                </li>
                <li
                  v-if="matchedTags.length === 0"
                  class="px-3 py-2 text-sm text-slate-400"
                >
                  找不到符合的標籤
                </li>
              </ul>
            </div>
            <p class="mt-2 text-xs text-slate-500">
              下拉視窗一次顯示約 5 筆，可用滾輪上下滑動；目前篩選：{{
                selectedTag || "全部標籤"
              }}
            </p>
          </div>

          <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
            <p
              class="mb-2 text-xs font-bold uppercase tracking-wider text-slate-500"
            >
              產業查詢
            </p>
            <div class="relative w-full max-w-full sm:max-w-xs lg:max-w-sm">
              <div class="flex flex-col gap-2 sm:flex-row sm:items-center">
                <input
                  v-model="industryKeyword"
                  type="text"
                  class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
                  placeholder="輸入產業關鍵字"
                  @focus="showIndustryOptions = true"
                  @input="showIndustryOptions = true"
                  @keydown.enter.prevent="
                    matchedIndustries.length > 0
                      ? applyIndustryFilter(matchedIndustries[0])
                      : clearIndustryFilter()
                  "
                  @blur="hideIndustryOptionsWithDelay"
                />
                <button
                  type="button"
                  class="shrink-0 rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100"
                  @click="clearIndustryFilter"
                >
                  全部
                </button>
              </div>

              <ul
                v-if="showIndustryOptions"
                class="absolute z-20 mt-1 max-h-[210px] w-full overflow-y-auto overflow-x-hidden rounded-lg border border-slate-200 bg-white shadow-lg"
              >
                <li
                  v-for="industry in matchedIndustries"
                  :key="industry"
                  class="cursor-pointer px-3 py-2 text-sm text-slate-700 hover:bg-indigo-50"
                  @mousedown.prevent="applyIndustryFilter(industry)"
                >
                  {{ industry }}
                </li>
                <li
                  v-if="matchedIndustries.length === 0"
                  class="px-3 py-2 text-sm text-slate-400"
                >
                  找不到符合的產業
                </li>
              </ul>
            </div>
            <p class="mt-2 text-xs text-slate-500">
              下拉視窗一次顯示約 5 筆，可用滾輪上下滑動；目前篩選：{{
                selectedIndustry || "全部產業"
              }}
            </p>
          </div>
        </div>

        <label
          class="flex w-full items-center justify-between gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 sm:w-auto sm:justify-start xl:min-w-40 xl:flex-col xl:items-stretch"
        >
          <span>Top N</span>
          <input
            type="number"
            min="1"
            max="500"
            class="w-24 rounded-lg border border-slate-300 px-3 py-2 text-right sm:w-28 xl:w-full"
            :value="rankingStore.topN"
            @change="
              rankingStore.setTopN(
                Number(($event.target as HTMLInputElement).value) || 100,
              )
            "
          />
        </label>
      </section>

      <section
        v-if="activeSection === 'ranking'"
        class="mb-6 grid gap-4 md:grid-cols-2"
      >
        <article
          class="rounded-2xl border border-emerald-200 bg-white p-4 shadow-sm"
        >
          <h2 class="text-sm font-bold text-emerald-800">
            今日強勢族群（Top 出現頻率）
          </h2>
          <p class="mt-1 text-xs text-slate-500">以當前 Top N 出現次數排序</p>
          <ul class="mt-3 space-y-2">
            <li
              v-for="group in rankingStore.todayGroupFrequency.slice(0, 5)"
              :key="group.tag"
              class="flex items-center justify-between rounded-lg bg-emerald-50 px-3 py-2 text-sm"
            >
              <span class="font-semibold text-emerald-900">{{
                group.tag
              }}</span>
              <span class="text-emerald-700">{{ group.count }} 檔</span>
            </li>
          </ul>
        </article>

        <article
          class="rounded-2xl border border-amber-200 bg-white p-4 shadow-sm"
        >
          <h2 class="text-sm font-bold text-amber-800">族群性集體轉強</h2>
          <p class="mt-1 text-xs text-slate-500">相較昨日進榜數顯著增加</p>
          <ul
            v-if="rankingStore.groupStrengthening.length > 0"
            class="mt-3 space-y-2"
          >
            <li
              v-for="signal in rankingStore.groupStrengthening.slice(0, 5)"
              :key="signal.tag"
              class="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-900"
            >
              {{ signal.tag }}：{{ signal.yesterday_count }} ->
              {{ signal.today_count }}（+{{ signal.delta_count }}）
            </li>
          </ul>
          <p
            v-else
            class="mt-3 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-500"
          >
            目前無明顯族群集體轉強。
          </p>
        </article>
      </section>

      <p
        v-if="rankingStore.loading"
        class="mb-4 rounded-lg bg-sky-100 px-4 py-2 text-sm font-medium text-sky-800"
      >
        載入排行榜中...
      </p>
      <p
        v-if="rankingStore.error"
        class="mb-4 rounded-lg bg-rose-100 px-4 py-2 text-sm font-medium text-rose-800"
      >
        {{ rankingStore.error }}
      </p>
      <p
        v-if="
          !rankingStore.loading &&
          !rankingStore.error &&
          filteredRows.length === 0
        "
        class="mb-4 rounded-lg bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700"
      >
        目前沒有符合條件的資料。
      </p>

      <RankingTable
        v-if="activeSection === 'ranking' && filteredRows.length > 0"
        :rows="filteredRows"
        :ranking-metric="rankingStore.rankingMetric"
      />

      <TagManagerPanel
        v-if="activeSection === 'tag-manager'"
        :rows="rankingStore.tagEditorRows"
        :generated-date="rankingStore.tagCatalogDate"
        :total-symbols="rankingStore.tagCatalogTotalSymbols"
        :new-symbols-today="rankingStore.tagCatalogNewSymbolsToday"
        :saving-tags="rankingStore.savingTags"
        @add-tag="handleAddTag"
        @remove-tag="handleRemoveTag"
      />
    </section>

    <button
      v-show="showScrollTop"
      type="button"
      class="fixed bottom-4 right-4 z-20 inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-900 text-xs font-bold text-white shadow-lg transition hover:-translate-y-0.5 hover:bg-slate-700 sm:bottom-6 sm:right-6 sm:h-11 sm:w-11 sm:text-sm"
      aria-label="回到頂部"
      @click="scrollToTop"
    >
      Top
    </button>
  </main>
</template>
