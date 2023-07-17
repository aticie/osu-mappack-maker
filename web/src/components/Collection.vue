<script setup lang="ts">
import BaseInput from "./ui/BaseInput.vue";
import BaseButton from "./ui/BaseButton.vue";
import axios from "axios";
import { ref } from "vue";

const collectionName = ref("");
const collectionFile = ref<File | undefined>();

const onFileChange = (event: Event) => {
  let target = event.target as HTMLInputElement;
  collectionFile.value = target.files?.[0];
};

const updateCollection = async () => {
  if (!collectionFile.value || !collectionName.value) return;

  try {
    const formData = new FormData();
    formData.append("file", collectionFile.value);

    const response = await axios.post("/api/update_collection", formData, {
      responseType: "blob",
      params: {
        mappack_name: collectionName.value
      }
    });

    const href = URL.createObjectURL(response.data);
    const link = document.createElement("a");

    link.href = href;
    link.setAttribute("download", "collection.db");

    document.body.appendChild(link);
    link.click();

    document.body.removeChild(link);
  } catch {

  }
};
</script>

<template>
  <div class="grid gap-3 border border-neutral-800 bg-neutral-900 rounded p-4">
    <BaseInput v-model="collectionName" title="Collection Name" />
    <input
      @change="onFileChange"
      type="file"
      class="file:rounded-full file:border-0 file:px-4 file:py-2 file:text-white file:font-semibold file:bg-rose-800 file:hover:bg-rose-900 text-sm"
      accept=".db"
    />

    <BaseButton @click="updateCollection"> Update Mappack! </BaseButton>
  </div>
</template>
