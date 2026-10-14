<script setup lang="ts">
import { ref } from 'vue';
import { ArrowUp, Folder, X } from '@lucide/vue';
import { fetchDatasetFolders } from '../api';
import type { DatasetFolders } from '../types';
const emit = defineEmits<{ select: [path: string] }>();
const dialog = ref<HTMLDialogElement>();
const listing = ref<DatasetFolders>();
const path = ref('');
const busy = ref(false);
const error = ref('');
async function browse(target = '') {
  if (busy.value) return;
  busy.value = true;
  error.value = '';
  listing.value = undefined;
  try {
    listing.value = await fetchDatasetFolders(target);
    path.value = listing.value.path;
  } catch (cause) {
    error.value =
      cause instanceof Error ? cause.message : 'Could not read folders.';
  } finally {
    busy.value = false;
  }
}
defineExpose({
  open: (initial: string) => {
    path.value = initial;
    dialog.value?.showModal();
    void browse(initial);
  },
});
function select() {
  if (!listing.value || busy.value) return;
  emit('select', listing.value.path);
  dialog.value?.close();
}
</script>
<template>
  <dialog ref="dialog" aria-labelledby="folder-title">
    <div class="dialog-content stack-large">
      <button
        class="icon-button dialog-close"
        aria-label="Close folder browser"
        @click="dialog?.close()"
      >
        <X />
      </button>
      <h2 id="folder-title">Select Dataset Folder</h2>
      <form class="stack" @submit.prevent="browse(path.trim())">
        <label for="browse-path">Folder on this PC</label>
        <div class="inline">
          <input
            id="browse-path"
            v-model="path"
            placeholder="/home/your-user/Pictures"
            :disabled="busy"
          />
          <button class="button outline" :disabled="busy">Go</button>
        </div>
      </form>
      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <p v-if="busy" role="status">Loading folders…</p>
      <template v-if="listing">
        <button
          v-if="listing.parent"
          class="button outline"
          @click="browse(listing.parent!)"
        >
          <ArrowUp />
          Parent Folder
        </button>
        <div class="folder-list stack" aria-label="Subfolders">
          <button
            v-for="folder in listing.folders"
            :key="folder.path"
            class="button outline"
            @click="browse(folder.path)"
          >
            <Folder />
            {{ folder.name }}
          </button>
          <p v-if="!listing.folders.length" class="muted">
            No subfolders. You can select this folder.
          </p>
        </div>
        <p class="muted local-path">{{ listing.path }}</p>
      </template>
      <button
        class="button primary full"
        :disabled="!listing || busy"
        @click="select"
      >
        Use This Folder
      </button>
    </div>
  </dialog>
</template>
