<script setup lang="ts">
const modelValue = defineModel();
defineProps<{
  title?: string
}>();
</script>

<template>
  <div>
    <p v-if="title" class="font-medium text-sm ml-1">{{ title }}</p>
    <input v-model="modelValue" class="p-2 bg-neutral-900 rounded border dark:border-neutral-800 w-full" />
  </div>
</template>
