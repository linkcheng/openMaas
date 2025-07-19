<script setup lang="ts">
// 关于页面
</script>

<template>
  <div class="about">
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
                  致力于为开发者和企业提供便捷、高效的模型管理和部署服务。
                  我们的使命是降低 AI 技术的使用门槛，让每个人都能轻松地使用和部署 AI 模型。
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

            <!-- 技术架构 -->
            <section class="section">
              <h2 class="section-title">技术架构</h2>
              <el-row :gutter="24">
                <el-col :xs="24" :lg="12">
                  <el-card class="tech-card">
                    <template #header>
                      <h3>
                        <el-icon><Cpu /></el-icon>
                        前端技术栈
                      </h3>
                    </template>
                    <ul class="tech-list">
                      <li>Vue 3 + TypeScript</li>
                      <li>Element Plus UI 框架</li>
                      <li>Vite 构建工具</li>
                      <li>Pinia 状态管理</li>
                      <li>Vue Router 路由管理</li>
                    </ul>
                  </el-card>
                </el-col>
                <el-col :xs="24" :lg="12">
                  <el-card class="tech-card">
                    <template #header>
                      <h3>
                        <el-icon><Server /></el-icon>
                        后端技术栈
                      </h3>
                    </template>
                    <ul class="tech-list">
                      <li>Python + FastAPI</li>
                      <li>SQLAlchemy ORM</li>
                      <li>PostgreSQL 数据库</li>
                      <li>Redis 缓存</li>
                      <li>Celery 异步任务</li>
                    </ul>
                  </el-card>
                </el-col>
              </el-row>
            </section>

            <!-- 团队信息 -->
            <section class="section">
              <h2 class="section-title">开发团队</h2>
              <el-card class="team-card">
                <p class="team-description">
                  我们是一支专注于 AI 技术的团队，拥有丰富的机器学习、系统架构和产品开发经验。
                  致力于打造最优秀的 AI 模型服务平台，为用户提供卓越的体验。
                </p>
                <el-divider />
                <div class="contact-info">
                  <h3>联系我们</h3>
                  <p>
                    <el-icon><Message /></el-icon>
                    邮箱：support@maas-platform.com
                  </p>
                  <p>
                    <el-icon><Phone /></el-icon>
                    电话：400-123-4567
                  </p>
                  <p>
                    <el-icon><Location /></el-icon>
                    地址：北京市海淀区中关村软件园
                  </p>
                </div>
              </el-card>
            </section>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<style scoped>
.about {
  min-height: 100vh;
  background-color: #f5f7fa;
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

.tech-card {
  height: 100%;
  margin-bottom: 24px;
}

.tech-card h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  color: #303133;
}

.tech-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.tech-list li {
  padding: 8px 0;
  color: #606266;
  border-bottom: 1px solid #f0f0f0;
}

.tech-list li:last-child {
  border-bottom: none;
}

.team-card {
  text-align: center;
}

.team-description {
  font-size: 1.1rem;
  line-height: 1.8;
  color: #606266;
  margin-bottom: 0;
}

.contact-info {
  text-align: left;
}

.contact-info h3 {
  margin-bottom: 20px;
  color: #303133;
}

.contact-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 12px 0;
  color: #606266;
}

@media (max-width: 768px) {
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
</style>
