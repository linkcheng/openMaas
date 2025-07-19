<script setup lang="ts">
// MaaS 平台首页
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
            <el-menu-item index="/home">首页</el-menu-item>
            <el-menu-item index="/dashboard">控制台</el-menu-item>
            <el-menu-item index="/about">关于</el-menu-item>
          </el-menu>
        </div>
        <div class="user-actions">
          <el-button type="primary" @click="$router.push('/auth/login')">
            登录
          </el-button>
          <el-button @click="$router.push('/auth/register')">
            注册
          </el-button>
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
              <p class="hero-subtitle">
                模型即服务平台，为您提供强大的 AI 模型服务和管理能力
              </p>
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
        <p>&copy; 2024 MaaS 平台. 保留所有权利.</p>
      </div>
    </el-footer>
  </div>
</template>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  height: 60px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.nav {
  flex: 1;
  display: flex;
  justify-content: center;
}

.user-actions {
  display: flex;
  gap: 12px;
}

.main-content {
  flex: 1;
  padding: 0;
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 80px 20px;
  text-align: center;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 20px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.25rem;
  margin-bottom: 40px;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.features-section,
.quickstart-section {
  padding: 80px 20px;
}

.features-section {
  background: #f8f9fa;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 60px;
  color: #303133;
}

.feature-card,
.quickstart-card {
  text-align: center;
  padding: 40px 20px;
  height: 100%;
  transition: transform 0.3s ease;
}

.feature-card:hover,
.quickstart-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  margin-bottom: 20px;
}

.feature-card h3,
.quickstart-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 15px;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.feature-card p,
.quickstart-card p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 20px;
}

.footer {
  background: #303133;
  color: white;
  text-align: center;
  padding: 20px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    height: auto;
    padding: 10px 20px;
  }

  .nav {
    order: 3;
    width: 100%;
    margin-top: 10px;
  }

  .user-actions {
    order: 2;
    margin: 10px 0;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .section-title {
    font-size: 2rem;
  }
}
</style>
