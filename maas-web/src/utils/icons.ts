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

// 按需导入常用的 Element Plus 图标
export {
  Edit,
  Delete,
  Plus,
  Search,
  Refresh,
  Setting,
  User,
  UserFilled,
  Lock,
  Unlock,
  View,
  Hide,
  Close,
  Check,
  Warning,
  InfoFilled,
  SuccessFilled,
  CircleClose,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  Upload,
  Download,
  More,
  MoreFilled,
  Filter,
  Sort,
  Document,
  DocumentCopy,
  Folder,
  FolderOpened,
  House,
  Location,
  Position,
  Star,
  StarFilled,
  Message,
  Bell,
  Notification
} from '@element-plus/icons-vue'

// 图标映射，便于在模板中使用
export const IconMap = {
  edit: 'Edit',
  delete: 'Delete',
  plus: 'Plus',
  search: 'Search',
  refresh: 'Refresh',
  setting: 'Setting',
  user: 'User',
  'user-filled': 'UserFilled',
  lock: 'Lock',
  unlock: 'Unlock',
  view: 'View',
  hide: 'Hide',
  close: 'Close',
  check: 'Check',
  warning: 'Warning',
  'info-filled': 'InfoFilled',
  'success-filled': 'SuccessFilled',
  'circle-close': 'CircleClose',
  'arrow-left': 'ArrowLeft',
  'arrow-right': 'ArrowRight',
  'arrow-up': 'ArrowUp',
  'arrow-down': 'ArrowDown',
  upload: 'Upload',
  download: 'Download',
  more: 'More',
  'more-filled': 'MoreFilled',
  filter: 'Filter',
  sort: 'Sort',
  document: 'Document',
  'document-copy': 'DocumentCopy',
  folder: 'Folder',
  'folder-opened': 'FolderOpened',
  house: 'House',
  location: 'Location',
  position: 'Position',
  star: 'Star',
  'star-filled': 'StarFilled',
  message: 'Message',
  bell: 'Bell',
  notification: 'Notification',
} as const

export type IconName = keyof typeof IconMap