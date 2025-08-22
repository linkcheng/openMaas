/**
 * 日期时间工具函数
 */

/**
 * 格式化日期时间
 * @param dateString - ISO 日期字符串
 * @param format - 格式类型
 * @returns 格式化后的日期字符串
 */
export function formatDateTime(
  dateString: string,
  format: 'full' | 'date' | 'time' | 'relative' = 'full'
): string {
  if (!dateString) return ''

  const date = new Date(dateString)
  
  if (isNaN(date.getTime())) {
    return dateString
  }

  const now = new Date()
  const diff = now.getTime() - date.getTime()

  switch (format) {
    case 'date':
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      })

    case 'time':
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })

    case 'relative':
      return formatRelativeTime(diff)

    case 'full':
    default:
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
  }
}

/**
 * 格式化相对时间
 * @param diff - 时间差（毫秒）
 * @returns 相对时间字符串
 */
function formatRelativeTime(diff: number): string {
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  const months = Math.floor(days / 30)
  const years = Math.floor(days / 365)

  if (years > 0) {
    return `${years}年前`
  } else if (months > 0) {
    return `${months}个月前`
  } else if (days > 0) {
    return `${days}天前`
  } else if (hours > 0) {
    return `${hours}小时前`
  } else if (minutes > 0) {
    return `${minutes}分钟前`
  } else if (seconds > 0) {
    return `${seconds}秒前`
  } else {
    return '刚刚'
  }
}

/**
 * 格式化日期范围
 * @param startDate - 开始日期
 * @param endDate - 结束日期
 * @returns 格式化的日期范围字符串
 */
export function formatDateRange(startDate: string, endDate: string): string {
  const start = formatDateTime(startDate, 'date')
  const end = formatDateTime(endDate, 'date')
  
  if (start === end) {
    return start
  }
  
  return `${start} - ${end}`
}

/**
 * 检查日期是否为今天
 * @param dateString - 日期字符串
 * @returns 是否为今天
 */
export function isToday(dateString: string): boolean {
  if (!dateString) return false
  
  const date = new Date(dateString)
  const today = new Date()
  
  return (
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate()
  )
}

/**
 * 检查日期是否为本周
 * @param dateString - 日期字符串
 * @returns 是否为本周
 */
export function isThisWeek(dateString: string): boolean {
  if (!dateString) return false
  
  const date = new Date(dateString)
  const today = new Date()
  
  // 获取本周的开始日期（周一）
  const startOfWeek = new Date(today)
  const day = today.getDay()
  const diff = today.getDate() - day + (day === 0 ? -6 : 1)
  startOfWeek.setDate(diff)
  startOfWeek.setHours(0, 0, 0, 0)
  
  // 获取本周的结束日期（周日）
  const endOfWeek = new Date(startOfWeek)
  endOfWeek.setDate(startOfWeek.getDate() + 6)
  endOfWeek.setHours(23, 59, 59, 999)
  
  return date >= startOfWeek && date <= endOfWeek
}

/**
 * 获取友好的时间描述
 * @param dateString - 日期字符串
 * @returns 友好的时间描述
 */
export function getFriendlyTime(dateString: string): string {
  if (!dateString) return ''
  
  if (isToday(dateString)) {
    return `今天 ${formatDateTime(dateString, 'time')}`
  }
  
  if (isThisWeek(dateString)) {
    const date = new Date(dateString)
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return `${weekdays[date.getDay()]} ${formatDateTime(dateString, 'time')}`
  }
  
  return formatDateTime(dateString, 'relative')
}