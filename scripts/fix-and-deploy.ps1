# Hajimi King Docker 部署修复脚本 (Windows PowerShell)
# 解决 cmj2002/warp 镜像不可用的问题

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Hajimi King Docker 部署修复脚本" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Docker 是否安装
try {
    docker --version | Out-Null
    Write-Host "✓ Docker 已安装" -ForegroundColor Green
} catch {
    Write-Host "错误: Docker 未安装" -ForegroundColor Red
    Write-Host "请先安装 Docker Desktop: https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# 检查 Docker Compose
try {
    docker compose version | Out-Null
    Write-Host "✓ Docker Compose 已安装" -ForegroundColor Green
} catch {
    Write-Host "错误: Docker Compose 未安装" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 备份原始配置
if (Test-Path "docker-compose.yml") {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "docker-compose.yml.backup.$timestamp"
    Copy-Item "docker-compose.yml" $backupFile
    Write-Host "✓ 已备份原始配置到: $backupFile" -ForegroundColor Green
}

# 显示菜单
Write-Host ""
Write-Host "请选择部署方式：" -ForegroundColor Yellow
Write-Host "1) 部署主服务 + WARP 代理（推荐）"
Write-Host "2) 仅部署主服务（不使用代理）"
Write-Host "3) 部署主服务 + SOCKS5 代理"
Write-Host "4) 修复镜像问题（仅更新 docker-compose.yml）"
Write-Host "5) 退出"
Write-Host ""

$choice = Read-Host "请输入选项 [1-5]"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "正在部署主服务 + WARP 代理..." -ForegroundColor Yellow
        
        # 检查 .env 文件
        if (-not (Test-Path ".env")) {
            Write-Host "未找到 .env 文件，从模板创建..." -ForegroundColor Yellow
            if (Test-Path "env.example") {
                Copy-Item "env.example" ".env"
                Write-Host "✓ 已创建 .env 文件" -ForegroundColor Green
                Write-Host "重要: 请在 .env 文件中配置 GITHUB_TOKENS" -ForegroundColor Red
                Write-Host "按任意键继续..."
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            } else {
                Write-Host "错误: 未找到 env.example 文件" -ForegroundColor Red
                exit 1
            }
        }
        
        # 拉取镜像
        Write-Host "拉取 WARP 代理镜像..."
        try {
            docker pull caomingjun/warp:latest
        } catch {
            Write-Host "直接拉取失败，尝试使用镜像加速器..." -ForegroundColor Yellow
            docker pull registry.cn-hangzhou.aliyuncs.com/caomingjun/warp:latest
            docker tag registry.cn-hangzhou.aliyuncs.com/caomingjun/warp:latest caomingjun/warp:latest
        }
        
        # 启动服务
        Write-Host "启动服务..."
        docker compose --profile proxy up -d --build
        
        Write-Host ""
        Write-Host "✓ 部署完成！" -ForegroundColor Green
        Write-Host ""
        Write-Host "服务状态：" -ForegroundColor Cyan
        docker compose ps
        Write-Host ""
        Write-Host "查看日志：" -ForegroundColor Cyan
        Write-Host "  主服务: docker logs hajimi-king"
        Write-Host "  代理服务: docker logs warp-proxy"
    }
    
    "2" {
        Write-Host ""
        Write-Host "正在部署主服务（不使用代理）..." -ForegroundColor Yellow
        
        # 检查 .env 文件
        if (-not (Test-Path ".env")) {
            Write-Host "未找到 .env 文件，从模板创建..." -ForegroundColor Yellow
            if (Test-Path "env.example") {
                Copy-Item "env.example" ".env"
                Write-Host "✓ 已创建 .env 文件" -ForegroundColor Green
                Write-Host "重要: 请在 .env 文件中配置 GITHUB_TOKENS" -ForegroundColor Red
                Write-Host "按任意键继续..."
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            } else {
                Write-Host "错误: 未找到 env.example 文件" -ForegroundColor Red
                exit 1
            }
        }
        
        # 启动服务
        Write-Host "启动服务..."
        docker compose up -d --build
        
        Write-Host ""
        Write-Host "✓ 部署完成！" -ForegroundColor Green
        Write-Host ""
        Write-Host "服务状态：" -ForegroundColor Cyan
        docker compose ps
        Write-Host ""
        Write-Host "查看日志：" -ForegroundColor Cyan
        Write-Host "  docker logs hajimi-king"
    }
    
    "3" {
        Write-Host ""
        Write-Host "正在部署主服务 + SOCKS5 代理..." -ForegroundColor Yellow
        Write-Host "注意: 此选项需要手动配置 docker-compose.yml" -ForegroundColor Yellow
        Write-Host "请参考 docker-compose-fixed.yml 中的 socks5-proxy 配置"
    }
    
    "4" {
        Write-Host ""
        Write-Host "修复 docker-compose.yml 中的镜像问题..." -ForegroundColor Yellow
        
        # 读取文件内容
        $content = Get-Content "docker-compose.yml" -Raw
        
        # 替换有问题的镜像
        $content = $content -replace 'cmj2002/warp:latest', 'caomingjun/warp:latest'
        
        # 保存修改
        Set-Content "docker-compose.yml" $content -NoNewline
        
        Write-Host "✓ 已将 cmj2002/warp 替换为 caomingjun/warp" -ForegroundColor Green
        Write-Host ""
        Write-Host "现在可以运行以下命令部署：" -ForegroundColor Cyan
        Write-Host "  docker compose --profile proxy up -d"
    }
    
    "5" {
        Write-Host "退出"
        exit 0
    }
    
    default {
        Write-Host "无效选项" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "部署提示：" -ForegroundColor Yellow
Write-Host "1. 确保已在 .env 文件中配置 GITHUB_TOKENS"
Write-Host "2. 如需使用代理，在 .env 中添加："
Write-Host "   PROXY=socks5://warp-proxy:1080"
Write-Host "3. 查看实时日志："
Write-Host "   docker compose logs -f"
Write-Host "=========================================" -ForegroundColor Cyan