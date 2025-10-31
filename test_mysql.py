#!/usr/bin/env python3
"""
MySQL连接测试脚本
"""
import subprocess
import sys

def test_mysql_connection():
    """测试MySQL连接"""
    print("🔍 测试MySQL连接...")
    
    # 测试无密码连接
    print("1. 测试无密码连接...")
    result = subprocess.run(["mysql", "-u", "root", "-e", "SELECT VERSION();"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 无密码连接成功!")
        print(f"MySQL版本: {result.stdout.strip()}")
        return True
    else:
        print("❌ 无密码连接失败")
        print(f"错误: {result.stderr.strip()}")
    
    # 测试需要密码连接
    print("\n2. 测试需要密码连接...")
    print("如果提示输入密码，请输入你设置的MySQL密码，或者按Ctrl+C取消")
    
    try:
        result = subprocess.run(["mysql", "-u", "root", "-p", "-e", "SELECT VERSION();"], 
                              capture_output=True, text=True, input="")
        if result.returncode == 0:
            print("✅ 密码连接成功!")
            return True
        else:
            print("❌ 密码连接失败")
            print(f"错误: {result.stderr.strip()}")
    except KeyboardInterrupt:
        print("\n⚠️  用户取消密码输入")
    
    return False

def setup_database():
    """设置数据库"""
    print("\n🗄️  设置数据库...")
    
    # 创建数据库
    result = subprocess.run(["mysql", "-u", "root", "-e", "CREATE DATABASE IF NOT EXISTS stock_analysis_db;"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 数据库创建成功!")
    else:
        print("❌ 数据库创建失败")
        print(f"错误: {result.stderr.strip()}")
        return False
    
    # 测试数据库连接
    result = subprocess.run(["mysql", "-u", "root", "-e", "USE stock_analysis_db; SHOW TABLES;"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 数据库连接测试成功!")
        return True
    else:
        print("❌ 数据库连接测试失败")
        print(f"错误: {result.stderr.strip()}")
        return False

if __name__ == "__main__":
    print("🚀 MySQL连接测试工具")
    print("=" * 40)
    
    if test_mysql_connection():
        if setup_database():
            print("\n✅ MySQL设置完成!")
            print("📝 现在可以运行: python init_db.py")
        else:
            print("\n❌ 数据库设置失败")
    else:
        print("\n❌ MySQL连接失败")
        print("\n📝 解决方案:")
        print("1. 运行: mysql_secure_installation")
        print("2. 或者运行: mysql -u root")
        print("3. 然后设置密码: ALTER USER 'root'@'localhost' IDENTIFIED BY 'password123';")

