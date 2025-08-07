# Hajimi King Makefile
.PHONY: help build run stop clean logs shell test deploy rollback backup

# 默认目标
.DEFAULT_GOAL := help

# 变量定义
PROJECT_NAME := hajimi-king
DOCKER_REGISTRY := ghcr.io/yourusername
VERSION := $(shell git describe --tags --always --dirty)
DOCKER_IMAGE := $(PROJECT_NAME):$(VERSION)
COMPOSE_FILE := docker-compose.yml
COMPOSE_PROD_FILE := docker-compose.prod.yml

# 帮助信息
help: ## 显示帮助信息
	@echo "Hajimi King - Docker 部署命令"
	@echo ""
	@echo "使用方法: make [目标]"
	@echo ""
	@echo "可用目标:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# 开发环境
build: ## 构建 Docker 镜像
	docker-compose build --no-cache

build-fast: ## 快速构建（使用缓存）
	docker-compose build

run: ## 启动服务（开发环境）
	docker-compose up -d
	@echo "服务已启动！查看日志: make logs"

stop: ## 停止服务
	docker-compose down

restart: stop run ## 重启服务

logs: ## 查看日志
	docker-compose logs -f --tail=100

shell: ## 进入容器 shell
	docker-compose exec hajimi-king /bin/bash

# 生产环境
prod-build: ## 构建生产镜像
	docker build \
		--cache-from $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest \
		--build-arg BUILDKIT_INLINE_CACHE=1 \
		-t $(DOCKER_REGISTRY)/$(DOCKER_IMAGE) \
		-t $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest \
		.

prod-push: ## 推送镜像到仓库
	docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE)
	docker push $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest

prod-run: ## 启动生产环境
	VERSION=$(VERSION) docker-compose -f $(COMPOSE_PROD_FILE) up -d

prod-stop: ## 停止生产环境
	docker-compose -f $(COMPOSE_PROD_FILE) down

prod-logs: ## 查看生产日志
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f --tail=100

# 部署相关
deploy: ## 执行零停机部署
	@chmod +x deploy.sh
	./deploy.sh --version $(VERSION)

deploy-full: prod-build prod-push deploy ## 完整部署流程

rollback: ## 回滚到上一版本
	@echo "回滚到上一版本..."
	docker-compose -f $(COMPOSE_PROD_FILE) down
	VERSION=latest docker-compose -f $(COMPOSE_PROD_FILE) up -d

# 数据管理
backup: ## 备份数据
	@echo "备份数据..."
	@mkdir -p backups
	docker run --rm \
		-v $(PROJECT_NAME)-data:/data:ro \
		-v $(PWD)/backups:/backup \
		alpine tar czf /backup/hajimi-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "备份完成: backups/hajimi-backup-$(shell date +%Y%m%d-%H%M%S).tar.gz"

restore: ## 恢复数据（需要指定 BACKUP_FILE）
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "错误: 请指定备份文件 BACKUP_FILE=backups/hajimi-backup-xxx.tar.gz"; \
		exit 1; \
	fi
	@echo "恢复数据: $(BACKUP_FILE)"
	docker run --rm \
		-v $(PROJECT_NAME)-data:/data \
		-v $(PWD)/$(BACKUP_FILE):/backup.tar.gz:ro \
		alpine tar xzf /backup.tar.gz -C /data

# 维护命令
clean: ## 清理未使用的镜像和容器
	docker system prune -f
	docker volume prune -f

clean-all: ## 深度清理（包括所有停止的容器和未使用的镜像）
	docker system prune -af
	docker volume prune -f

stats: ## 显示资源使用情况
	docker stats --no-stream

health: ## 检查服务健康状态
	@docker-compose ps
	@echo ""
	@echo "健康检查:"
	@docker exec $(PROJECT_NAME) curl -sf http://localhost:9090/health && echo "✓ 服务健康" || echo "✗ 服务异常"

# 开发工具
test: ## 运行测试
	docker-compose run --rm hajimi-king python -m pytest tests/

lint: ## 代码检查
	docker-compose run --rm hajimi-king python -m ruff check .

format: ## 格式化代码
	docker-compose run --rm hajimi-king python -m black .

# 调试命令
debug-env: ## 显示环境变量
	docker-compose exec hajimi-king env | sort

debug-network: ## 测试网络连接
	docker-compose exec hajimi-king ping -c 3 google.com
	docker-compose exec hajimi-king curl -I https://api.github.com

debug-files: ## 列出数据目录文件
	docker-compose exec hajimi-king ls -la /app/data/

# 监控
monitor: ## 启动监控服务
	docker-compose --profile monitoring up -d

monitor-stop: ## 停止监控服务
	docker-compose --profile monitoring down

# 快捷命令
up: run ## 启动（别名）
down: stop ## 停止（别名）
ps: ## 显示运行状态
	docker-compose ps

# 版本信息
version: ## 显示版本信息
	@echo "Project: $(PROJECT_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Image: $(DOCKER_REGISTRY)/$(DOCKER_IMAGE)"