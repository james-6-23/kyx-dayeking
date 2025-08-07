#!/bin/bash

# Hajimi King Docker 部署修复脚本
# 解决 cmj2002/warp 镜像不可用的问题

set -e

echo "========================================="
echo "  Hajimi King Docker 部署修复脚本"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker 未安装${NC}"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    echo -e "${RED}错误: Docker Compose 未安装${NC}"
    echo "请先安装 Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker 和 Docker Compose 已安装${NC}"
echo ""

# 备份原始配置
if [ -f "docker-compose.yml" ]; then
    echo "备份原始 docker-compose.yml..."
    cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ 备份完成${NC}"
fi

# 选择部署方式
echo ""
echo "请选择部署方式："
echo "1) 部署主服务 + WARP 代理（推荐）"
echo "2) 仅部署主服务（不使用代理）"
echo "3) 部署主服务 + SOCKS5 代理"
echo "4) 退出"
echo ""
read -p "请输入选项 [1-4]: " choice

case $choice in
    1)
        echo ""
        echo -e "${YELLOW}正在部署主服务 + WARP 代理...${NC}"
        
        # 检查 .env 文件
        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}未找到 .env 文件，从模板创建...${NC}"
            if [ -f "env.example" ]; then
                cp env.example .env
                echo -e "${GREEN}✓ 已创建 .env 文件，请编辑配置${NC}"
                echo -e "${RED}重要: 请在 .env 文件中配置 GITHUB_TOKENS${NC}"
                read -p "按回车键继续..."
            else
                echo -e "${RED}错误: 未找到 env.example 文件${NC}"
                exit 1
            fi
        fi
        
        # 拉取镜像
        echo "拉取 WARP 代理镜像..."
        docker pull caomingjun/warp:latest || {
            echo -e "${YELLOW}直接拉取失败，尝试使用镜像加速器...${NC}"
            docker pull registry.cn-hangzhou.aliyuncs.com/caomingjun/warp:latest
            docker tag registry.cn-hangzhou.aliyuncs.com/caomingjun/warp:latest caomingjun/warp:latest
        }
        
        # 启动服务
        echo "启动服务..."
        docker compose --profile proxy up -d --build
        
        echo ""
        echo -e "${GREEN}✓ 部署完成！${NC}"
        echo ""
        echo "服务状态："
        docker compose ps
        echo ""
        echo "查看日志："
        echo "  主服务: docker logs hajimi-king"
        echo "  代理服务: docker logs warp-proxy"
        ;;
        
    2)
        echo ""
        echo -e "${YELLOW}正在部署主服务（不使用代理）...${NC}"
        
        # 检查 .env 文件
        if [ ! -f ".env" ]; then
            echo -e "${YELLOW}未找到 .env 文件，从模板创建...${NC}"
            if [ -f "env.example" ]; then
                cp env.example .env
                echo -e "${GREEN}✓ 已创建 .env 文件，请编辑配置${NC}"
                echo -e "${RED}重要: 请在 .env 文件中配置 GITHUB_TOKENS${NC}"
                read -p "按回车键继续..."
            else
                echo -e "${RED}错误: 未找到 env.example 文件${NC}"
                exit 1
            fi
        fi
        
        # 启动服务
        echo "启动服务..."
        docker compose up -d --build
        
        echo ""
        echo -e "${GREEN}✓ 部署完成！${NC}"
        echo ""
        echo "服务状态："
        docker compose ps
        echo ""
        echo "查看日志："
        echo "  docker logs hajimi-king"
        ;;
        
    3)
        echo ""
        echo -e "${YELLOW}正在部署主服务 + SOCKS5 代理...${NC}"
        
        # 需要先修改 docker-compose.yml 添加 socks5 配置
        echo -e "${YELLOW}注意: 此选项需要手动配置 docker-compose.yml${NC}"
        echo "请参考 docker-compose-fixed.yml 中的 socks5-proxy 配置"
        exit 0
        ;;
        
    4)
        echo "退出"
        exit 0
        ;;
        
    *)
        echo -e "${RED}无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "部署提示："
echo "1. 确保已在 .env 文件中配置 GITHUB_TOKENS"
echo "2. 如需使用代理，在 .env 中添加："
echo "   PROXY=socks5://warp-proxy:1080"
echo "3. 查看实时日志："
echo "   docker compose logs -f"
echo "========================================="