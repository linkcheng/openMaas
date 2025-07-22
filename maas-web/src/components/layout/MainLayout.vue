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
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <SidebarComponent />

    <!-- 主要内容区域 -->
    <el-container class="main-content">
      <!-- 头部 -->
      <HeaderComponent />

      <!-- 主体内容 -->
      <el-main class="content-area">
        <div class="content-wrapper">
          <!-- 路由视图 -->
          <router-view v-slot="{ Component, route }">
            <transition name="fade-slide" mode="out-in">
              <keep-alive :include="keepAliveComponents">
                <component :is="Component" :key="route.path" />
              </keep-alive>
            </transition>
          </router-view>
        </div>
      </el-main>

      <!-- 页脚（可选） -->
      <el-footer v-if="showFooter" class="app-footer" height="auto">
        <div class="footer-content">
          <el-text type="info" size="small">
            © 2024 AI MaaS 平台 | 
            <el-link type="primary" :underline="false" size="small">帮助文档</el-link> |
            <el-link type="primary" :underline="false" size="small">联系我们</el-link>
          </el-text>
        </div>
      </el-footer>
    </el-container>

    <!-- 移动端遮罩层 -->
    <div 
      v-if="isMobile && sidebarVisible" 
      class="mobile-overlay"
      @click="closeSidebar"
    />
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import HeaderComponent from './HeaderComponent.vue'
import SidebarComponent from './SidebarComponent.vue'

// 响应式状态
const windowWidth = ref(window.innerWidth)
const sidebarVisible = ref(false)
const showFooter = ref(false) // 可配置是否显示页脚

// 计算属性
const isMobile = computed(() => windowWidth.value < 768)

// 需要缓存的组件列表
const keepAliveComponents = ref([
  'DashboardView',
  'DataManagement',
  'ModelManagement',
  'KnowledgeBase'
])

// 窗口大小变化处理
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

// 关闭移动端侧边栏
const closeSidebar = () => {
  sidebarVisible.value = false
}

// 生命周期钩子
onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
  background: var(--el-bg-color-page);
}

.main-content {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.content-area {
  flex: 1;
  padding: 0;
  overflow-y: auto;
  overflow-x: hidden;
  background: var(--el-bg-color-page);
}

.content-wrapper {
  min-height: 100%;
  padding: 24px;
  background: var(--el-bg-color-page);
}

.app-footer {
  background: var(--el-bg-color-overlay);
  border-top: 1px solid var(--el-border-color);
  padding: 12px 24px;
}

.footer-content {
  text-align: center;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 999;
  backdrop-filter: blur(2px);
}

/* 页面过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}

/* 滚动条样式 */
.content-area::-webkit-scrollbar {
  width: 8px;
}

.content-area::-webkit-scrollbar-track {
  background: var(--el-bg-color-page);
}

.content-area::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 4px;
}

.content-area::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-darker);
}

/* 响应式样式 */
@media (max-width: 1200px) {
  .content-wrapper {
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .content-wrapper {
    padding: 16px;
  }
  
  .main-layout {
    position: relative;
  }
  
  /* 移动端时主内容占满宽度 */
  .main-content {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .content-wrapper {
    padding: 12px;
  }
  
  .app-footer {
    padding: 8px 12px;
  }
  
  .footer-content {
    font-size: 12px;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .main-layout {
    background: var(--el-bg-color-page);
  }
  
  .content-area {
    background: var(--el-bg-color-page);
  }
  
  .content-wrapper {
    background: var(--el-bg-color-page);
  }
  
  .mobile-overlay {
    background: rgba(0, 0, 0, 0.5);
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .content-area::-webkit-scrollbar-thumb {
    background: var(--el-text-color-primary);
  }
  
  .mobile-overlay {
    background: rgba(0, 0, 0, 0.8);
  }
}

/* 减少动画模式 */
@media (prefers-reduced-motion: reduce) {
  .fade-slide-enter-active,
  .fade-slide-leave-active {
    transition: none;
  }
}

/* 打印样式 */
@media print {
  .main-layout {
    background: white;
    color: black;
  }
  
  .app-footer {
    display: none;
  }
  
  .content-wrapper {
    padding: 0;
  }
}
</style>