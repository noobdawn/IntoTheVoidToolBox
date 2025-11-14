"""
IntoTheVoidToolBox 打包脚本
使用 PyInstaller 将 Python 项目打包为独立的可执行文件
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# 项目配置
APP_NAME = "IntoTheVoidToolBox"
MAIN_SCRIPT = "start.py"
VERSION = "0.1.0"

# 颜色输出（Windows PowerShell 支持）
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(message):
    """打印步骤信息"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}[步骤] {message}{Colors.END}")

def print_success(message):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def clean_build_dirs():
    """清理之前的构建目录"""
    print_step("清理旧的构建文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = [f'{APP_NAME}.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"  删除目录: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            print(f"  删除文件: {file_name}")
            os.remove(file_name)
    
    print_success("清理完成")

def check_dependencies():
    """检查依赖是否已安装"""
    print_step("检查依赖...")
    
    try:
        import PyQt5
        print_success("PyQt5 已安装")
    except ImportError:
        print_error("PyQt5 未安装")
        return False
    
    try:
        import qfluentwidgets
        print_success("PyQt-Fluent-Widgets 已安装")
    except ImportError:
        print_error("PyQt-Fluent-Widgets 未安装")
        return False
    
    try:
        result = subprocess.run(
            ['pyinstaller', '--version'], 
            check=True, 
            capture_output=True, 
            text=True
        )
        version = result.stdout.strip()
        print_success(f"PyInstaller 已安装 (版本: {version})")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    return True

def build_executable():
    """构建可执行文件"""
    print_step("开始构建可执行文件...")
    
    # PyInstaller 命令参数
    cmd = [
        'pyinstaller',
        '--name=' + APP_NAME,
        '--windowed',              # 不显示控制台窗口（GUI 应用）
        '--onedir',                # 打包成一个文件夹（推荐）
        '--noconfirm',             # 覆盖输出目录而不询问
        
        # 添加数据文件
        '--add-data=assets;assets',
        '--add-data=data;data',
        
        # 隐藏导入（确保这些模块被包含）
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=qfluentwidgets',
        '--hidden-import=pynput',
        '--hidden-import=numpy',
        
        # 排除不需要的模块以减小体积
        '--exclude-module=matplotlib',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        '--exclude-module=tkinter',
        '--exclude-module=tools',  # 排除 tools 文件夹（仅用于开发的工具脚本）
        
        # 清理临时文件
        '--clean',
        
        # 主脚本
        MAIN_SCRIPT
    ]
    
    # 显示完整命令
    print(f"\n执行命令:")
    print(f"  {' '.join(cmd)}\n")
    
    try:
        # 执行打包命令
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # 实时输出
        for line in process.stdout:
            print(f"  {line.rstrip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print_success("构建成功！")
            dist_path = os.path.join(os.getcwd(), 'dist', APP_NAME)
            print(f"\n可执行文件位于: {dist_path}")
            return True
        else:
            print_error("构建失败！")
            return False
            
    except Exception as e:
        print_error(f"构建过程中发生错误: {str(e)}")
        return False

def create_release_package():
    """创建发布包"""
    print_step("创建发布包...")
    
    dist_dir = os.path.join('dist', APP_NAME)
    if not os.path.exists(dist_dir):
        print_error("找不到构建的文件")
        return False
    
    # 创建 release 文件夹
    release_dir = 'release'
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    # 复制构建的文件
    release_app_dir = os.path.join(release_dir, APP_NAME)
    print(f"  复制文件到: {release_app_dir}")
    shutil.copytree(dist_dir, release_app_dir)
    
    # 复制额外的文件
    files_to_copy = {
        'README.md': '中文说明文档',
        'README_en.md': '英文说明文档',
        'LICENSE': '许可证文件'
    }
    
    for file, desc in files_to_copy.items():
        if os.path.exists(file):
            shutil.copy(file, release_app_dir)
            print(f"  ✓ 复制 {desc}: {file}")
        else:
            print_warning(f"文件不存在，跳过: {file}")
    
    # 创建使用说明
    usage_file = os.path.join(release_app_dir, '使用说明.txt')
    with open(usage_file, 'w', encoding='utf-8') as f:
        f.write(f"""《驱入虚空》工具箱 v{VERSION}
{'=' * 50}

运行方法：
  双击 {APP_NAME}.exe 启动程序

系统要求：
  - Windows 10/11
  - 无需安装 Python 环境

注意事项：
  1. 首次运行可能被 Windows Defender 拦截，请允许运行
  2. 请勿删除程序目录下的其他文件
  3. assets 和 data 文件夹包含程序必需的资源文件

问题反馈：
  GitHub: https://github.com/noobdawn/IntoTheVoidToolBox/issues

{'=' * 50}
感谢使用！
""")
    print_success(f"创建使用说明: {usage_file}")
    
    # 计算文件夹大小
    total_size = sum(
        os.path.getsize(os.path.join(dirpath, filename))
        for dirpath, _, filenames in os.walk(release_app_dir)
        for filename in filenames
    )
    size_mb = total_size / (1024 * 1024)
    
    print_success(f"发布包创建完成: {release_dir}")
    print(f"  总大小: {size_mb:.2f} MB")
    print(f"\n下一步：")
    print(f"  1. 测试 {release_app_dir}\\{APP_NAME}.exe")
    print(f"  2. 将 {release_dir} 文件夹压缩为 .zip 文件")
    print(f"  3. 上传到 GitHub Releases")
    
    return True

def print_banner():
    """打印横幅"""
    banner = f"""
{'=' * 60}
    IntoTheVoidToolBox 打包脚本
    版本: {VERSION}
{'=' * 60}
"""
    print(Colors.BOLD + banner + Colors.END)

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        print_error("\n依赖检查失败，请先安装所需依赖")
        print("运行以下命令安装：")
        print("  pip install -r requirements.txt")
        print("  pip install pyinstaller")
        sys.exit(1)
    
    # 清理旧文件
    clean_build_dirs()
    
    # 构建可执行文件
    if not build_executable():
        print_error("\n构建失败！")
        sys.exit(1)
    
    # 创建发布包
    if not create_release_package():
        print_error("\n创建发布包失败！")
        sys.exit(1)
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 60}")
    print("    构建完成！")
    print(f"{'=' * 60}{Colors.END}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n发生未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
