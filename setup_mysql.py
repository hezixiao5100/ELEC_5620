#!/usr/bin/env python3
"""
MySQL Setup Script
This script helps set up the MySQL database for the stock analysis system
"""
import subprocess
import sys
import time

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - 成功!")
            return True, result.stdout
        else:
            print(f"❌ {description} - 失败: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - 错误: {e}")
        return False, str(e)

def setup_mysql():
    """Set up MySQL database"""
    print("🚀 设置MySQL数据库...")
    print("=" * 50)
    
    # 1. 检查MySQL服务状态
    success, output = run_command("brew services list | grep mysql", "检查MySQL服务状态")
    if not success:
        print("❌ 无法检查MySQL服务状态")
        return False
    
    if "started" not in output:
        print("🔄 启动MySQL服务...")
        success, _ = run_command("brew services start mysql", "启动MySQL服务")
        if not success:
            print("❌ 无法启动MySQL服务")
            return False
        time.sleep(3)
    
    # 2. 尝试不同的连接方式
    connection_methods = [
        ("mysql -u root -e 'SELECT VERSION();'", "无密码连接"),
        ("mysql -u root -p -e 'SELECT VERSION();'", "需要密码连接"),
    ]
    
    mysql_connected = False
    for cmd, desc in connection_methods:
        success, output = run_command(cmd, desc)
        if success:
            print(f"✅ MySQL连接成功! 版本: {output.strip()}")
            mysql_connected = True
            break
        else:
            print(f"⚠️  {desc} - 失败，尝试下一种方法...")
    
    if not mysql_connected:
        print("❌ 无法连接到MySQL，请手动设置MySQL密码")
        print("📝 请运行以下命令设置密码:")
        print("   mysql_secure_installation")
        print("   或者")
        print("   mysql -u root")
        print("   ALTER USER 'root'@'localhost' IDENTIFIED BY 'password123';")
        return False
    
    # 3. 创建数据库
    success, _ = run_command("mysql -u root -e 'CREATE DATABASE IF NOT EXISTS stock_analysis_db;'", "创建数据库")
    if not success:
        print("❌ 无法创建数据库")
        return False
    
    # 4. 测试数据库连接
    success, _ = run_command("mysql -u root -e 'USE stock_analysis_db; SHOW TABLES;'", "测试数据库连接")
    if not success:
        print("❌ 无法连接到数据库")
        return False
    
    print("✅ MySQL数据库设置完成!")
    print("📝 数据库信息:")
    print("   主机: localhost")
    print("   端口: 3306")
    print("   数据库: stock_analysis_db")
    print("   用户: root")
    print("   密码: 你设置的密码")
    
    return True

if __name__ == "__main__":
    setup_mysql()

