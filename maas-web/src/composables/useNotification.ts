/*
 * Copyright 2025 MaaS Team
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'
import type { MessageOptions, NotificationOptions, ElMessageBoxOptions } from 'element-plus'

/**
 * 统一的通知和消息处理
 * 提供与系统其他部分一致的用户反馈机制
 */
export const useNotification = () => {
  // 成功消息
  const showSuccess = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.success({
      message,
      duration: 3000,
      showClose: true,
      ...options,
    })
  }

  // 错误消息
  const showError = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.error({
      message,
      duration: 5000,
      showClose: true,
      ...options,
    })
  }

  // 警告消息
  const showWarning = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.warning({
      message,
      duration: 4000,
      showClose: true,
      ...options,
    })
  }

  // 信息消息
  const showInfo = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.info({
      message,
      duration: 3000,
      showClose: true,
      ...options,
    })
  }

  // 成功通知（右上角）
  const notifySuccess = (
    title: string,
    message?: string,
    options?: Partial<NotificationOptions>,
  ) => {
    ElNotification.success({
      title,
      message,
      duration: 4000,
      ...options,
    })
  }

  // 错误通知（右上角）
  const notifyError = (title: string, message?: string, options?: Partial<NotificationOptions>) => {
    ElNotification.error({
      title,
      message,
      duration: 6000,
      ...options,
    })
  }

  // 警告通知（右上角）
  const notifyWarning = (
    title: string,
    message?: string,
    options?: Partial<NotificationOptions>,
  ) => {
    ElNotification.warning({
      title,
      message,
      duration: 5000,
      ...options,
    })
  }

  // 信息通知（右上角）
  const notifyInfo = (title: string, message?: string, options?: Partial<NotificationOptions>) => {
    ElNotification.info({
      title,
      message,
      duration: 4000,
      ...options,
    })
  }

  // 确认对话框
  const confirm = async (
    message: string,
    title: string = '确认操作',
    options?: Partial<ElMessageBoxOptions>,
  ): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(message, title, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        ...options,
      })
      return true
    } catch {
      return false
    }
  }

  // 删除确认对话框
  const confirmDelete = async (itemName: string, customMessage?: string): Promise<boolean> => {
    const message = customMessage || `确定要删除"${itemName}"吗？此操作不可撤销。`

    try {
      await ElMessageBox.confirm(message, '确认删除', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger',
      })
      return true
    } catch {
      return false
    }
  }

  // 批量删除确认
  const confirmBatchDelete = async (count: number): Promise<boolean> => {
    const message = `确定要删除选中的 ${count} 项吗？此操作不可撤销。`

    try {
      await ElMessageBox.confirm(message, '批量删除确认', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger',
      })
      return true
    } catch {
      return false
    }
  }

  // 输入对话框
  const prompt = async (
    message: string,
    title: string = '请输入',
    options?: Partial<ElMessageBoxOptions>,
  ): Promise<string | null> => {
    try {
      const { value } = await ElMessageBox.prompt(message, title, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        ...options,
      })
      return value
    } catch {
      return null
    }
  }

  // 处理API错误的统一方法
  const handleApiError = (error: any, defaultMessage: string = '操作失败') => {
    let message = defaultMessage

    if (error?.response?.data?.error) {
      message = error.response.data.error
    } else if (error?.message) {
      message = error.message
    } else if (typeof error === 'string') {
      message = error
    }

    showError(message)
  }

  // 处理操作成功的统一方法
  const handleSuccess = (message: string, useNotification: boolean = false) => {
    if (useNotification) {
      notifySuccess('操作成功', message)
    } else {
      showSuccess(message)
    }
  }

  return {
    // 消息方法
    showSuccess,
    showError,
    showWarning,
    showInfo,

    // 通知方法
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,

    // 对话框方法
    confirm,
    confirmDelete,
    confirmBatchDelete,
    prompt,

    // 统一处理方法
    handleApiError,
    handleSuccess,
  }
}
