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

import { createRouter, createWebHashHistory } from 'vue-router'
import { routes } from './routes'
import { routeGuard } from './guards'
import { preloadRouteComponents } from './preloader'

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
})

// 应用路由守卫
router.beforeEach(async (to, from, next) => {
  // 应用统一的路由守卫
  await routeGuard(to, from, next)

  // 预加载路由组件（异步，不阻塞导航）
  if (to.name && typeof to.name === 'string') {
    preloadRouteComponents(to.name)
  }
})

export default router
