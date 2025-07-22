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

/**
 * SM2加密工具类
 * 用于前端密码加密传输
 */

import { sm2 } from 'sm-crypto'
import { apiClient, handleApiError } from './api'

/**
 * 十六进制字符串转Base64（浏览器兼容）
 * @param hex 十六进制字符串
 * @returns Base64字符串
 */
function hexToBase64(hex: string): string {
  const bytes = []
  for (let i = 0; i < hex.length; i += 2) {
    bytes.push(parseInt(hex.substring(i, i + 2), 16))
  }
  return btoa(String.fromCharCode(...bytes))
}

export interface SM2PublicKey {
  public_key: string
  algorithm: string
  key_length: string
}

export class SM2CryptoUtil {
  /**
   * localStorage缓存key
   */
  private static readonly LOCAL_KEY = 'sm2_public_key_cache';
  private static readonly CACHE_EXPIRE_MS = 24 * 60 * 60 * 1000; // 24小时

  /**
   * 使用SM2公钥加密数据
   * @param data 要加密的明文数据
   * @param publicKey SM2公钥（十六进制字符串）
   * @returns Base64编码的密文
   */
  static encrypt(data: string, publicKey: string): string {
    try {
      // 确保公钥格式正确（以04开头的完整公钥）
      let formattedPublicKey = decodeURIComponent(publicKey)
      if (!publicKey.startsWith('04')) {
        formattedPublicKey = '04' + publicKey
      }
      
      // 使用sm-crypto库进行SM2加密
      // 模式1表示C1C3C2格式
      const encrypted = sm2.doEncrypt(data, formattedPublicKey, 1)
      return encrypted
      // 将十六进制转换为Base64（浏览器兼容方式）
      return hexToBase64(encrypted)
    } catch (error) {
      console.error('SM2加密失败:', error)
      throw new Error('密码加密失败')
    }
  }

  /**
   * 获取服务器公钥（带localStorage缓存，24小时有效）
   * @returns Promise<SM2PublicKey> 公钥信息
   */
  static async getPublicKey(): Promise<SM2PublicKey> {

    // 1. 先查localStorage缓存
    const cacheStr = localStorage.getItem(this.LOCAL_KEY)
    if (cacheStr) {
      try {
        const cacheObj = JSON.parse(cacheStr)
        if (cacheObj && cacheObj.data && cacheObj.ts) {
          const now = Date.now()
          if (now - cacheObj.ts < this.CACHE_EXPIRE_MS) {
            return cacheObj.data as SM2PublicKey
          } else {
            // 过期，清理
            localStorage.removeItem(this.LOCAL_KEY)
          }
        }
      } catch {
        // 解析失败，清理
        localStorage.removeItem(this.LOCAL_KEY)
      }
    }
    // 2. 无缓存或过期，请求接口
    try {
      const response = await apiClient.auth.getPublicKey()
      if (response.data.success && response.data.data) {
        const keyInfo = response.data.data as SM2PublicKey
        // 写入localStorage
        localStorage.setItem(this.LOCAL_KEY, JSON.stringify({ data: keyInfo, ts: Date.now() }))
        return keyInfo
      } else {
        throw new Error(response.data.error || '获取公钥失败')
      }
    } catch (error) {
      console.error('获取公钥失败:', error)
      throw new Error(handleApiError(error))
    }
  }

  /**
   * 加密密码用于传输
   * @param password 明文密码
   * @returns Promise<string> 加密后的密码
   */
  static async encryptPassword(password: string): Promise<string> {
    try {
      // 获取公钥
      const keyInfo = await this.getPublicKey()
      // 加密密码
      return this.encrypt(password, keyInfo.public_key)
    } catch (error) {
      console.error('密码加密失败:', error)
      throw error
    }
  }
}
