# 前端Docker配置
# 多阶段构建：构建阶段 + 运行阶段

# 构建阶段
FROM node:22-alpine3.20 AS builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用（默认生产环境，可通过构建参数指定）
ARG BUILD_MODE=prod
RUN npm run build:${BUILD_MODE}

# 运行阶段 - 使用nginx
FROM nginx:alpine AS runtime

# 复制nginx配置
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 创建启动脚本
RUN cat > /docker-entrypoint.sh << 'EOF'
#!/bin/sh
set -e

# 替换nginx配置中的环境变量
envsubst '${NGINX_SERVER_NAME} ${NGINX_ROOT_PATH} ${API_BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# 启动nginx
exec nginx -g 'daemon off;'
EOF

RUN chmod +x /docker-entrypoint.sh

# 暴露端口
EXPOSE 80

# 启动命令
ENTRYPOINT ["/docker-entrypoint.sh"]

# 使用示例:
# 构建镜像:
# docker build --build-arg BUILD_MODE=dev -t maas-web:dev .
# docker build --build-arg BUILD_MODE=test -t maas-web:test .
# docker build --build-arg BUILD_MODE=prod -t maas-web:prod .
#
# 运行容器:
# docker run -d -p 80:80 \
#   -e NGINX_SERVER_NAME=your-domain.com \
#   -e NGINX_ROOT_PATH=/usr/share/nginx/html \
#   -e API_BACKEND_URL=http://api-server:8000 \
#   maas-web:prod