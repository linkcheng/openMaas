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
  <div class="application-management">
    <div class="page-header">
      <h1 class="page-title">应用管理</h1>
      <p class="page-description">管理 AI 应用的创建和配置</p>
    </div>

    <div class="content-placeholder">
      <el-empty description="应用管理功能开发中">
        <el-button type="primary">了解更多</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
// 应用管理页面
</script>

<style scoped>
.application-management {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.page-description {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.content-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400px;
}
</style>
