<script setup lang="ts">
const modelValue = defineModel();
defineProps<{
  label?: string;
}>();
</script>

<template>
  <div>
    <label v-if="label" class="font-medium text-sm ml-1" for="label">{{
      label
    }}</label>
    <input
      id="label"
      v-model="modelValue"
      class="p-2 bg-surface-container-highest rounded w-full"
    />
  </div>
</template>
