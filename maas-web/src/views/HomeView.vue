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

<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import {
  Platform,
  Odometer,
  InfoFilled,
  Monitor,
  SetUp,
  User,
  Tools,
  UserFilled,
  Setting,
  SwitchButton,
  ArrowDown,
} from '@element-plus/icons-vue'

const { isAuthenticated, currentUser, logout } = useAuth()
</script>

<template>
  <div class="home">
    <!-- 页面头部 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="32" color="#409EFF">
            <Platform />
          </el-icon>
          <span class="logo-text">MaaS 平台</span>
        </div>
        <div class="nav">
          <el-menu mode="horizontal" :default-active="'home'" router>
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/dashboard">控制台</el-menu-item>
            <el-menu-item index="/about">关于</el-menu-item>
          </el-menu>
        </div>
        <div class="user-actions">
          <!-- 未登录用户显示登录注册按钮 -->
          <template v-if="!isAuthenticated">
            <el-button type="primary" @click="$router.push('/auth/login')">登录</el-button>
            <el-button @click="$router.push('/auth/register')">注册</el-button>
          </template>

          <!-- 已登录用户显示用户菜单 -->
          <template v-else>
            <el-dropdown trigger="click" placement="bottom-end">
              <div class="user-info">
                <el-avatar :size="32" :src="currentUser?.profile?.avatar_url">
                  <el-icon><UserFilled /></el-icon>
                </el-avatar>
                <span class="username">{{ currentUser?.username || '用户' }}</span>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/dashboard')">
                    <el-icon><Odometer /></el-icon>
                    控制台
                  </el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/user/profile')">
                    <el-icon><User /></el-icon>
                    个人资料
                  </el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/user/settings')">
                    <el-icon><Setting /></el-icon>
                    设置
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="main-content">
      <!-- 欢迎横幅 -->
      <div class="hero-section">
        <el-row justify="center">
          <el-col :span="20">
            <div class="hero-content">
              <h1 class="hero-title">欢迎使用 MaaS 平台</h1>
              <p class="hero-subtitle">模型即服务平台，为您提供强大的 AI 模型服务和管理能力</p>
              <div class="hero-actions">
                <el-button type="primary" size="large" @click="$router.push('/dashboard')">
                  <el-icon><Odometer /></el-icon>
                  开始使用
                </el-button>
                <el-button size="large" @click="$router.push('/about')">
                  <el-icon><InfoFilled /></el-icon>
                  了解更多
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- 功能特性 -->
      <div class="features-section">
        <el-row justify="center">
          <el-col :span="20">
            <h2 class="section-title">平台特性</h2>
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon">
                    <el-icon :size="48" color="#409EFF">
                      <Platform />
                    </el-icon>
                  </div>
                  <h3>模型管理</h3>
                  <p>统一管理和部署各种 AI 模型，支持版本控制和自动化部署</p>
                </el-card>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon">
                    <el-icon :size="48" color="#67C23A">
                      <Monitor />
                    </el-icon>
                  </div>
                  <h3>实时监控</h3>
                  <p>全方位监控模型性能、资源使用情况和服务状态</p>
                </el-card>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8">
                <el-card class="feature-card" shadow="hover">
                  <div class="feature-icon">
                    <el-icon :size="48" color="#E6A23C">
                      <SetUp />
                    </el-icon>
                  </div>
                  <h3>易于集成</h3>
                  <p>提供 RESTful API 和 SDK，轻松集成到您的应用程序中</p>
                </el-card>
              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </div>

      <!-- 快速开始 -->
      <div class="quickstart-section">
        <el-row justify="center">
          <el-col :span="20">
            <h2 class="section-title">快速开始</h2>
            <el-row :gutter="24">
              <el-col :xs="24" :md="12">
                <el-card class="quickstart-card">
                  <h3>
                    <el-icon><User /></el-icon>
                    用户入门
                  </h3>
                  <p>了解如何使用 MaaS 平台的各项功能</p>
                  <el-button type="primary" link @click="$router.push('/user/profile')">
                    用户指南 →
                  </el-button>
                </el-card>
              </el-col>
              <el-col :xs="24" :md="12">
                <el-card class="quickstart-card">
                  <h3>
                    <el-icon><Tools /></el-icon>
                    管理控制台
                  </h3>
                  <p>管理用户、模型和系统配置</p>
                  <el-button type="primary" link @click="$router.push('/admin/dashboard')">
                    管理后台 →
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </div>
    </el-main>

    <!-- 页面底部 -->
    <el-footer class="footer">
      <div class="footer-content">
        <p>&copy; 2025 MaaS 平台. 保留所有权利.</p>
      </div>
    </el-footer>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-background);
}

.header {
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  padding: 0;
  height: var(--header-height);
  position: sticky;
  top: 0;
  z-index: 100;

  /* Mobile optimization */
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: var(--container-max-width);
  margin: 0 auto;
  padding: 0 var(--space-md);
  height: 100%;
  gap: var(--space-md);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
}

.nav {
  flex: 1;
  display: flex;
  justify-content: center;

  /* Hide on mobile, show on larger screens */
  display: none;
}

.user-actions {
  display: flex;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color 0.2s;
  user-select: none;
}

.user-info:hover {
  background-color: var(--el-color-primary-light-9);
}

.username {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  transition: transform 0.2s;
}

.user-info:hover .dropdown-icon {
  color: var(--color-text-primary);
}

