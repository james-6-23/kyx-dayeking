# 多阶段构建以优化镜像大小
FROM python:3.11-slim as builder

# 设置构建时的环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 创建虚拟环境
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制依赖文件
COPY requirements.txt pyproject.toml ./

# 安装Python依赖 - 使用requirements.txt确保所有依赖都被安装
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 最终运行阶段
FROM python:3.11-slim

# 设置运行时环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # 默认环境变量
    DATA_PATH=/app/data \
    QUERIES_FILE=queries.txt

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p /app/data/keys /app/data/logs /app/data/cache && \
    chown -R appuser:appuser /app/data

# 创建健康检查脚本
RUN echo '#!/bin/sh\npgrep -f "hajimi_king" > /dev/null || exit 1' > /healthcheck.sh && \
    chmod +x /healthcheck.sh

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD /healthcheck.sh

# 数据卷
VOLUME ["/app/data"]

# 启动命令 - 支持选择不同版本
CMD ["python", "app/api_key_scanner.py"]
