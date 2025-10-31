#!/bin/bash
# Docker MySQL Setup Script

echo "🐳 使用Docker设置MySQL数据库..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    echo "📝 安装命令: brew install --cask docker"
    exit 1
fi

# 停止并删除现有容器
echo "🔄 清理现有MySQL容器..."
docker stop mysql-stock 2>/dev/null || true
docker rm mysql-stock 2>/dev/null || true

# 启动MySQL容器
echo "🚀 启动MySQL容器..."
docker run --name mysql-stock \
    -e MYSQL_ROOT_PASSWORD=password123 \
    -e MYSQL_DATABASE=stock_analysis_db \
    -e MYSQL_USER=stock_user \
    -e MYSQL_PASSWORD=stock_password \
    -p 3306:3306 \
    -d mysql:8.0

# 等待MySQL启动
echo "⏳ 等待MySQL启动..."
sleep 10

# 测试连接
echo "🔍 测试数据库连接..."
docker exec mysql-stock mysql -u root -ppassword123 -e "SELECT VERSION();"

if [ $? -eq 0 ]; then
    echo "✅ MySQL容器启动成功!"
    echo "📝 数据库连接信息:"
    echo "   主机: localhost"
    echo "   端口: 3306"
    echo "   数据库: stock_analysis_db"
    echo "   用户: root"
    echo "   密码: password123"
    echo ""
    echo "🔄 现在可以运行: python init_db.py"
else
    echo "❌ MySQL容器启动失败"
    echo "📝 查看日志: docker logs mysql-stock"
fi

