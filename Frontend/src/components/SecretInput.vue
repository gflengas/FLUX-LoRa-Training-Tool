<script setup lang="ts">
import { ref } from 'vue';
import { Eye, EyeOff } from '@lucide/vue';
defineProps<{ id: string; label: string; placeholder?: string }>();
const value = defineModel<string>({ required: true });
const visible = ref(false);
</script>
<template>
  <div class="secret-input">
    <input
      :id="id"
      v-model="value"
      :type="visible ? 'text' : 'password'"
      :placeholder="placeholder"
      autocomplete="off"
      spellcheck="false"
    />
    <button
      type="button"
      class="icon-button"
      :aria-label="`${visible ? 'Hide' : 'Show'} ${label}`"
      :aria-pressed="visible"
      @click="visible = !visible"
    >
      <EyeOff v-if="visible" />
      <Eye v-else />
    </button>
  </div>
</template>
