"""
PyQt6 新增案例测试脚本
用于验证所有新增案例的依赖是否已正确安装
"""

import sys


def check_dependency(package_name, import_name=None):
    """检查依赖是否已安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name:20s} - 已安装")
        return True
    except ImportError as e:
        print(f"❌ {package_name:20s} - 未安装 ({e})")
        return False


def main():
    print("=" * 60)
    print("PyQt6 新增案例依赖检查")
    print("=" * 60)
    print()
    
    dependencies = [
        ("PyQt6", "PyQt6"),
        ("requests", "requests"),
        ("psutil", "psutil"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
    ]
    
    results = []
    for pkg_name, import_name in dependencies:
        result = check_dependency(pkg_name, import_name)
        results.append(result)
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✅ 所有依赖已安装，可以运行所有案例！")
    else:
        missing_count = results.count(False)
        print(f"⚠️  有 {missing_count} 个依赖未安装")
        print()
        print("请运行以下命令安装缺失的依赖：")
        print("pip install -r requirements.txt")
        print()
        print("或单独安装：")
        print("pip install requests psutil pandas openpyxl")
    
    print("=" * 60)
    print()
    
    # 显示案例列表
    print("📋 新增案例列表：")
    print()
    print("基础操作：")
    print("  1. 4 文件管理器.py")
    print("  2. 5 文本编辑器.py")
    print("  3. 6 图片浏览器.py")
    print()
    print("高级功能：")
    print("  1. 3 网络请求工具.py")
    print("  2. 4 定时任务调度器.py")
    print("  3. 5 数据导入导出工具.py")
    print()
    print("应用场景：")
    print("  1. 1 待办事项管理.py")
    print("  2. 2 系统监控面板.py")
    print("  3. 3 批量文件重命名.py")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
