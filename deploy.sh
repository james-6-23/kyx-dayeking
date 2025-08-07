#!/bin/bash
# Hajimi King 零停机部署脚本

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
PROJECT_NAME="hajimi-king"
REGISTRY="ghcr.io/yourusername"
HEALTH_CHECK_URL="http://localhost:9090/health"
ROLLBACK_ON_FAILURE=true
MAX_WAIT_TIME=300 # 5分钟

# 函数：打印带颜色的消息
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# 函数：检查服务健康状态
check_health() {
    local container=$1
    local max_attempts=30
    local attempt=0
    
    log "检查容器 $container 的健康状态..."
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec $container curl -sf $HEALTH_CHECK_URL > /dev/null 2>&1; then
            log "容器 $container 健康检查通过"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log "等待容器启动... ($attempt/$max_attempts)"
        sleep 10
    done
    
    error "容器 $container 健康检查失败"
    return 1
}

# 函数：备份当前数据
backup_data() {
    local backup_dir="/backup/hajimi/$(date +'%Y%m%d_%H%M%S')"
    log "备份数据到 $backup_dir"
    
    mkdir -p "$backup_dir"
    docker run --rm \
        -v hajimi-data:/data:ro \
        -v "$backup_dir":/backup \
        alpine tar czf /backup/data.tar.gz -C /data .
    
    log "数据备份完成"
}

# 函数：构建新镜像
build_image() {
    local version=$1
    log "构建镜像 $REGISTRY/$PROJECT_NAME:$version"
    
    docker build \
        --cache-from $REGISTRY/$PROJECT_NAME:latest \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        -t $REGISTRY/$PROJECT_NAME:$version \
        -t $REGISTRY/$PROJECT_NAME:latest \
        .
    
    log "镜像构建完成"
}

# 函数：推送镜像到仓库
push_image() {
    local version=$1
    log "推送镜像到仓库"
    
    docker push $REGISTRY/$PROJECT_NAME:$version
    docker push $REGISTRY/$PROJECT_NAME:latest
    
    log "镜像推送完成"
}

# 函数：蓝绿部署
blue_green_deploy() {
    local version=$1
    local old_container="${PROJECT_NAME}-blue"
    local new_container="${PROJECT_NAME}-green"
    
    # 检查当前运行的容器
    if docker ps -q -f name=$old_container > /dev/null 2>&1; then
        # Blue 正在运行，部署到 Green
        log "当前运行: Blue, 部署到: Green"
    else
        # Green 正在运行，部署到 Blue
        log "当前运行: Green, 部署到: Blue"
        old_container="${PROJECT_NAME}-green"
        new_container="${PROJECT_NAME}-blue"
    fi
    
    # 启动新容器
    log "启动新容器 $new_container"
    VERSION=$version INSTANCE=${new_container##*-} \
        docker-compose -f docker-compose.prod.yml up -d hajimi-king
    
    # 等待新容器健康
    if ! check_health $new_container; then
        error "新容器健康检查失败"
        docker stop $new_container
        docker rm $new_container
        return 1
    fi
    
    # 切换流量（如果使用负载均衡器）
    if command -v update_load_balancer &> /dev/null; then
        log "更新负载均衡器配置"
        update_load_balancer $new_container
    fi
    
    # 停止旧容器
    log "停止旧容器 $old_container"
    docker stop $old_container || true
    docker rm $old_container || true
    
    log "部署完成！新版本 $version 正在运行"
}

# 函数：回滚
rollback() {
    local previous_version=$1
    error "部署失败，开始回滚到版本 $previous_version"
    
    VERSION=$previous_version docker-compose -f docker-compose.prod.yml up -d
    
    if check_health "${PROJECT_NAME}-1"; then
        log "回滚成功"
    else
        error "回滚失败！请手动介入"
        exit 1
    fi
}

# 主函数
main() {
    local version=${1:-$(git rev-parse --short HEAD)}
    local previous_version=$(docker inspect ${PROJECT_NAME}-1 2>/dev/null | jq -r '.[0].Config.Labels["com.hajimi.version"]' || echo "unknown")
    
    log "开始部署 Hajimi King 版本: $version"
    log "当前版本: $previous_version"
    
    # 步骤1：备份数据
    if [ "${BACKUP_ENABLED:-true}" = "true" ]; then
        backup_data
    fi
    
    # 步骤2：构建镜像
    build_image $version
    
    # 步骤3：推送镜像（如果配置了仓库）
    if [ "${PUSH_TO_REGISTRY:-false}" = "true" ]; then
        push_image $version
    fi
    
    # 步骤4：执行部署
    if blue_green_deploy $version; then
        log "部署成功！"
        
        # 清理旧镜像
        log "清理未使用的镜像"
        docker image prune -f
    else
        if [ "$ROLLBACK_ON_FAILURE" = "true" ]; then
            rollback $previous_version
        fi
        exit 1
    fi
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --version)
            VERSION="$2"
            shift 2
            ;;
        --no-backup)
            BACKUP_ENABLED=false
            shift
            ;;
        --push)
            PUSH_TO_REGISTRY=true
            shift
            ;;
        --no-rollback)
            ROLLBACK_ON_FAILURE=false
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: $0 [--version VERSION] [--no-backup] [--push] [--no-rollback]"
            exit 1
            ;;
    esac
done

# 执行主函数
main "${VERSION:-}"