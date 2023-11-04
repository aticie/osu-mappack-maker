<script setup lang="ts">
import BaseInput from "./components/ui/BaseInput.vue";
import BaseButton from "./components/ui/BaseButton.vue";
import Spinner from "./components/icons/Spinner.vue";
import TheToast from "./components/TheToast.vue";

import { emitter } from "./composables/useMitt";
import { ref, reactive, computed } from "vue";
import axios from "axios";

const isFetching = ref(false);
const isGathering = ref(false);
const isDownloading = ref(false);
const ids = ref("");
const job_id = ref();
const processProgress = reactive({
  beatmaps: 0,
  gathered: 0,
  downloaded: 0,
  errors: "",
});
var DlErrors = 0;

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
      responseType: "text",
      params: {
        beatmaps: ids.value,
      },
    });
    job_id.value = response.data;
    var loc = window.location,
      wsUrl;
    if (loc.protocol === "https:") {
      wsUrl = "wss:";
    } else {
      wsUrl = "ws:";
    }
    wsUrl += "//" + loc.host;
    const ws = new WebSocket(wsUrl + `/api/jobs/${job_id.value}`);
    ws.onmessage = async (event) => {
      let eventDataObj = JSON.parse(event.data);
      if (eventDataObj.errors) {
        DlErrors += 1;
        emitter.emit("notify", {
          title: eventDataObj.errors,
          message: "A beatmap could not be downloaded.",
          error: true,
        });
      }
      if (!eventDataObj.completed) {
        processProgress.beatmaps = eventDataObj.beatmaps;
        processProgress.gathered = eventDataObj.gathered;
        processProgress.downloaded = eventDataObj.downloaded;

        if (processProgress.beatmaps - DlErrors === processProgress.gathered) {
          isGathering.value = false;
        } else {
          isGathering.value = true;
        }
        if (
          processProgress.beatmaps - DlErrors ===
          processProgress.downloaded
        ) {
          isDownloading.value = false;
        } else {
          isDownloading.value = true;
        }
      } else {
        const response = await axios(`/${eventDataObj.result_path}`, {
          responseType: "blob",
          onDownloadProgress: ({ progress, total }) => {
            if (!progress || !total) return;

            fileDownload.progress = progress * 100;
            fileDownload.total = total / (1000 * 1000);
          },
        });
        const file = URL.createObjectURL(response.data);
        location.assign(file);
        URL.revokeObjectURL(file);
        isFetching.value = false;
        fileDownload.progress = 0;
        fileDownload.total = 0;
      }
    };
  } catch (error) {
    if (axios.isAxiosError(error)) {
      emitter.emit("notify", {
        title: error.message,
        message: "An error occured when creating mappack.",
        error: true,
      });
    } else {
      console.error(error);
    }
  } finally {
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
        <div class="text-surface-on flex flex-row">
          <p>Creating Mappack</p>
        </div>
        <p class="text-surface-on flex flex-row gap-2">
          Gathering {{ processProgress.gathered }}/{{
            processProgress.beatmaps
          }}
          <Spinner v-if="isGathering" />
        </p>
        <p class="text-surface-on flex flex-row gap-2">
          Downloading {{ processProgress.downloaded }}/{{
            processProgress.beatmaps
          }}
          <Spinner v-if="isDownloading" />
        </p>
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

    <div class="flex flex-col gap-1" id="messages">
      <p v-if="idsList.length > 1" class="text-sm ml-1 font-medium">
        Map ids you've copied {{ idsList }}
      </p>

      <BaseButton @click="download"> Get Mappack! </BaseButton>
    </div>

    <!-- <TheCollection v-if="showCollection" /> -->
  </main>
</template>
