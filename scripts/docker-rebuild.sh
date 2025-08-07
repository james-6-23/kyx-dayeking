#!/bin/bash

# Docker镜像重建脚本
# 解决依赖包安装问题

set -e

echo "========================================="
echo "  Docker镜像重建脚本"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 停止运行中的容器
echo -e "${YELLOW}停止运行中的容器...${NC}"
docker compose down

# 清理旧镜像
echo -e "${YELLOW}清理旧镜像...${NC}"
docker rmi hajimi-king:latest 2>/dev/null || true

# 重新构建镜像（不使用缓存）
echo -e "${YELLOW}重新构建镜像（不使用缓存）...${NC}"
docker compose build --no-cache hajimi-king

# 验证依赖包安装
echo -e "${YELLOW}验证依赖包安装...${NC}"
docker run --rm hajimi-king:latest python -c "
import sys
print('Python版本:', sys.version)
print('检查依赖包...')
try:
    import google.generativeai as genai
    print('✓ google-generativeai 已安装')
except ImportError as e:
    print('✗ google-generativeai 未安装:', e)
    sys.exit(1)
    
try:
    import requests
    print('✓ requests 已安装')
except ImportError as e:
    print('✗ requests 未安装:', e)
    sys.exit(1)
    
try:
    import dotenv
    print('✓ python-dotenv 已安装')
except ImportError as e:
    print('✗ python-dotenv 未安装:', e)
    sys.exit(1)
    
print('所有依赖包已正确安装！')
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 依赖包验证成功！${NC}"
    echo ""
    echo "现在可以启动服务："
    echo "  docker compose up -d"
    echo "  或"
    echo "  docker compose --profile proxy up -d"
else
    echo -e "${RED}✗ 依赖包验证失败${NC}"
    echo "请检查 requirements.txt 文件"
    exit 1
fi