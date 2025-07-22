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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { login, isLoading } = useAuth()

const loginForm = reactive({
  login_id: '',
  password: '',
  remember: false,
})

const rules = {
  login_id: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' },
    { min: 3, message: '用户名或邮箱至少3个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
  ],
}

const loginFormRef = ref()

const handleLogin = async () => {
  if (!loginFormRef.value) return

  try {
    await loginFormRef.value.validate()

    // 调用实际的登录 API
    const result = await login({
      login_id: loginForm.login_id,
      password: loginForm.password,
    })

    if (result.success) {
      ElMessage.success(result.message || '登录成功')
      router.push('/dashboard')
    } else {
      ElMessage.error(result.error || '登录失败')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请检查用户名和密码')
  }
}

const goToRegister = () => {
  router.push('/auth/register')
}

const goToForgotPassword = () => {
  router.push('/auth/forgot-password')
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="48" color="#409EFF">
          <Platform />
        </el-icon>
        <h1>MaaS 平台</h1>
        <p>登录您的账户</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        size="large"
        label-position="top"
      >
        <el-form-item label="用户名/邮箱" prop="login_id">
          <el-input
            v-model="loginForm.login_id"
            placeholder="请输入用户名或邮箱"
            prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <div class="form-footer">
            <el-checkbox v-model="loginForm.remember"> 记住我 </el-checkbox>
            <el-link type="primary" @click="goToForgotPassword"> 忘记密码？ </el-link>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" class="login-button" :loading="isLoading" @click="handleLogin">
            {{ isLoading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="register-link">
        <span>还没有账户？</span>
        <el-link type="primary" @click="goToRegister"> 立即注册 </el-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  min-height: -webkit-fill-available; /* iOS Safari fix */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-md);

  /* Mobile optimization */
  position: relative;
  overflow-x: hidden;
}

.login-card {
  background: var(--color-background);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--space-2xl);
  width: 100%;
  max-width: 400px;
  position: relative;

  /* Mobile-first approach */
  margin: var(--space-md) 0;

  /* Browser compatibility */
  -webkit-backdrop-filter: blur(10px);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);

  /* Animation */
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.login-header h1 {
  margin: var(--space-md) 0 var(--space-sm);
  color: var(--color-text-primary);
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.2;
}

.login-header p {
  color: var(--color-text-secondary);
  margin: 0;
  font-size: 1rem;
  line-height: 1.5;
}

.login-form {
  margin-bottom: var(--space-lg);
}

.form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: var(--radius-md);

  /* Touch optimization */
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.register-link {
  text-align: center;
  color: var(--color-text-secondary);
  margin-top: var(--space-md);
}

.register-link span {
  margin-right: var(--space-sm);
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .login-container {
    padding: var(--space-sm);
    /* Fix for mobile browsers */
    min-height: calc(100vh - env(keyboard-inset-height, 0px));
  }

  .login-card {
    padding: var(--space-xl) var(--space-lg);
    margin: var(--space-sm) 0;
    border-radius: var(--radius-lg);
  }

  .login-header h1 {
    font-size: 1.5rem;
  }

  .login-header p {
    font-size: 0.875rem;
  }

  .form-footer {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .login-button {
    height: 52px; /* Larger touch target on mobile */
    font-size: 1.125rem;
  }
}

/* Tablet optimizations */
@media (min-width: 641px) and (max-width: 768px) {
  .login-card {
    max-width: 480px;
    padding: var(--space-2xl) var(--space-xl);
  }
}

/* Large screens */
@media (min-width: 1024px) {
  .login-card {
    padding: 3rem 2.5rem;
  }

  .login-header h1 {
    font-size: 2rem;
  }
}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .login-card {
    border-width: 0.5px;
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .login-card {
    background: var(--color-background-soft);
    border: 1px solid var(--color-border);
  }
}

/* Focus states for accessibility */
.login-form :deep(.el-input__inner):focus {
  border-color: var(--maas-primary-500) !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

.login-form :deep(.el-button):focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

/* Loading state */
.login-form :deep(.el-button.is-loading) {
  pointer-events: none;
}

/* Form validation */
.login-form :deep(.el-form-item.is-error .el-input__inner) {
  border-color: var(--maas-error) !important;
}

/* Touch improvements for mobile */
@media (pointer: coarse) {
  .login-form :deep(.el-input__inner) {
    min-height: 48px;
    padding: 12px 16px;
    font-size: 16px; /* Prevents zoom on iOS */
  }

  .login-form :deep(.el-button) {
    min-height: 48px;
    padding: 12px 24px;
  }

  .login-form :deep(.el-checkbox__input) {
    transform: scale(1.2);
  }
}

/* Orientation handling */
@media (orientation: landscape) and (max-height: 500px) {
  .login-container {
    padding: var(--space-sm);
  }

  .login-card {
    padding: var(--space-lg);
    margin: var(--space-xs) 0;
  }

  .login-header {
    margin-bottom: var(--space-md);
  }

  .login-header h1 {
    font-size: 1.25rem;
    margin-bottom: var(--space-xs);
  }

  .login-header p {
    font-size: 0.875rem;
  }
}
</style>
