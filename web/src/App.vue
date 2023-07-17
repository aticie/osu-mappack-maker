<script setup lang="ts">
import Collection from "./components/Collection.vue";
import BaseInput from "./components/ui/BaseInput.vue";
import BaseButton from "./components/ui/BaseButton.vue";
import Spinner from "./components/icons/Spinner.vue";

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
        beatmaps: ids.value
      }
    });

    downloadWithHref(response.data);
    isCollection.value = true;
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
    class="min-h-screen max-w-md mx-auto flex flex-col justify-center gap-6 p-2"
  >
    <BaseInput v-model="ids" title="Paste the beatmap ids and click to download mappack." />

    <div v-if="isFetching" class="grid gap-2 place-content-center justify-items-center bg-neutral-900 p-2 rounded">
      <p>Creating Mappack</p>
      <Spinner />
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
