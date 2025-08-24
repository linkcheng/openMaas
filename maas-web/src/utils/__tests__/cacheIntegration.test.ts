import { describe, it, expect, beforeEach } from 'vitest'
import { cacheApiResponse } from '../performance'
import { memoryCache } from '../cache'

describe('Cache Integration', () => {
  beforeEach(() => {
    memoryCache.clear()
  })

  it('should cache API responses', async () => {
    let callCount = 0
    const mockApiFn = async () => {
      callCount++
      return { data: 'test-data', timestamp: Date.now() }
    }

    // 第一次调用
    const result1 = await cacheApiResponse('test-api', mockApiFn, 1000)
    expect(result1.data).toBe('test-data')
    expect(callCount).toBe(1)

    // 第二次调用应该使用缓存
    const result2 = await cacheApiResponse('test-api', mockApiFn, 1000)
    expect(result2.data).toBe('test-data')
    expect(result2.timestamp).toBe(result1.timestamp) // 相同的时间戳说明是缓存数据
    expect(callCount).toBe(1) // API函数没有被再次调用
  })

  it('should cache different keys separately', async () => {
    let callCount = 0
    const mockApiFn = async (id: string) => {
      callCount++
      return { id, data: `data-${id}` }
    }

    // 为不同key缓存不同数据
    const result1 = await cacheApiResponse('api-1', () => mockApiFn('1'))
    const result2 = await cacheApiResponse('api-2', () => mockApiFn('2'))

    expect(result1.id).toBe('1')
    expect(result2.id).toBe('2')
    expect(callCount).toBe(2)

    // 再次获取应该使用缓存
    const cached1 = await cacheApiResponse('api-1', () => mockApiFn('1'))
    const cached2 = await cacheApiResponse('api-2', () => mockApiFn('2'))

    expect(cached1.id).toBe('1')
    expect(cached2.id).toBe('2')
    expect(callCount).toBe(2) // 没有增加
  })
})