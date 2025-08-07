# Docker镜像重建脚本 (Windows PowerShell)
# 解决依赖包安装问题

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Docker镜像重建脚本" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 停止运行中的容器
Write-Host "停止运行中的容器..." -ForegroundColor Yellow
docker compose down

# 清理旧镜像
Write-Host "清理旧镜像..." -ForegroundColor Yellow
docker rmi hajimi-king:latest 2>$null

# 重新构建镜像（不使用缓存）
Write-Host "重新构建镜像（不使用缓存）..." -ForegroundColor Yellow
docker compose build --no-cache hajimi-king

# 验证依赖包安装
Write-Host "验证依赖包安装..." -ForegroundColor Yellow

$pythonScript = @"
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
"@

docker run --rm hajimi-king:latest python -c $pythonScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 依赖包验证成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "现在可以启动服务：" -ForegroundColor Cyan
    Write-Host "  docker compose up -d"
    Write-Host "  或"
    Write-Host "  docker compose --profile proxy up -d"
} else {
    Write-Host "✗ 依赖包验证失败" -ForegroundColor Red
    Write-Host "请检查 requirements.txt 文件"
    exit 1
}