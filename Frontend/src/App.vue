<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { Brain, Sun, Moon, X } from '@lucide/vue';
import ModelInfoForm from './components/ModelInfoForm.vue';
import ModelSettingsPage from './components/ModelSettingsPage.vue';
import InferencePage from './components/InferencePage.vue';
import { useModels } from './composables/useModels';
import { defaultSettings, type ModelInfo } from './types';
const pages = [
  {
    id: 'inference',
    label: 'Inference',
    title: 'Image Inference',
    description: 'Create portraits with your local models and LoRAs',
  },
  {
    id: 'models',
    label: 'Model Settings',
    title: 'Model Settings',
    description: 'Manage the models and LoRAs available on this PC',
  },
  {
    id: 'training',
    label: 'Training',
    title: 'LoRA Training',
    description: 'Train a portrait LoRA from your own image dataset',
  },
] as const;
type Page = (typeof pages)[number]['id'];
const activeTab = ref<Page>('inference');
const page = computed(() => pages.find((page) => page.id === activeTab.value)!);
const model = ref<ModelInfo>({ name: '', type: 'human', characteristics: {} });
const settings = ref(defaultSettings());
const library = useModels();
const notice = ref('');
const suggestedDataset = ref<File>();
function receiveDataset(dataset: File) {
  suggestedDataset.value = dataset;
  activeTab.value = 'training';
}
onMounted(library.refresh);
const systemTheme = window.matchMedia('(prefers-color-scheme: dark)');
function storedTheme() {
  try {
    return localStorage.getItem('theme');
  } catch {
    return null;
  }
}
const theme = ref(storedTheme() || 'system');
const dark = ref(false);
function applyTheme() {
  dark.value =
    theme.value === 'dark' || (theme.value === 'system' && systemTheme.matches);
  document.documentElement.classList.toggle('dark', dark.value);
  document.documentElement.style.colorScheme = dark.value ? 'dark' : 'light';
}
watch(theme, (value) => {
  applyTheme();
  try {
    localStorage.setItem('theme', value);
  } catch {
    /* Storage may be disabled. */
  }
});
onMounted(() => {
  applyTheme();
  systemTheme.addEventListener('change', applyTheme);
});
onUnmounted(() => systemTheme.removeEventListener('change', applyTheme));

function moveTab(event: KeyboardEvent) {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
  event.preventDefault();
  const index = pages.findIndex((page) => page.id === activeTab.value);
  const next =
    event.key === 'Home'
      ? 0
      : event.key === 'End'
        ? pages.length - 1
        : (index + (event.key === 'ArrowRight' ? 1 : -1) + pages.length) %
          pages.length;
  activeTab.value = pages[next].id;
  document.getElementById(`tab-${activeTab.value}`)?.focus();
}
</script>
<template>
  <header class="site-header">
    <div class="header-content">
      <div class="brand inline">
        <Brain />
        <span>LoRA Studio</span>
      </div>
      <div class="inline">
        <button
          class="icon-button theme-toggle"
          aria-label="Toggle theme"
          @click="theme = dark ? 'light' : 'dark'"
        >
          <Moon v-if="dark" />
          <Sun v-else />
        </button>
      </div>
    </div>
  </header>
  <main class="studio">
    <div class="intro">
      <h1>{{ page.title }}</h1>
      <p>{{ page.description }}</p>
    </div>
    <div
      class="tabs studio-tabs"
      role="tablist"
      aria-label="LoRA Studio pages"
      @keydown="moveTab"
    >
      <button
        v-for="item in pages"
        :key="item.id"
        :id="`tab-${item.id}`"
        role="tab"
        :aria-selected="activeTab === item.id"
        :aria-controls="`panel-${item.id}`"
        :tabindex="activeTab === item.id ? 0 : -1"
        @click="activeTab = item.id"
      >
        {{ item.label }}
      </button>
    </div>
    <section
      v-show="activeTab === 'inference'"
      id="panel-inference"
      role="tabpanel"
      aria-labelledby="tab-inference"
    >
      <InferencePage
        :library="library"
        @models="activeTab = 'models'"
        @train="receiveDataset"
        @notice="notice = $event"
      />
    </section>
    <section
      v-show="activeTab === 'models'"
      id="panel-models"
      role="tabpanel"
      aria-labelledby="tab-models"
    >
      <ModelSettingsPage :library="library" @use="activeTab = 'inference'" />
    </section>
    <section
      v-show="activeTab === 'training'"
      id="panel-training"
      role="tabpanel"
      aria-labelledby="tab-training"
    >
      <ModelInfoForm
        v-model="model"
        v-model:settings="settings"
        :suggested-dataset="suggestedDataset"
        @dataset-used="suggestedDataset = undefined"
        @notice="notice = $event"
      />
    </section>
  </main>
  <aside v-if="notice" class="toast card" role="status">
    <span>{{ notice }}</span>
    <button
      class="icon-button"
      aria-label="Dismiss notification"
      @click="notice = ''"
    >
      <X />
    </button>
  </aside>
</template>
