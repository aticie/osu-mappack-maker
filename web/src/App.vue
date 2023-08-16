<script setup lang="ts">
import TheCollection from "./components/TheCollection.vue";
import BaseInput from "./components/ui/BaseInput.vue";
import BaseButton from "./components/ui/BaseButton.vue";
import Spinner from "./components/icons/Spinner.vue";
import TheToast from "./components/TheToast.vue";

import { emitter } from "./composables/useMitt";
import { downloadWithHref } from "./download";
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
        beatmaps: ids.value,
      },
    });

    downloadWithHref(response.data);
    isCollection.value = true;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      emitter.emit("notify", {
        title: error.message,
        message: "An error occured when creating mappack.",
        error: true
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
    class="min-h-screen max-w-md mx-auto flex flex-col justify-center gap-6 p-2"
  >
    <BaseInput
      v-model="ids"
      label="Paste the beatmap ids and click to download mappack."
    />

    <div
      v-if="!isFetching"
      class="grid gap-2 place-content-center justify-items-center bg-surface-container p-2 rounded"
    >
      <p class="text-surface-on">Creating Mappack</p>
      <Spinner />
    </div>

    <div class="flex flex-col gap-1">
      <p v-if="idsList.length > 1" class="text-sm ml-1 font-medium">
        Map ids you've copied {{ idsList }}
      </p>

      <BaseButton @click="download"> Get Mappack! </BaseButton>
    </div>

    <TheCollection v-if="isCollection" />
  </main>
</template>
