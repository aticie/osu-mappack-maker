<script setup lang="ts">
import Collection from "./components/Collection.vue";
import BaseInput from "./components/ui/BaseInput.vue";
import BaseButton from "./components/ui/BaseButton.vue";

import { ref, reactive, computed } from "vue";
import axios from "axios";

const isCollection = ref(false);
const isFetching = ref(false);
const ids = ref("");

// const progress = ref(0);
const fileDownload = reactive({
  progress: 0,
  total: 0,
});

const idsList = computed(() =>
  ids.value
    .split(" ")
    .filter((x) => x != "" && parseInt(x))
    .join(", ")
);

const download = async () => {
  if (!ids.value || idsList.value.length === 0) return;
  isFetching.value = true;

  try {
    const response = await axios("/api/make_pool", {
      responseType: "blob",
      params: {
        beatmaps: ids.value
      },
      onDownloadProgress: ({ progress, total }) => {
        if (!progress || !total) return;

        fileDownload.progress = progress * 100;
        fileDownload.total = total / (1000 * 1000);
      },
    });

    const file = URL.createObjectURL(response.data);
    location.assign(file);

    isCollection.value = true;
    URL.revokeObjectURL(file);
  } catch {
  } finally {
    isFetching.value = false;
    fileDownload.progress = 0;
    fileDownload.total = 0;
  }
};
</script>

<template>
  <main
    class="min-h-screen max-w-md mx-auto flex flex-col justify-center gap-6"
  >
    <BaseInput v-model="ids" title="Paste the beatmap ids and click to download mappack." />
    
    <div v-if="isFetching">
      <div
        class="flex flex-col items-center gap-2 p-2 bg-neutral-900 border dark:border-neutral-900 rounded"
      >
        <p class="text-center text-sm">
          {{ fileDownload.progress ? "Downloading" : "Creating" }} Mappack
        </p>

        <svg
          v-if="!fileDownload.progress"
          width="20"
          height="20"
          viewBox="0 0 22 22"
          fill="none"
          class="animate-spin"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            cx="11"
            cy="11"
            r="7"
            stroke="white"
            stroke-opacity="0.5"
            stroke-width="4"
          />
          <path
            d="M4.63604 17.364C3.37737 16.1053 2.5202 14.5016 2.17293 12.7558C1.82567 11.01 2.0039 9.20038 2.68508 7.55585C3.36627 5.91131 4.51983 4.50571 5.99987 3.51677C7.47991 2.52784 9.21997 2 11 2L11 6.00751C10.0126 6.00751 9.04733 6.30031 8.22632 6.84889C7.40531 7.39747 6.76541 8.1772 6.38754 9.08945C6.00967 10.0017 5.9108 11.0055 6.10343 11.974C6.29607 12.9424 6.77156 13.832 7.46977 14.5302L4.63604 17.364Z"
            fill="white"
          />
        </svg>
      </div>

      <div
        v-if="fileDownload.total"
        class="flex justify-between text-sm text-neutral-400 font-semibold mt-1"
      >
        <p>{{ fileDownload.progress.toFixed() }}%</p>
        <p>{{ fileDownload.total.toFixed() }}MB</p>
      </div>

      <div
        v-if="fileDownload.progress"
        class="h-6 w-full bg-neutral-900 rounded overflow-hidden"
      >
        <div
          class="bg-green-500 h-full"
          :style="{ width: `${fileDownload.progress}%` }"
        />
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <p v-if="idsList.length > 1" class="text-neutral-400 text-sm ml-1">
        Map ids you've copied {{ idsList }}
      </p>

      <BaseButton @click="download">
        Get Mappack!
      </BaseButton>
    </div>

    <Collection v-if="isCollection" />
  </main>
</template>
