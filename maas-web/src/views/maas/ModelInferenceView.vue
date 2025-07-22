<template>
  <div class="model-inference">
    <div class="page-header">
      <h1 class="page-title">模型推理</h1>
      <p class="page-description">在线模型推理和 API 服务</p>
    </div>

    <div class="content-placeholder">
      <el-empty description="模型推理功能开发中">
        <el-button type="primary">了解更多</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
// 模型推理页面
</script>

<style scoped>
.model-inference {
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