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
  <div class="model-management">
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">模型管理</h1>
          <p class="page-description">管理AI模型的训练、部署和版本控制</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Plus" @click="createModel"> 创建模型 </el-button>
          <el-button :icon="Upload" @click="importModel"> 导入模型 </el-button>
        </div>
      </div>
    </div>

    <!-- 模型统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon models">
                <el-icon><Box /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalModels }}</div>
                <div class="stat-label">模型总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon deployed">
                <el-icon><Cloudy /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.deployedModels }}</div>
                <div class="stat-label">已部署模型</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon training">
                <el-icon><Setting /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.trainingModels }}</div>
                <div class="stat-label">训练中模型</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon performance">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.avgPerformance }}</div>
                <div class="stat-label">平均性能</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 模型卡片视图 -->
    <div class="models-grid">
      <el-row :gutter="24">
        <el-col v-for="model in filteredModels" :key="model.id" :xs="24" :sm="12" :lg="8" :xl="6">
          <el-card class="model-card" shadow="hover">
            <template #header>
              <div class="model-header">
                <div class="model-title">
                  <h3>{{ model.name }}</h3>
                  <el-tag :type="getStatusTagType(model.status)" size="small">
                    {{ getStatusText(model.status) }}
                  </el-tag>
                </div>
              </div>
            </template>

            <div class="model-content">
              <div class="model-info">
                <div class="info-item">
                  <span class="label">模型类型:</span>
                  <span class="value">{{ model.type }}</span>
                </div>
                <div class="info-item">
                  <span class="label">版本:</span>
                  <span class="value">{{ model.version }}</span>
                </div>
                <div class="info-item">
                  <span class="label">准确率:</span>
                  <span class="value">{{ model.accuracy }}</span>
                </div>
                <div class="info-item">
                  <span class="label">创建时间:</span>
                  <span class="value">{{ model.created_at }}</span>
                </div>
              </div>

              <!-- 性能指标 -->
              <div class="performance-chart">
                <div class="chart-placeholder">
                  <el-icon><TrendCharts /></el-icon>
                  <span>性能趋势</span>
                </div>
              </div>
            </div>

            <template #footer>
              <div class="model-actions">
                <el-button size="small" @click="viewModel(model)"> 查看详情 </el-button>
                <el-dropdown @command="handleModelAction">
                  <el-button size="small" type="primary">
                    操作
                    <el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item :command="{ action: 'deploy', model }">
                        部署
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'finetune', model }">
                        微调
                      </el-dropdown-item>
                      <el-dropdown-item :command="{ action: 'version', model }">
                        版本管理
                      </el-dropdown-item>
                      <el-dropdown-item divided :command="{ action: 'delete', model }">
                        删除
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[8, 16, 24, 32]"
        :total="totalItems"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Box, Cloudy, Setting, TrendCharts, ArrowDown } from '@element-plus/icons-vue'

interface Model {
  id: string
  name: string
  type: string
  version: string
  accuracy: string
  status: 'training' | 'ready' | 'deployed' | 'error'
  created_at: string
}

// 响应式数据
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(8)

// 统计数据
const stats = reactive({
  totalModels: 0,
  deployedModels: 0,
  trainingModels: 0,
  avgPerformance: '0%',
})

// 模型列表
const models = ref<Model[]>([])
const totalItems = ref(0)

// 计算属性
const filteredModels = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return models.value.slice(start, end)
})

// 方法
const getStatusTagType = (status: string) => {
  const statusMap: Record<string, string> = {
    training: 'warning',
    ready: 'success',
    deployed: 'info',
    error: 'danger',
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusText: Record<string, string> = {
    training: '训练中',
    ready: '就绪',
    deployed: '已部署',
    error: '错误',
  }
  return statusText[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    // 模拟数据加载
    await new Promise((resolve) => setTimeout(resolve, 1000))

    // 模拟数据
    models.value = [
      {
        id: '1',
        name: 'ChatGLM-6B',
        type: 'LLM',
        version: 'v1.2.0',
        accuracy: '92.5%',
        status: 'deployed',
        created_at: '2024-01-15',
      },
      {
        id: '2',
        name: 'BERT-Base-Chinese',
        type: 'NLP',
        version: 'v1.0.0',
        accuracy: '89.3%',
        status: 'ready',
        created_at: '2024-01-12',
      },
      {
        id: '3',
        name: 'ResNet-50',
        type: 'Computer Vision',
        version: 'v2.1.0',
        accuracy: '95.7%',
        status: 'training',
        created_at: '2024-01-10',
      },
      {
        id: '4',
        name: 'GPT-3.5-Turbo',
        type: 'LLM',
        version: 'v1.0.0',
        accuracy: '88.9%',
        status: 'deployed',
        created_at: '2024-01-08',
      },
    ]

    stats.totalModels = models.value.length
    stats.deployedModels = models.value.filter((item) => item.status === 'deployed').length
    stats.trainingModels = models.value.filter((item) => item.status === 'training').length
    stats.avgPerformance = '91.6%'
    totalItems.value = models.value.length
  } catch {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

const createModel = () => {
  ElMessage.info('创建模型功能开发中')
}

const importModel = () => {
  ElMessage.info('导入模型功能开发中')
}

const viewModel = (model: Model) => {
  ElMessage.info(`查看模型详情: ${model.name}`)
}

const handleModelAction = async ({ action, model }: { action: string; model: Model }) => {
  switch (action) {
    case 'deploy':
      ElMessage.info(`部署模型: ${model.name}`)
      break
    case 'finetune':
      ElMessage.info(`微调模型: ${model.name}`)
      break
    case 'version':
      ElMessage.info(`版本管理: ${model.name}`)
      break
    case 'delete':
      try {
        await ElMessageBox.confirm(
          `确定要删除模型 "${model.name}" 吗？此操作不可逆。`,
          '确认删除',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
          },
        )
        ElMessage.success(`模型 "${model.name}" 删除成功`)
        loadData()
      } catch {
        // 用户取消删除
      }
      break
    default:
      break
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.model-management {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-section {
  flex: 1;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  height: 100%;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.models {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.deployed {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.training {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.performance {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.models-grid {
  margin-bottom: 24px;
}

.model-card {
  height: 100%;
  transition: transform 0.2s;
}

.model-card:hover {
  transform: translateY(-2px);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.model-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.model-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.model-content {
  padding: 0;
}

.model-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.info-item .label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.info-item .value {
  color: var(--el-text-color-primary);
  font-size: 14px;
  font-weight: 500;
}

.performance-chart {
  height: 80px;
  background: var(--el-fill-color-lighter);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.chart-placeholder .el-icon {
  font-size: 24px;
}

.model-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

.model-actions .el-button {
  flex: 1;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .model-actions {
    flex-direction: column;
  }

  .model-actions .el-button {
    width: 100%;
  }
}
</style>
