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
  <div class="audit-logs-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">系统日志管理</h2>
      <el-text type="info">查看和分析系统操作审计日志</el-text>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stats.total_logs }}</div>
              <div class="stat-label">总日志数</div>
            </div>
            <el-icon class="stat-icon" color="var(--el-color-primary)">
              <Document />
            </el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stats.today_logs }}</div>
              <div class="stat-label">今日日志</div>
            </div>
            <el-icon class="stat-icon" color="var(--el-color-success)">
              <Calendar />
            </el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stats.active_users }}</div>
              <div class="stat-label">活跃用户</div>
            </div>
            <el-icon class="stat-icon" color="var(--el-color-warning)">
              <User />
            </el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ stats.failed_operations }}</div>
              <div class="stat-label">失败操作</div>
            </div>
            <el-icon class="stat-icon" color="var(--el-color-danger)">
              <Warning />
            </el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="filter-card">
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item label="操作类型">
          <el-select
            v-model="searchForm.action"
            placeholder="请选择操作类型"
            clearable
            style="width: 180px"
          >
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
            <el-option label="创建用户" value="user_create" />
            <el-option label="更新用户" value="user_update" />
            <el-option label="删除用户" value="user_delete" />
            <el-option label="密码重置" value="password_reset" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作结果">
          <el-select
            v-model="searchForm.result"
            placeholder="请选择操作结果"
            clearable
            style="width: 120px"
          >
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failure" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 300px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="table-header">
          <span>审计日志列表</span>
          <el-button type="primary" size="small" @click="handleExport" :loading="exportLoading">
            <el-icon><Download /></el-icon>
            导出日志
          </el-button>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="logs"
        style="width: 100%"
        height="500"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="username" label="用户名" width="120">
          <template #default="{ row }">
            <span v-if="row.username">{{ row.username }}</span>
            <el-tag v-else type="info" size="small">系统</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="操作类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)" size="small">
              {{ formatAction(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="操作描述" min-width="200" />
        <el-table-column prop="resource_type" label="资源类型" width="100">
          <template #default="{ row }">
            <span v-if="row.resource_type">{{ row.resource_type }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="80">
          <template #default="{ row }">
            <el-tag :type="row.result === 'success' ? 'success' : 'danger'" size="small">
              {{ row.result === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="120" />
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="日志详情"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-descriptions v-if="selectedLog" :column="2" border class="log-detail">
        <el-descriptions-item label="用户名">
          <span v-if="selectedLog.username">{{ selectedLog.username }}</span>
          <el-tag v-else type="info" size="small">系统操作</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户ID">
          {{ selectedLog.user_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionTagType(selectedLog.action)" size="small">
            {{ formatAction(selectedLog.action) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作结果">
          <el-tag :type="selectedLog.result === 'success' ? 'success' : 'danger'" size="small">
            {{ selectedLog.result === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="资源类型">
          {{ selectedLog.resource_type || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="资源ID">
          {{ selectedLog.resource_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="IP地址">
          {{ selectedLog.ip_address || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="请求ID">
          {{ selectedLog.request_id || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="操作时间" :span="2">
          {{ formatDateTime(selectedLog.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="操作描述" :span="2">
          {{ selectedLog.description }}
        </el-descriptions-item>
        <el-descriptions-item label="用户代理" :span="2">
          <el-text size="small" class="user-agent-text">
            {{ selectedLog.user_agent || '-' }}
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item v-if="selectedLog.error_message" label="错误信息" :span="2">
          <el-text type="danger" size="small">
            {{ selectedLog.error_message }}
          </el-text>
        </el-descriptions-item>
        <el-descriptions-item
          v-if="selectedLog.metadata && Object.keys(selectedLog.metadata).length > 0"
          label="扩展信息"
          :span="2"
        >
          <pre class="metadata-text">{{ JSON.stringify(selectedLog.metadata, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Document,
  Calendar,
  User,
  Warning,
  Search,
  Refresh,
  Download,
} from '@element-plus/icons-vue'
import { getAuditLogs, getAuditStats, exportAuditLogs } from '@/utils/api'
import type { AuditLogResponse, AuditStatsResponse } from '@/utils/api'

// 响应式数据
const loading = ref(false)
const exportLoading = ref(false)
const logs = ref<AuditLogResponse[]>([])
const selectedRows = ref<AuditLogResponse[]>([])
const detailDialogVisible = ref(false)
const selectedLog = ref<AuditLogResponse | null>(null)

// 统计数据
const stats = reactive<AuditStatsResponse>({
  total_logs: 0,
  today_logs: 0,
  active_users: 0,
  failed_operations: 0,
})

// 搜索表单
const searchForm = reactive({
  username: '',
  action: '',
  result: '',
  dateRange: null as [string, string] | null,
})

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
})

// 生命周期
onMounted(() => {
  loadStats()
  loadLogs()
})

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await getAuditStats()
    if (response.data.success) {
      Object.assign(stats, response.data.data)
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载日志列表
const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      username: searchForm.username || undefined,
      action: searchForm.action || undefined,
      result: searchForm.result || undefined,
      start_time: searchForm.dateRange?.[0] || undefined,
      end_time: searchForm.dateRange?.[1] || undefined,
    }
    const response = await getAuditLogs(params)
    if (response.data.success && response.data.data) {
      logs.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data.error || '加载日志失败')
    }
  } catch (error) {
    console.error('加载日志失败:', error)
    ElMessage.error('网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadLogs()
}

// 重置搜索
const handleReset = () => {
  Object.assign(searchForm, {
    username: '',
    action: '',
    result: '',
    dateRange: null as [string, string] | null,
  })
  pagination.page = 1
  loadLogs()
}

// 分页处理
const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.page = 1
  loadLogs()
}

const handleCurrentChange = (page: number) => {
  pagination.page = page
  loadLogs()
}

// 选择变化
const handleSelectionChange = (selection: AuditLogResponse[]) => {
  selectedRows.value = selection
}

// 查看详情
const handleViewDetail = (row: AuditLogResponse) => {
  selectedLog.value = row
  detailDialogVisible.value = true
}

// 导出日志
const handleExport = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要导出的日志记录')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要导出选中的 ${selectedRows.value.length} 条日志记录吗？`,
      '确认导出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    exportLoading.value = true
    const logIds = selectedRows.value.map((row) => row.audit_log_id)
    const response = await exportAuditLogs({ log_ids: logIds })

    if (response.data.success) {
      // 创建下载链接
      const blob = new Blob([JSON.stringify(response.data.data, null, 2)], {
        type: 'application/json',
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `audit_logs_${new Date().toISOString().slice(0, 10)}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      ElMessage.success('日志导出成功')
    } else {
      ElMessage.error(response.data.error || '导出失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('导出日志失败:', error)
      ElMessage.error('网络错误，请稍后重试')
    }
  } finally {
    exportLoading.value = false
  }
}

// 格式化操作类型
const formatAction = (action: string) => {
  const actionMap: Record<string, string> = {
    login: '登录',
    logout: '登出',
    user_create: '创建用户',
    user_update: '更新用户',
    user_delete: '删除用户',
    password_reset: '密码重置',
    profile_update: '更新资料',
  }
  return actionMap[action] || action
}

// 获取操作类型标签颜色
const getActionTagType = (action: string) => {
  const typeMap: Record<string, string> = {
    login: 'success',
    logout: 'info',
    user_create: 'primary',
    user_update: 'warning',
    user_delete: 'danger',
    password_reset: 'warning',
  }
  return typeMap[action] || 'default'
}

// 格式化日期时间
const formatDateTime = (dateTime: string) => {
  return new Date(dateTime).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}
</script>

<style scoped>
.audit-logs-view {
  padding: 24px;
  min-height: 100vh;
  background: var(--el-bg-color-page);
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
  font-size: 24px;
  font-weight: 600;
}

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  position: relative;
  overflow: hidden;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-content {
  text-align: left;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.stat-icon {
  font-size: 40px;
  opacity: 0.3;
}

.filter-card {
  margin-bottom: 24px;
}

.search-form {
  align-items: flex-end;
}

.table-card {
  background: var(--el-bg-color);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.text-muted {
  color: var(--el-text-color-placeholder);
}

.log-detail {
  margin-bottom: 20px;
}

.user-agent-text {
  word-break: break-all;
  line-height: 1.4;
}

.metadata-text {
  background: var(--el-fill-color-light);
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.4;
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .audit-logs-view {
    padding: 16px;
  }

  .stats-cards .el-col {
    margin-bottom: 16px;
  }

  .search-form {
    flex-direction: column;
    align-items: stretch;
  }

  .search-form .el-form-item {
    margin-right: 0;
    margin-bottom: 16px;
  }
}
</style>
