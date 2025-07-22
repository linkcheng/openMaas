<template>
  <div class="model-finetune">
    <div class="page-header">
      <h1 class="page-title">模型微调</h1>
      <p class="page-description">对预训练模型进行微调优化</p>
    </div>

    <div class="content-placeholder">
      <el-empty description="模型微调功能开发中">
        <el-button type="primary">了解更多</el-button>
      </el-empty>
    </div>
  </div>
</template>

<script setup lang="ts">
// 模型微调页面
</script>

<style scoped>
.model-finetune {
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