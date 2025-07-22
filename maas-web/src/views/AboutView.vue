<script setup lang="ts">
// 关于页面
</script>

<template>
  <div class="about">
    <!-- 页面头部（与首页一致） -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="32" color="#409EFF">
            <Platform />
          </el-icon>
          <span class="logo-text">MaaS 平台</span>
        </div>
        <div class="nav">
          <el-menu mode="horizontal" :default-active="'about'" router>
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/dashboard">控制台</el-menu-item>
            <el-menu-item index="/about">关于</el-menu-item>
          </el-menu>
        </div>
        <div class="user-actions">
          <el-button type="primary" @click="$router.push('/auth/login')"> 登录 </el-button>
          <el-button @click="$router.push('/auth/register')"> 注册 </el-button>
        </div>
      </div>
    </el-header>

    <el-container>
      <!-- 页面头部 -->
      <el-header height="200px" class="hero-header">
        <div class="hero-content">
          <h1 class="hero-title">关于 MaaS 平台</h1>
          <p class="hero-subtitle">模型即服务，让 AI 触手可及</p>
        </div>
      </el-header>

      <!-- 主要内容 -->
      <el-main class="main-content">
        <el-row justify="center">
          <el-col :span="20">
            <!-- 平台介绍 -->
            <section class="section">
              <h2 class="section-title">平台介绍</h2>
              <el-card class="intro-card" shadow="never">
                <p class="intro-text">
                  MaaS（Model-as-a-Service）是一个现代化的 AI 模型服务平台，
                  致力于为开发者和企业提供便捷、高效的模型管理和部署服务。 我们的使命是降低 AI
                  技术的使用门槛，让每个人都能轻松地使用和部署 AI 模型。
                </p>
              </el-card>
            </section>

            <!-- 核心特性 -->
            <section class="section">
              <h2 class="section-title">核心特性</h2>
              <el-row :gutter="24">
                <el-col :xs="24" :md="12" :lg="6">
                  <el-card class="feature-card" shadow="hover">
                    <div class="feature-icon">
                      <el-icon :size="32" color="#409EFF">
                        <Platform />
                      </el-icon>
                    </div>
                    <h3>模型管理</h3>
                    <p>支持多种 AI 模型的统一管理、版本控制和生命周期管理</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :md="12" :lg="6">
                  <el-card class="feature-card" shadow="hover">
                    <div class="feature-icon">
                      <el-icon :size="32" color="#67C23A">
                        <Cpu />
                      </el-icon>
                    </div>
                    <h3>弹性部署</h3>
                    <p>自动扩缩容、负载均衡，确保模型服务的高可用性</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :md="12" :lg="6">
                  <el-card class="feature-card" shadow="hover">
                    <div class="feature-icon">
                      <el-icon :size="32" color="#E6A23C">
                        <Monitor />
                      </el-icon>
                    </div>
                    <h3>实时监控</h3>
                    <p>全方位监控模型性能、资源使用和服务质量</p>
                  </el-card>
                </el-col>
                <el-col :xs="24" :md="12" :lg="6">
                  <el-card class="feature-card" shadow="hover">
                    <div class="feature-icon">
                      <el-icon :size="32" color="#F56C6C">
                        <Connection />
                      </el-icon>
                    </div>
                    <h3>API 集成</h3>
                    <p>提供 RESTful API 和 SDK，支持快速集成</p>
                  </el-card>
                </el-col>
              </el-row>
            </section>

          </el-col>
        </el-row>
      </el-main>
    </el-container>

    <!-- 页面底部（与首页一致） -->
    <el-footer class="footer">
      <div class="footer-content">
        <p>&copy; 2024 MaaS 平台. 保留所有权利.</p>
      </div>
    </el-footer>
  </div>
</template>

<style scoped>
.about {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 添加首页样式 */
.header {
  background: var(--color-background);
  border-bottom: 1px solid var(--color-border);
  padding: 0;
  height: var(--header-height);
  position: sticky;
  top: 0;
  z-index: 100;
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
  display: none;
}

.user-actions {
  display: flex;
  gap: var(--space-sm);
  flex-shrink: 0;
}

.hero-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero-content {
  text-align: center;
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 16px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  margin: 0;
}

.main-content {
  padding: 60px 20px;
}

.section {
  margin-bottom: 60px;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 40px;
  color: #303133;
}

.intro-card {
  border: none;
}

.intro-text {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #606266;
  text-align: center;
  margin: 0;
}

.feature-card {
  text-align: center;
  height: 100%;
  transition: transform 0.3s ease;
  margin-bottom: 24px;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  margin-bottom: 16px;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}


/* 移动端适配 */
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

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .main-content {
    padding: 40px 20px;
  }
}

/* 平板适配 */
@media (min-width: 641px) and (max-width: 768px) {
  .nav {
    display: flex;
  }

  .header-content {
    gap: var(--space-lg);
  }
}

/* 桌面端适配 */
@media (min-width: 769px) {
  .nav {
    display: flex;
  }

  .header-content {
    gap: var(--space-xl);
  }
}

/* 底部样式（与首页一致） */
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
</style>
