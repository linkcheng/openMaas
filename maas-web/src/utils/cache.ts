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

interface CacheItem {
  data: any
  expireTime: number
}

/**
 * 简化的统一缓存工具
 */
export class SimpleCache {
  private cache = new Map<string, CacheItem>()

  /**
   * 设置缓存
   * @param key 缓存键
   * @param data 数据
   * @param ttlMs 过期时间（毫秒），默认5分钟
   */
  set(key: string, data: any, ttlMs = 5 * 60 * 1000): void {
    this.cache.set(key, {
      data,
      expireTime: Date.now() + ttlMs
    })
  }

  /**
   * 获取缓存
   * @param key 缓存键
   * @returns 缓存数据，过期或不存在返回null
   */
  get<T = any>(key: string): T | null {
    const item = this.cache.get(key)
    
    if (!item) return null
    
    if (Date.now() > item.expireTime) {
      this.cache.delete(key)
      return null
    }
    
    return item.data
  }

  /**
   * 删除缓存
   * @param key 缓存键
   */
  delete(key: string): void {
    this.cache.delete(key)
  }

  /**
   * 清除所有缓存
   */
  clear(): void {
    this.cache.clear()
  }

  /**
   * 检查缓存是否存在且未过期
   * @param key 缓存键
   */
  has(key: string): boolean {
    const item = this.cache.get(key)
    if (!item) return false
    
    if (Date.now() > item.expireTime) {
      this.cache.delete(key)
      return false
    }
    
    return true
  }
}

/**
 * LocalStorage缓存工具
 */
export class LocalStorageCache {
  /**
   * 设置缓存到localStorage
   * @param key 缓存键
   * @param data 数据
   * @param ttlMs 过期时间（毫秒），默认24小时
   */
  static set(key: string, data: any, ttlMs = 24 * 60 * 60 * 1000): void {
    try {
      const item = {
        data,
        expireTime: Date.now() + ttlMs
      }
      localStorage.setItem(key, JSON.stringify(item))
    } catch (error) {
      console.warn('LocalStorage缓存设置失败:', error)
    }
  }

  /**
   * 从localStorage获取缓存
   * @param key 缓存键
   * @returns 缓存数据，过期或不存在返回null
   */
  static get<T = any>(key: string): T | null {
    try {
      const itemStr = localStorage.getItem(key)
      if (!itemStr) return null

      const item = JSON.parse(itemStr)
      
      if (Date.now() > item.expireTime) {
        localStorage.removeItem(key)
        return null
      }
      
      return item.data
    } catch (error) {
      localStorage.removeItem(key)
      return null
    }
  }

  /**
   * 删除localStorage缓存
   * @param key 缓存键
   */
  static delete(key: string): void {
    localStorage.removeItem(key)
  }

  /**
   * 检查localStorage缓存是否存在且未过期
   * @param key 缓存键
   */
  static has(key: string): boolean {
    const item = this.get(key)
    return item !== null
  }
}

// 全局内存缓存实例
export const memoryCache = new SimpleCache()

// 常用缓存键
export const CACHE_KEYS = {
  SM2_PUBLIC_KEY: 'sm2_public_key',
  USER_THEME: 'maas-theme',
  API_RESPONSE: (url: string, params?: any) => 
    `api_${url}${params ? '_' + JSON.stringify(params) : ''}`,
} as const