<template>
  <div class="application-scenarios">
    <div class="page-header">
      <h1 class="page-title">应用场景</h1>
      <p class="page-description">探索和部署 AI 应用场景</p>
    </div>

    <div class="content-placeholder">
      <el-empty description="应用场景功能开发中">
        <el-button type="primary">了解更多</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
// 应用场景页面
</script>

<style scoped>
.application-scenarios {
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