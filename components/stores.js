import { writable } from 'svelte/store';

export const annotationStore = writable({
  videos: [],
  labels: [],
  reviewer: '',
  currentIndex: 0,
  isSetup: true
});

export const exportStore = writable({
  format: 'csv', // csv or json
  outputPath: 'data/export/ai_original/babydog-sightings.csv'
});
