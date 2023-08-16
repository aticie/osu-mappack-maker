<script setup lang="ts">
import BaseInput from "./components/ui/BaseInput.vue";
import BaseButton from "./components/ui/BaseButton.vue";
import Spinner from "./components/icons/Spinner.vue";
import TheToast from "./components/TheToast.vue";

import { emitter } from "./composables/useMitt";
import { ref, reactive, computed } from "vue";
import axios from "axios";

// const showCollection = ref(false);
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
        beatmaps: ids.value,
      },
      onDownloadProgress: ({ progress, total }) => {
        if (!progress || !total) return;

        fileDownload.progress = progress * 100;
        fileDownload.total = total / (1000 * 1000);
      },
    });

    const file = URL.createObjectURL(response.data);
    location.assign(file);

    URL.revokeObjectURL(file);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      emitter.emit("notify", {
        title: error.message,
        message: "An error occured when creating mappack.",
        error: true,
      });
    }
  } finally {
    isFetching.value = false;
    fileDownload.progress = 0;
    fileDownload.total = 0;
  }
};
</script>

<template>
  <TheToast />

  <main
    class="min-h-screen max-w-md mx-auto flex flex-col justify-center gap-6 p-2 pb-10"
  >
    <h1 class="text-center font-semibold text-lg text-primary mb-10">
      heyronii's Mappack Maker
    </h1>

    <BaseInput
      v-model="ids"
      label="Paste the beatmap ids and click to download mappack."
    />

    <div
      v-if="isFetching"
      class="grid gap-2 justify-items-center bg-surface-container rounded overflow-hidden"
    >
      <div class="p-2 grid justify-items-center gap-2">
        <p class="text-surface-on">Creating Mappack</p>
        <Spinner />
      </div>

      <div
        v-if="fileDownload.progress"
        class="h-6 w-full bg-surface-container-highest overflow-hidden"
      >
        <div
          :style="{ width: `${fileDownload.progress}%` }"
          class="h-full bg-primary"
        />
      </div>
    </div>

    <div class="flex flex-col gap-1">
      <p v-if="idsList.length > 1" class="text-sm ml-1 font-medium">
        Map ids you've copied {{ idsList }}
      </p>

      <BaseButton @click="download"> Get Mappack! </BaseButton>
    </div>

    <!-- <TheCollection v-if="showCollection" /> -->
  </main>
</template>
