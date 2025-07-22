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
 * SM2加密工具类单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { SM2CryptoUtil } from '@/utils/crypto'

// Mock apiClient
vi.mock('@/utils/api', () => ({
  apiClient: {
    auth: {
      getPublicKey: vi.fn(),
    },
  },
  handleApiError: vi.fn((error) => error.message || '请求失败，请稍后重试'),
}))

// Mock sm-crypto
vi.mock('sm-crypto', () => ({
  sm2: {
    doEncrypt: vi.fn(),
  },
}))

import { sm2 } from 'sm-crypto'
import { apiClient } from '@/utils/api'

describe('SM2CryptoUtil', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('encrypt', () => {
    it('应该成功加密数据', () => {
      const mockData = 'test_password'
      const mockPublicKey = 'test_public_key'
      const mockEncrypted = 'abcdef123456'

      vi.mocked(sm2.doEncrypt).mockReturnValue(mockEncrypted)

      const result = SM2CryptoUtil.encrypt(mockData, mockPublicKey)

      expect(sm2.doEncrypt).toHaveBeenCalledWith(mockData, mockPublicKey, 1)
      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
    })

    it('应该在加密失败时抛出错误', () => {
      const mockData = 'test_password'
      const mockPublicKey = 'test_public_key'

      vi.mocked(sm2.doEncrypt).mockImplementation(() => {
        throw new Error('Encryption failed')
      })

      expect(() => {
        SM2CryptoUtil.encrypt(mockData, mockPublicKey)
      }).toThrow('密码加密失败')
    })
  })

  describe('getPublicKey', () => {
    it('应该成功获取公钥', async () => {
      const mockKeyInfo = {
        public_key: 'test_public_key_hex',
        algorithm: 'SM2',
        key_length: '256',
      }

      const mockResponse = {
        data: {
          success: true,
          data: mockKeyInfo,
          message: '获取公钥成功',
        },
      }

      vi.mocked(apiClient.auth.getPublicKey).mockResolvedValue(mockResponse)

      const result = await SM2CryptoUtil.getPublicKey()

      expect(apiClient.auth.getPublicKey).toHaveBeenCalledOnce()
      expect(result).toEqual(mockKeyInfo)
    })

    it('应该在API返回错误时抛出错误', async () => {
      const mockResponse = {
        data: {
          success: false,
          error: 'Server error',
        },
      }

      vi.mocked(apiClient.auth.getPublicKey).mockResolvedValue(mockResponse)

      await expect(SM2CryptoUtil.getPublicKey()).rejects.toThrow('Server error')
    })

    it('应该在网络错误时抛出错误', async () => {
      const networkError = new Error('Network error')
      vi.mocked(apiClient.auth.getPublicKey).mockRejectedValue(networkError)

      await expect(SM2CryptoUtil.getPublicKey()).rejects.toThrow()
    })
  })

  describe('encryptPassword', () => {
    it('应该成功加密密码', async () => {
      const mockPassword = 'test_password_123'
      const mockKeyInfo = {
        public_key: 'test_public_key_hex',
        algorithm: 'SM2',
        key_length: '256',
      }
      const mockEncrypted = 'abcdef123456'

      // Mock getPublicKey
      const mockResponse = {
        data: {
          success: true,
          data: mockKeyInfo,
        },
      }
      vi.mocked(apiClient.auth.getPublicKey).mockResolvedValue(mockResponse)

      // Mock encrypt
      vi.mocked(sm2.doEncrypt).mockReturnValue(mockEncrypted)

      const result = await SM2CryptoUtil.encryptPassword(mockPassword)

      expect(result).toBeTruthy()
      expect(typeof result).toBe('string')
      expect(sm2.doEncrypt).toHaveBeenCalledWith(mockPassword, mockKeyInfo.public_key, 1)
    })

    it('应该在获取公钥失败时抛出错误', async () => {
      const mockPassword = 'test_password_123'

      const networkError = new Error('Network error')
      vi.mocked(apiClient.auth.getPublicKey).mockRejectedValue(networkError)

      await expect(SM2CryptoUtil.encryptPassword(mockPassword)).rejects.toThrow()
    })

    it('应该在加密失败时抛出错误', async () => {
      const mockPassword = 'test_password_123'
      const mockKeyInfo = {
        public_key: 'test_public_key_hex',
        algorithm: 'SM2',
        key_length: '256',
      }

      // Mock getPublicKey success
      const mockResponse = {
        data: {
          success: true,
          data: mockKeyInfo,
        },
      }
      vi.mocked(apiClient.auth.getPublicKey).mockResolvedValue(mockResponse)

      // Mock encrypt failure
      vi.mocked(sm2.doEncrypt).mockImplementation(() => {
        throw new Error('Encryption failed')
      })

      await expect(SM2CryptoUtil.encryptPassword(mockPassword)).rejects.toThrow()
    })
  })
})
