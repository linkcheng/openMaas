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

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<style>
#app {
  font-family:
    'Inter',
    'Helvetica Neue',
    Helvetica,
    'PingFang SC',
    'Hiragino Sans GB',
    'Microsoft YaHei',
    '微软雅黑',
    -apple-system,
    BlinkMacSystemFont,
    'Segoe UI',
    Roboto,
    'Noto Sans',
    Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text-primary);
  min-height: 100vh;
  background-color: var(--color-background);

  /* Mobile optimization */
  -webkit-tap-highlight-color: transparent;
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* Allow text selection for form inputs and content areas */
input,
textarea,
[contenteditable='true'],
.selectable {
  -webkit-user-select: auto;
  -moz-user-select: auto;
  -ms-user-select: auto;
  user-select: auto;
}

/* iOS Safari specific fixes */
@supports (-webkit-touch-callout: none) {
  #app {
    /* Fix for iOS Safari viewport height */
    min-height: -webkit-fill-available;
  }
}

/* Android Chrome specific fixes */
@media screen and (max-width: 768px) {
  #app {
    /* Fix for Android Chrome viewport */
    min-height: calc(100vh - env(keyboard-inset-height, 0px));
  }
}

/* Global box-sizing reset */
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* Remove default margins and paddings */
body {
  margin: 0;
  padding: 0;

  /* Prevent horizontal scrolling on mobile */
  overflow-x: hidden;

  /* Smooth scrolling */
  scroll-behavior: smooth;

  /* Better font rendering */
  text-rendering: optimizeLegibility;
  font-feature-settings: 'kern' 1;
  -webkit-font-feature-settings: 'kern' 1;
  -moz-font-feature-settings: 'kern' 1;
}

/* Focus management for accessibility */
:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

:focus:not(:focus-visible) {
  outline: none;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  #app {
    filter: contrast(1.2);
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Print styles */
@media print {
  #app {
    background: white !important;
    color: black !important;
  }
}
</style>
