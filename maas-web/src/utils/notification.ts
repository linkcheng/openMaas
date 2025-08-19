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

import { ElMessage, ElNotification } from 'element-plus'
import { AxiosError } from 'axios'

// 错误类型枚举
export enum ErrorType {
  NETWORK = 'network',
  AUTH = 'auth',
  SERVER = 'server',
  TIMEOUT = 'timeout',
  UNKNOWN = 'unknown',
}

// 根据错误类型获取错误信息
const getErrorType = (error: AxiosError): ErrorType => {
  if (!error.response) {
    // 网络错误（无响应）
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return ErrorType.TIMEOUT
    }
    return ErrorType.NETWORK
  }

  const status = error.response.status
  if (status === 401 || status === 403) {
    return ErrorType.AUTH
  }
  if (status >= 500) {
    return ErrorType.SERVER
  }

  return ErrorType.UNKNOWN
}

// Token刷新相关的通知
export const tokenNotification = {
  // 刷新失败通知
  refreshFailed: (error: AxiosError, attempt: number, maxAttempts: number) => {
    const errorType = getErrorType(error)
    let title = 'Token刷新失败'
    let message = ''

    switch (errorType) {
      case ErrorType.NETWORK:
        title = '网络连接问题'
        message = '无法连接到服务器，请检查网络连接后重试'
        break
      case ErrorType.TIMEOUT:
        title = '请求超时'
        message = '服务器响应超时，请稍后重试'
        break
      case ErrorType.SERVER:
        title = '服务器错误'
        message = '服务器暂时不可用，请稍后重试'
        break
      case ErrorType.AUTH:
        title = '认证已失效'
        message = '登录已过期，即将跳转到登录页面'
        break
      default:
        message = '身份验证失败，即将跳转到登录页面'
    }

    if (attempt < maxAttempts && errorType !== ErrorType.AUTH) {
      // 还有重试机会且不是认证错误
      ElMessage.warning({
        message: `${message}（第${attempt}次重试，共${maxAttempts}次）`,
        duration: 3000,
        showClose: true,
      })
    } else {
      // 最终失败或认证错误
      ElNotification.error({
        title,
        message,
        duration: 5000,
        position: 'top-right',
      })
    }
  },

  // 所有重试失败后的最终通知
  allRetriesFailed: (error: AxiosError) => {
    const errorType = getErrorType(error)

    if (errorType === ErrorType.NETWORK || errorType === ErrorType.TIMEOUT) {
      ElNotification.error({
        title: '连接失败',
        message: '网络连接问题，登录状态可能受到影响。请检查网络后刷新页面重试。',
        duration: 8000,
        position: 'top-right',
      })
    } else {
      ElNotification.error({
        title: '登录已失效',
        message: '您的登录已过期，系统将在3秒后跳转到登录页面。',
        duration: 3000,
        position: 'top-right',
      })
    }
  },

  // 预防性刷新成功
  preventiveRefreshSuccess: () => {
    // 预防性刷新成功通常不需要显示通知，只在调试时显示
    if (import.meta.env.DEV) {
      console.log('Token已自动续期')
    }
  },

  // 预防性刷新失败
  preventiveRefreshFailed: (error: AxiosError) => {
    // 预防性刷新失败通常不显示错误提示，让正常的401处理机制处理
    console.warn('预防性token刷新失败，将由正常流程处理:', error.message)
  },
}

// 通用的API错误处理
export const handleApiNotification = (error: AxiosError, context?: string) => {
  const errorType = getErrorType(error)
  const contextMessage = context ? `${context}: ` : ''

  switch (errorType) {
    case ErrorType.NETWORK:
      ElMessage.error(`${contextMessage}网络连接失败，请检查网络设置`)
      break
    case ErrorType.TIMEOUT:
      ElMessage.error(`${contextMessage}请求超时，请稍后重试`)
      break
    case ErrorType.SERVER:
      ElMessage.error(`${contextMessage}服务器错误，请稍后重试`)
      break
    case ErrorType.AUTH:
      // 认证错误通常由拦截器处理，这里不显示通知
      break
    default:
      ElMessage.error(`${contextMessage}操作失败，请重试`)
  }
}
