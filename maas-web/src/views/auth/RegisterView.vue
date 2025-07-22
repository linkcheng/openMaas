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
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <el-icon :size="48" color="#409EFF">
          <UserFilled />
        </el-icon>
        <h1>MaaS 平台</h1>
        <p>注册您的账户</p>
      </div>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        class="register-form"
        size="large"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名（3-50字符，字母数字下划线）"
            prefix-icon="User"
            clearable
            :maxlength="50"
            show-word-limit
          />
          <div
            v-if="registerForm.username && !/^[a-zA-Z0-9_]+$/.test(registerForm.username)"
            class="validation-tip error"
          >
            用户名只能包含字母、数字和下划线
          </div>
          <div
            v-else-if="registerForm.username && registerForm.username.length >= 3"
            class="validation-tip success"
          >
            ✓ 用户名格式正确
          </div>
        </el-form-item>

        <el-form-item label="邮箱地址" prop="email">
          <el-input
            v-model="registerForm.email"
            type="email"
            placeholder="请输入邮箱地址"
            prefix-icon="Message"
            clearable
          />
          <div
            v-if="
              registerForm.email &&
              !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(registerForm.email)
            "
            class="validation-tip error"
          >
            请输入有效的邮箱地址
          </div>
          <div
            v-else-if="
              registerForm.email &&
              /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(registerForm.email)
            "
            class="validation-tip success"
          >
            ✓ 邮箱格式正确
          </div>
        </el-form-item>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="名字" prop="first_name">
              <el-input
                v-model="registerForm.first_name"
                placeholder="请输入名字"
                clearable
                :maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓氏" prop="last_name">
              <el-input
                v-model="registerForm.last_name"
                placeholder="请输入姓氏"
                clearable
                :maxlength="50"
                show-word-limit
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="组织 (可选)" prop="organization">
          <el-input
            v-model="registerForm.organization"
            placeholder="请输入组织名称"
            prefix-icon="OfficeBuilding"
            clearable
            :maxlength="255"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="至少8位，包含大小写字母和数字"
            prefix-icon="Lock"
            show-password
            clearable
          />
          <!-- 密码强度提示 -->
          <div class="password-tips">
            <div class="password-tip" :class="{ valid: passwordChecks.length }">
              <el-icon><Select /></el-icon>
              <span>至少8个字符</span>
            </div>
            <div class="password-tip" :class="{ valid: passwordChecks.uppercase }">
              <el-icon><Select /></el-icon>
              <span>包含大写字母</span>
            </div>
            <div class="password-tip" :class="{ valid: passwordChecks.lowercase }">
              <el-icon><Select /></el-icon>
              <span>包含小写字母</span>
            </div>
            <div class="password-tip" :class="{ valid: passwordChecks.number }">
              <el-icon><Select /></el-icon>
              <span>包含数字</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="registerForm.confirm_password"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item prop="agreeTerms">
          <el-checkbox v-model="registerForm.agreeTerms">
            我已阅读并同意
            <el-link type="primary">服务条款</el-link>
            和
            <el-link type="primary">隐私政策</el-link>
          </el-checkbox>
        </el-form-item>

        <el-form-item v-if="error">
          <el-alert :title="error" type="error" show-icon :closable="false" />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="register-button"
            :loading="loading"
            @click="handleRegister"
          >
            {{ loading ? '注册中...' : '创建账户' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-link">
        <span>已有账户？</span>
        <el-link type="primary" @click="goToLogin"> 立即登录 </el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { register } = useAuth()

const loading = ref(false)
const error = ref('')

const registerForm = reactive({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  organization: '',
  password: '',
  confirm_password: '',
  agreeTerms: false,
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在 3 到 50 个字符', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
          callback(new Error('用户名只能包含字母、数字和下划线'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        // 更严格的邮箱验证
        const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
        if (value && !emailRegex.test(value)) {
          callback(new Error('请输入有效的邮箱地址'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  first_name: [
    { required: true, message: '请输入名字', trigger: 'blur' },
    { min: 1, max: 50, message: '名字长度在 1 到 50 个字符', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (value && /^\s*$/.test(value)) {
          callback(new Error('名字不能只包含空格'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  last_name: [
    { required: true, message: '请输入姓氏', trigger: 'blur' },
    { min: 1, max: 50, message: '姓氏长度在 1 到 50 个字符', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (value && /^\s*$/.test(value)) {
          callback(new Error('姓氏不能只包含空格'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  organization: [
    { max: 255, message: '组织名称不能超过255个字符', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (value && /^\s*$/.test(value)) {
          callback(new Error('组织名称不能只包含空格'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 100, message: '密码长度在 8 到 100 个字符', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (!/(?=.*[a-z])/.test(value)) {
          callback(new Error('密码必须包含小写字母'))
        } else if (!/(?=.*[A-Z])/.test(value)) {
          callback(new Error('密码必须包含大写字母'))
        } else if (!/(?=.*\d)/.test(value)) {
          callback(new Error('密码必须包含数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  agreeTerms: [
    {
      validator: (_rule: unknown, value: boolean, callback: (error?: Error) => void) => {
        if (!value) {
          callback(new Error('请阅读并同意服务条款和隐私政策'))
        } else {
          callback()
        }
      },
      trigger: 'change',
    },
  ],
}

const registerFormRef = ref()

// 密码强度检查
const passwordChecks = computed(() => ({
  length: registerForm.password.length >= 8,
  uppercase: /[A-Z]/.test(registerForm.password),
  lowercase: /[a-z]/.test(registerForm.password),
  number: /\d/.test(registerForm.password),
}))

const goToLogin = () => {
  router.push('/auth/login')
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  try {
    await registerFormRef.value.validate()
    loading.value = true
    error.value = ''

    const result = await register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      first_name: registerForm.first_name,
      last_name: registerForm.last_name,
      organization: registerForm.organization || undefined,
    })

    if (result.success) {
      ElMessage.success('注册成功，请检查邮箱完成验证后登录')
      router.push('/auth/login')
    } else {
      error.value = result.error || '注册失败，请重试'
    }
  } catch (validationError) {
    console.error('表单验证失败:', validationError)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
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

.register-card {
  background: var(--color-background);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--space-2xl);
  width: 100%;
  max-width: 480px;
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

.register-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}

.register-header h1 {
  margin: var(--space-md) 0 var(--space-sm);
  color: var(--color-text-primary);
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.2;
}

.register-header p {
  color: var(--color-text-secondary);
  margin: 0;
  font-size: 1rem;
  line-height: 1.5;
}

.register-form {
  margin-bottom: var(--space-lg);
}

.register-button {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 500;
  border-radius: var(--radius-md);

  /* Touch optimization */
  touch-action: manipulation;
  -webkit-tap-highlight-color: transparent;
}

.login-link {
  text-align: center;
  color: var(--color-text-secondary);
  margin-top: var(--space-md);
}

.login-link span {
  margin-right: var(--space-sm);
}

/* 验证提示样式 */
.validation-tip {
  font-size: 0.75rem;
  margin-top: 4px;
  transition: all 0.2s ease;
}

.validation-tip.error {
  color: var(--el-color-danger);
}

.validation-tip.success {
  color: var(--el-color-success);
}

/* 密码强度提示样式 */
.password-tips {
  margin-top: var(--space-sm);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-xs);
}

.password-tip {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  transition: color 0.2s ease;
}

.password-tip.valid {
  color: var(--el-color-success);
}

.password-tip .el-icon {
  font-size: 0.75rem;
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .register-container {
    padding: var(--space-sm);
    /* Fix for mobile browsers */
    min-height: calc(100vh - env(keyboard-inset-height, 0px));
  }

  .register-card {
    padding: var(--space-xl) var(--space-lg);
    margin: var(--space-sm) 0;
    border-radius: var(--radius-lg);
    max-width: 100%;
  }

  .register-header h1 {
    font-size: 1.5rem;
  }

  .register-header p {
    font-size: 0.875rem;
  }

  .register-button {
    height: 52px; /* Larger touch target on mobile */
    font-size: 1.125rem;
  }

  .password-tips {
    grid-template-columns: 1fr;
  }
}

/* Tablet optimizations */
@media (min-width: 641px) and (max-width: 768px) {
  .register-card {
    max-width: 520px;
    padding: var(--space-2xl) var(--space-xl);
  }
}

/* Large screens */
@media (min-width: 1024px) {
  .register-card {
    padding: 3rem 2.5rem;
    max-width: 520px;
  }

  .register-header h1 {
    font-size: 2rem;
  }
}

/* High DPI displays */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .register-card {
    border-width: 0.5px;
  }
}

/* Dark mode adjustments */
@media (prefers-color-scheme: dark) {
  .register-card {
    background: var(--color-background-soft);
    border: 1px solid var(--color-border);
  }
}

/* Focus states for accessibility */
.register-form :deep(.el-input__inner):focus {
  border-color: var(--maas-primary-500) !important;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

.register-form :deep(.el-button):focus {
  outline: 2px solid var(--maas-primary-500);
  outline-offset: 2px;
}

/* Loading state */
.register-form :deep(.el-button.is-loading) {
  pointer-events: none;
}

/* Form validation */
.register-form :deep(.el-form-item.is-error .el-input__inner) {
  border-color: var(--maas-error) !important;
}

/* Touch improvements for mobile */
@media (pointer: coarse) {
  .register-form :deep(.el-input__inner) {
    min-height: 48px;
    padding: 12px 16px;
    font-size: 16px; /* Prevents zoom on iOS */
  }

  .register-form :deep(.el-button) {
    min-height: 48px;
    padding: 12px 24px;
  }

  .register-form :deep(.el-checkbox__input) {
    transform: scale(1.2);
  }
}

/* Orientation handling */
@media (orientation: landscape) and (max-height: 500px) {
  .register-container {
    padding: var(--space-sm);
  }

  .register-card {
    padding: var(--space-lg);
    margin: var(--space-xs) 0;
  }

  .register-header {
    margin-bottom: var(--space-md);
  }

  .register-header h1 {
    font-size: 1.25rem;
    margin-bottom: var(--space-xs);
  }

  .register-header p {
    font-size: 0.875rem;
  }
}
</style>
