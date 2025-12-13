#! /usr/bin/env bash

set -e  # 遇到错误立即退出
set -x  # 打印执行的命令（方便调试）

# 1. 等待数据库启动
python app/backend_pre_start.py

# 2. 执行数据库迁移（应用最新的表结构变更）
alembic upgrade head

# 3. 创建初始数据（如管理员账号）
python app/initial_data.py