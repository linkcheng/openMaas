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
  <div class="data-management">
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <h1 class="page-title">数据管理</h1>
          <p class="page-description">管理训练数据集和知识库数据</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Plus" @click="showUploadDialog">
            上传数据集
          </el-button>
          <el-button :icon="Upload" @click="importData">
            导入数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="24">
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon datasets">
                <el-icon><FolderOpened /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalDatasets }}</div>
                <div class="stat-label">数据集总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon storage">
                <el-icon><Coin /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalStorage }}</div>
                <div class="stat-label">存储空间</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon records">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.totalRecords }}</div>
                <div class="stat-label">数据记录数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon active">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.activeDatasets }}</div>
                <div class="stat-label">活跃数据集</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <h3>数据集列表</h3>
          <div class="header-controls">
            <el-input
              v-model="searchQuery"
              placeholder="搜索数据集..."
              :prefix-icon="Search"
              clearable
              style="width: 240px; margin-right: 12px;"
            />
            <el-select v-model="filterType" placeholder="数据类型" style="width: 120px;">
              <el-option label="全部" value="" />
              <el-option label="文本" value="text" />
              <el-option label="图像" value="image" />
              <el-option label="音频" value="audio" />
              <el-option label="视频" value="video" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        :data="filteredDatasets"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="name" label="数据集名称" min-width="180">
          <template #default="{ row }">
            <div class="dataset-name">
              <el-icon class="dataset-icon"><FolderOpened /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="数据类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="100" />
        <el-table-column prop="records" label="记录数" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="160" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDataset(row)">查看</el-button>
            <el-button size="small" type="primary" @click="editDataset(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDataset(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="totalItems"
          layout="total, sizes, prev, pager, next, jumper"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Upload,
  Search,
  FolderOpened,
  Coin,
  Document,
  CircleCheck
} from '@element-plus/icons-vue'

interface Dataset {
  id: string
  name: string
  type: string
  size: string
  records: number
  created_at: string
  status: 'active' | 'processing' | 'error' | 'archived'
}

// 响应式数据
const loading = ref(false)
const searchQuery = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 统计数据
const stats = reactive({
  totalDatasets: 0,
  totalStorage: '0 GB',
  totalRecords: 0,
  activeDatasets: 0
})

// 数据集列表
const datasets = ref<Dataset[]>([])
const totalItems = ref(0)

// 计算属性
const filteredDatasets = computed(() => {
  let filtered = datasets.value

  if (searchQuery.value) {
    filtered = filtered.filter(dataset =>
      dataset.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (filterType.value) {
    filtered = filtered.filter(dataset => dataset.type === filterType.value)
  }

  return filtered
})

// 方法
const getTypeTagType = (type: string) => {
  const typeMap: Record<string, string> = {
    text: '',
    image: 'success',
    audio: 'warning',
    video: 'info'
  }
  return typeMap[type] || ''
}

const getStatusTagType = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'success',
    processing: 'warning',
    error: 'danger',
    archived: 'info'
  }
  return statusMap[status] || ''
}

const getStatusText = (status: string) => {
  const statusText: Record<string, string> = {
    active: '活跃',
    processing: '处理中',
    error: '错误',
    archived: '已归档'
  }
  return statusText[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    // 模拟数据加载
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 模拟数据
    datasets.value = [
      {
        id: '1',
        name: '对话训练数据集v1',
        type: 'text',
        size: '2.3 GB',
        records: 15420,
        created_at: '2024-01-15',
        status: 'active'
      },
      {
        id: '2',
        name: '图像分类数据集',
        type: 'image',
        size: '8.7 GB',
        records: 50000,
        created_at: '2024-01-10',
        status: 'active'
      },
      {
        id: '3',
        name: '语音识别数据',
        type: 'audio',
        size: '1.2 GB',
        records: 3500,
        created_at: '2024-01-08',
        status: 'processing'
      }
    ]

    stats.totalDatasets = datasets.value.length
    stats.totalStorage = '12.2 GB'
    stats.totalRecords = datasets.value.reduce((sum, item) => sum + item.records, 0)
    stats.activeDatasets = datasets.value.filter(item => item.status === 'active').length
    totalItems.value = datasets.value.length

  } catch {
    ElMessage.error('数据加载失败')
  } finally {
    loading.value = false
  }
}

const showUploadDialog = () => {
  ElMessage.info('上传功能开发中')
}

const importData = () => {
  ElMessage.info('导入功能开发中')
}

const viewDataset = (dataset: Dataset) => {
  ElMessage.info(`查看数据集: ${dataset.name}`)
}

const editDataset = (dataset: Dataset) => {
  ElMessage.info(`编辑数据集: ${dataset.name}`)
}

const deleteDataset = async (dataset: Dataset) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据集 "${dataset.name}" 吗？此操作不可逆。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    ElMessage.success(`数据集 "${dataset.name}" 删除成功`)
    loadData()
  } catch {
    // 用户取消删除
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.data-management {
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

.stat-icon.datasets {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.storage {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.records {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.active {
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

.table-card {
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.header-controls {
  display: flex;
  align-items: center;
}

.dataset-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dataset-icon {
  color: var(--el-color-primary);
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

  .card-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-controls {
    flex-direction: column;
    gap: 12px;
  }

  .header-controls .el-input,
  .header-controls .el-select {
    width: 100% !important;
  }
}
</style>