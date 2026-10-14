<script setup lang="ts">
import { ref } from 'vue';
import { CheckCircle2, X } from '@lucide/vue';
const emit = defineEmits<{ accept: [] }>();
const dialog = ref<HTMLDialogElement>();
defineExpose({ open: () => dialog.value?.showModal() });
const sections = [
  {
    title: 'Image Quality Requirements',
    items: [
      'Use sharp images, preferably 512px or larger (minimum 256px per side)',
      'Clear, well-lit subjects with minimal blur',
      'Include natural variations in lighting',
      'Sharp focus on the main subject',
    ],
  },
  {
    title: 'Subject Guidelines',
    items: [
      'Include various angles and poses',
      'Maintain consistent subject distance',
      'Avoid busy or distracting backgrounds',
      'Include 20-30 images for optimal results',
    ],
  },
  {
    title: 'Technical Specifications',
    items: [
      'Supported formats: JPG, JPEG, PNG, WebP',
      'Maximum file size: 50MB per image',
      'Add a matching UTF-8 .txt caption for each image',
      'Use your trigger word in the captions',
    ],
  },
  {
    title: 'Best Practices',
    items: [
      'Remove any watermarks or text overlays',
      'Ensure consistent image style',
      'Avoid heavily edited or filtered images',
      'Include natural variations in lighting and background',
    ],
  },
];
function accept() {
  dialog.value?.close();
  emit('accept');
}
</script>
<template>
  <dialog
    ref="dialog"
    aria-labelledby="guidelines-title"
    aria-describedby="guidelines-description"
    @click="$event.target === dialog && dialog?.close()"
  >
    <div class="dialog-content">
      <button
        class="icon-button dialog-close"
        aria-label="Close guidelines"
        @click="dialog?.close()"
      >
        <X />
      </button>
      <h2 id="guidelines-title">Image Guidelines for Best Results</h2>
      <p id="guidelines-description" class="muted">
        Please read these guidelines carefully to ensure optimal training
        results
      </p>
      <div class="guidelines-scroll">
        <section v-for="section in sections" :key="section.title">
          <h3>{{ section.title }}</h3>
          <ul>
            <li v-for="item in section.items" :key="item">{{ item }}</li>
          </ul>
        </section>
      </div>
      <button class="button primary full" @click="accept">
        <CheckCircle2 />
        I have read the guidelines and want to proceed
      </button>
    </div>
  </dialog>
</template>