.main-content {
  flex: 1;
  padding: 0;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--space-2xl) var(--space-md);
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
  pointer-events: none;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.hero-title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  margin-bottom: var(--space-md);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  line-height: 1.1;
}

.hero-subtitle {
  font-size: clamp(1rem, 2.5vw, 1.25rem);
  margin-bottom: var(--space-xl);
  opacity: 0.9;
  line-height: 1.5;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
  flex-wrap: wrap;
}

.features-section,
.quickstart-section {
  padding: var(--space-2xl) var(--space-md);
}

.features-section {
  background: var(--color-background-soft);
}

.section-title {
  text-align: center;
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  font-weight: 600;
  margin-bottom: var(--space-2xl);
  color: var(--color-text-primary);
  line-height: 1.2;
}

.feature-card,
.quickstart-card {
  text-align: center;
  padding: var(--space-xl) var(--space-md);
  height: 100%;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.feature-card:hover,
.quickstart-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.feature-icon {
  margin-bottom: var(--space-md);
  display: flex;
  justify-content: center;
}

.feature-card h3,
.quickstart-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: var(--space-sm);
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  line-height: 1.3;
}

.feature-card p,
.quickstart-card p {
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: var(--space-md);
  font-size: 0.875rem;
}

.footer {
  background: var(--color-text-primary);
  color: var(--color-background);
  text-align: center;
  padding: var(--space-xl) var(--space-md);
  margin-top: auto;
}

.footer-content {
  max-width: var(--container-max-width);
  margin: 0 auto;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .header-content {
    padding: 0 var(--space-sm);
    flex-wrap: wrap;
    min-height: var(--header-height);
    height: auto;
  }

  .logo {
    order: 1;
  }

  .user-actions {
    order: 2;
    gap: var(--space-xs);
  }

  .nav {
    order: 3;
    width: 100%;
    justify-content: center;
    margin-top: var(--space-sm);
    padding-bottom: var(--space-sm);
    border-top: 1px solid var(--color-border);
    display: flex;
  }

  .hero-section {
    padding: var(--space-xl) var(--space-sm);
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
    gap: var(--space-sm);
  }

  .hero-actions .el-button {
    width: 100%;
    max-width: 280px;
    min-height: 48px;
  }

  .features-section,
  .quickstart-section {
    padding: var(--space-xl) var(--space-sm);
  }

  .feature-card,
  .quickstart-card {
    padding: var(--space-lg) var(--space-md);
  }

  .footer {
    padding: var(--space-lg) var(--space-sm);
  }
}

/* Tablet optimizations */
@media (min-width: 641px) and (max-width: 768px) {
  .nav {
    display: flex;
  }

  .header-content {
    gap: var(--space-lg);
  }

  .hero-section {
    padding: var(--space-2xl) var(--space-lg);
  }

  .features-section,
  .quickstart-section {
    padding: var(--space-2xl) var(--space-lg);
  }
}

/* Desktop optimizations */
@media (min-width: 769px) {
  .nav {
    display: flex;
  }

  .header-content {
    gap: var(--space-xl);
  }

  .hero-section {
    padding: 5rem var(--space-lg);
  }

  .features-section,
  .quickstart-section {
    padding: 5rem var(--space-lg);
  }

  .feature-card,
  .quickstart-card {
    padding: var(--space-2xl) var(--space-lg);
  }
}

/* Large screens */
@media (min-width: 1024px) {
  .hero-section {
    padding: 6rem var(--space-xl);
  }

  .features-section,
  .quickstart-section {
    padding: 6rem var(--space-xl);
  }
}

/* Grid layout for feature cards */
.features-section :deep(.el-row) {
  max-width: var(--container-max-width);
  margin: 0 auto;
}

.quickstart-section :deep(.el-row) {
  max-width: var(--container-max-width);
  margin: 0 auto;
}

/* Touch optimizations */
@media (pointer: coarse) {
  .user-actions .el-button {
    min-height: 44px;
    padding: var(--space-sm) var(--space-md);
  }

  .hero-actions .el-button {
    min-height: 48px;
    padding: var(--space-md) var(--space-lg);
  }

  .feature-card,
  .quickstart-card {
    touch-action: manipulation;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  .hero-section {
    background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
  }

  .feature-card,
  .quickstart-card {
    border-width: 2px;
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .feature-card,
  .quickstart-card {
    transition: none;
  }

  .feature-card:hover,
  .quickstart-card:hover {
    transform: none;
  }
}

/* Print styles */
@media print {
  .header,
  .footer,
  .hero-actions,
  .user-actions {
    display: none;
  }

  .hero-section {
    background: white;
    color: black;
  }

  .feature-card,
  .quickstart-card {
    break-inside: avoid;
    box-shadow: none;
    border: 1px solid #ccc;
  }
}

/* Focus management */
.feature-card:focus,
.quickstart-card:focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

/* Loading states */
.hero-actions .el-button.is-loading,
.user-actions .el-button.is-loading {
  pointer-events: none;
}

/* Dark mode enhancements */
@media (prefers-color-scheme: dark) {
  .hero-section {
    background: linear-gradient(135deg, #1e3a8a 0%, #7c2d12 100%);
  }

  .feature-card,
  .quickstart-card {
    background: var(--color-background-soft);
    border-color: var(--color-border);
  }
}
</style>
