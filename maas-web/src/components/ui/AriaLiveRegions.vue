<!--
 Copyright 2025 MaaS Team

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

<template>
  <!-- ARIA Live Regions for screen reader announcements -->
  <div class="aria-live-regions">
    <!-- Polite announcements - won't interrupt current speech -->
    <div
      ref="politeRegionRef"
      class="sr-only"
      aria-live="polite"
      aria-atomic="true"
      role="status"
    ></div>

    <!-- Assertive announcements - will interrupt current speech -->
    <div
      ref="assertiveRegionRef"
      class="sr-only"
      aria-live="assertive"
      aria-atomic="true"
      role="alert"
    ></div>

    <!-- Status region for loading states -->
    <div class="sr-only" aria-live="polite" aria-atomic="false" role="status">
      <span v-if="loading">{{ loadingMessage }}</span>
    </div>

    <!-- Error region for form validation -->
    <div class="sr-only" aria-live="assertive" aria-atomic="true" role="alert">
      <span v-if="errorMessage">{{ errorMessage }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, provide } from 'vue'
import { useAriaAnnouncements } from '@/composables/useAriaAnnouncements'

interface Props {
  loading?: boolean
  loadingMessage?: string
  errorMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  loadingMessage: '正在加载',
  errorMessage: '',
})

// Use the ARIA announcements composable
const { politeRegionRef, assertiveRegionRef } = useAriaAnnouncements()

// Provide the refs to child components
provide('ariaPoliteRegion', politeRegionRef)
provide('ariaAssertiveRegion', assertiveRegionRef)

onMounted(() => {
  // Ensure the live regions are properly initialized
  if (politeRegionRef.value) {
    politeRegionRef.value.setAttribute('aria-label', '状态更新')
  }

  if (assertiveRegionRef.value) {
    assertiveRegionRef.value.setAttribute('aria-label', '重要通知')
  }
})
</script>

<style scoped>
.aria-live-regions {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
