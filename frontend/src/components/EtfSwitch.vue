<script setup lang="ts">
const model = defineModel<boolean>({ required: true })
</script>

<template>
  <label class="inline-flex cursor-pointer items-center gap-3">
    <span class="text-sm font-semibold text-slate-700">顯示 ETF</span>
    <button
      type="button"
      class="relative h-7 w-14 rounded-full transition-colors"
      :class="model ? 'bg-emerald-500' : 'bg-slate-300'"
      @click="model = !model"
      :aria-pressed="model"
    >
      <span
        class="absolute top-1 h-5 w-5 rounded-full bg-white shadow transition-transform"
        :class="model ? 'translate-x-8' : 'translate-x-1'"
      />
    </button>
  </label>
</template>
