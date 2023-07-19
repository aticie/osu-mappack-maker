<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { emitter, Event } from "../composables/useMitt";

interface EventWithId extends Event {
  id: number;
}

const notifications = ref<Array<EventWithId>>([]);

onMounted(() => {
  emitter.on("notify", (e) => {
    let id = Math.random();

    notifications.value.push({
      id: id,
      ...e,
    });

    setTimeout(() => {
      let found = notifications.value.findIndex((x) => x.id === id);
      notifications.value.splice(found, 1);
    }, 5000);
  });
});

onUnmounted(() => {
  emitter.off("notify");
});

const beforeLeave = (el: Element) => {
  const element = el as HTMLElement;

  const { width, height } = element.getBoundingClientRect();
  element.style.width = `${width}px`;
  element.style.height = `${height}px`;
};
</script>

<template>
  <TransitionGroup
    tag="div"
    class="fixed top-5 left-5 flex flex-col gap-2 text-sm"
    enter-from-class="opacity-0 -translate-x-full"
    leave-to-class="opacity-0 -translate-x-full"
    leave-active-class="absolute"
    @beforeLeave="beforeLeave"
  >
    <div
      v-for="notif in notifications"
      :key="notif.id"
      class="flex gap-2 p-2 bg-neutral-900 rounded-md border border-neutral-800 max-w-sm transition-all"
    >
      <svg
        v-if="notif.error"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 -960 960 960"
        class="w-8 h-8 aspect-square shrink-0 rounded-full p-0.5"
      >
        <path
          class="fill-red-400"
          d="M479.982-280q14.018 0 23.518-9.482 9.5-9.483 9.5-23.5 0-14.018-9.482-23.518-9.483-9.5-23.5-9.5-14.018 0-23.518 9.482-9.5 9.483-9.5 23.5 0 14.018 9.482 23.518 9.483 9.5 23.5 9.5ZM453-433h60v-253h-60v253Zm27.266 353q-82.734 0-155.5-31.5t-127.266-86q-54.5-54.5-86-127.341Q80-397.681 80-480.5q0-82.819 31.5-155.659Q143-709 197.5-763t127.341-85.5Q397.681-880 480.5-880q82.819 0 155.659 31.5Q709-817 763-763t85.5 127Q880-563 880-480.266q0 82.734-31.5 155.5T763-197.684q-54 54.316-127 86Q563-80 480.266-80Zm.234-60Q622-140 721-239.5t99-241Q820-622 721.188-721 622.375-820 480-820q-141 0-240.5 98.812Q140-622.375 140-480q0 141 99.5 240.5t241 99.5Zm-.5-340Z"
        />
      </svg>

      <div>
        <h1 class="font-semibold">{{ notif.title }}</h1>
        <p class="col-start-2 break-all">{{ notif.message }}</p>
      </div>
    </div>
  </TransitionGroup>
</template>
