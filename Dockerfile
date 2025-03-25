FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 确保脚本有执行权限
RUN chmod +x main.py

# 设置环境变量（根据需要调整）
ENV PYTHONUNBUFFERED=1

# 使用非 root 用户运行容器（安全最佳实践）
RUN useradd -m appuser
USER appuser

# 容器启动命令
CMD ["python", "main.py"]