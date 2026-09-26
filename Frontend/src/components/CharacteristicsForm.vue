<script setup lang="ts">
import type { ModelType } from '../types';
defineProps<{ type: ModelType }>();
const values = defineModel<Record<string, string | number>>({ required: true });
const selects = [
  { key: 'gender', label: 'Gender', options: ['male', 'female', 'other'] },
  {
    key: 'eyeColor',
    label: 'Eye Color',
    options: ['brown', 'blue', 'green', 'hazel', 'gray'],
  },
  {
    key: 'bodyType',
    label: 'Body Type',
    options: ['slim', 'athletic', 'average', 'curvy', 'muscular'],
  },
  {
    key: 'ethnicity',
    label: 'Ethnicity',
    options: ['asian', 'black', 'hispanic', 'white', 'middleEastern', 'other'],
  },
];
const petFields = [
  { key: 'species', label: 'Species', placeholder: 'e.g., Dog, Cat, Bird' },
  { key: 'color', label: 'Color', placeholder: 'e.g., Brown, Black & White' },
  {
    key: 'distinctiveTrait',
    label: 'Distinctive Trait',
    placeholder: 'e.g., Long fur, Spotted coat',
  },
];
function label(value: string) {
  return value === 'middleEastern'
    ? 'Middle Eastern'
    : value[0].toUpperCase() + value.slice(1);
}
</script>
<template>
  <div v-if="type === 'human'" class="field-grid">
    <div class="field">
      <label for="age">Age</label>
      <input
        id="age"
        v-model.number="values.age"
        type="number"
        min="0"
        max="100"
      />
    </div>
    <div v-for="field in selects" :key="field.key" class="field">
      <label :for="field.key">{{ field.label }}</label>
      <select
        :id="field.key"
        :value="values[field.key] ?? ''"
        @change="values[field.key] = ($event.target as HTMLSelectElement).value"
      >
        <option disabled value="">
          Select {{ field.label.toLowerCase() }}
        </option>
        <option v-for="option in field.options" :key="option" :value="option">
          {{ label(option) }}
        </option>
      </select>
    </div>
  </div>
  <div v-else-if="type === 'pet'" class="field-grid">
    <div
      v-for="field in petFields"
      :key="field.key"
      class="field"
      :class="{ 'full-row': field.key === 'distinctiveTrait' }"
    >
      <label :for="field.key">{{ field.label }}</label>
      <input
        :id="field.key"
        v-model="values[field.key]"
        :placeholder="field.placeholder"
      />
    </div>
  </div>
  <div v-else class="field">
    <label for="purpose">Purpose</label>
    <input
      id="purpose"
      v-model="values.purpose"
      placeholder="e.g., Furniture, Tool, Decoration"
    />
  </div>
</template>
