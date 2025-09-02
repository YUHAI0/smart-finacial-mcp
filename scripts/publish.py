#!/usr/bin/env python3
"""
自动化 UV 发布到 PyPI 的脚本

该脚本提供以下功能：
1. 版本管理（自动递增版本号）
2. 代码质量检查
3. 构建包
4. 发布到 PyPI（支持测试和生产环境）
5. Git 标签管理

使用方法:
    python scripts/publish.py --help                 # 查看帮助
    python scripts/publish.py --check               # 只进行代码检查
    python scripts/publish.py --build               # 只构建包
    python scripts/publish.py --test                # 发布到 TestPyPI
    python scripts/publish.py --release             # 发布到 PyPI
    python scripts/publish.py --version patch       # 递增补丁版本并发布
    python scripts/publish.py --version minor       # 递增次要版本并发布
    python scripts/publish.py --version major       # 递增主要版本并发布
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

# 导入dotenv用于读取环境变量
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class Colors:
    """控制台颜色常量"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_step(message: str, color: str = Colors.BLUE):
    """打印步骤信息"""
    print(f"{color}{Colors.BOLD}🔄 {message}{Colors.END}")


def print_success(message: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}{Colors.BOLD}✅ {message}{Colors.END}")


def print_error(message: str):
    """打印错误信息"""
    print(f"{Colors.RED}{Colors.BOLD}❌ {message}{Colors.END}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠️  {message}{Colors.END}")


def print_info(message: str):
    """打印信息"""
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")


def run_command(command: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """运行命令"""
    print_info(f"执行命令: {command}")
    
    try:
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                check=check, 
                capture_output=True, 
                text=True
            )
        else:
            result = subprocess.run(command, shell=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {command}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"stdout: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"stderr: {e.stderr}")
        raise


def load_environment_variables():
    """加载环境变量"""
    env_file = Path(".env")
    
    if env_file.exists():
        if DOTENV_AVAILABLE:
            load_dotenv(env_file)
            print_success("已加载 .env 文件中的环境变量")
        else:
            print_warning("未安装 python-dotenv，无法加载 .env 文件")
            print_info("请手动设置环境变量或安装: pip install python-dotenv")
    else:
        print_warning("未找到 .env 文件")
        print_info("请创建 .env 文件并设置 PyPI Token")


def check_pypi_tokens():
    """检查PyPI Token是否已配置"""
    pypi_token = os.getenv('UV_PUBLISH_PYPI_TOKEN')
    testpypi_token = os.getenv('UV_PUBLISH_TESTPYPI_TOKEN')
    
    if pypi_token and pypi_token != 'your-pypi-token-here':
        print_success("PyPI Token 已配置")
    else:
        print_warning("PyPI Token 未配置或为默认值")
    
    if testpypi_token and testpypi_token != 'your-testpypi-token-here':
        print_success("TestPyPI Token 已配置")
    else:
        print_warning("TestPyPI Token 未配置或为默认值")
    
    return bool(pypi_token and pypi_token != 'your-pypi-token-here'), bool(testpypi_token and testpypi_token != 'your-testpypi-token-here')


def check_uv_installed():
    """检查 uv 是否已安装"""
    try:
        result = run_command("uv --version", capture_output=True)
        print_success(f"UV 已安装: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print_error("UV 未安装，请先安装 UV")
        print_info("安装方法:")
        print_info("  Windows: winget install --id=astral-sh.uv  -e")
        print_info("  macOS: brew install uv")
        print_info("  Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def get_current_version() -> str:
    """从 __init__.py 获取当前版本"""
    init_file = Path("smart_finacial_mcp/__init__.py")
    if not init_file.exists():
        raise FileNotFoundError("找不到 smart_finacial_mcp/__init__.py 文件")
    
    content = init_file.read_text(encoding='utf-8')
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    
    if not version_match:
        raise ValueError("无法在 __init__.py 中找到版本信息")
    
    return version_match.group(1)


def parse_version(version: str) -> Tuple[int, int, int]:
    """解析版本号"""
    match = re.match(r'(\d+)\.(\d+)\.(\d+)', version)
    if not match:
        raise ValueError(f"无效的版本格式: {version}")
    
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def increment_version(current_version: str, increment_type: str) -> str:
    """递增版本号"""
    major, minor, patch = parse_version(current_version)
    
    if increment_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif increment_type == "minor":
        minor += 1
        patch = 0
    elif increment_type == "patch":
        patch += 1
    else:
        raise ValueError(f"无效的版本递增类型: {increment_type}")
    
    return f"{major}.{minor}.{patch}"


def update_version(new_version: str):
    """更新版本号"""
    init_file = Path("smart_finacial_mcp/__init__.py")
    content = init_file.read_text(encoding='utf-8')
    
    # 更新版本号
    new_content = re.sub(
        r'(__version__\s*=\s*["\'])[^"\']+(["\'])',
        rf'\g<1>{new_version}\g<2>',
        content
    )
    
    init_file.write_text(new_content, encoding='utf-8')
    print_success(f"版本号已更新为: {new_version}")


def check_git_status():
    """检查 Git 状态"""
    try:
        result = run_command("git status --porcelain", capture_output=True)
        if result.stdout.strip():
            print_warning("工作目录有未提交的更改:")
            print(result.stdout)
            
            response = input("是否继续？(y/N): ")
            if response.lower() != 'y':
                print_info("操作已取消")
                sys.exit(1)
    except subprocess.CalledProcessError:
        print_warning("无法检查 Git 状态，可能不是 Git 仓库")


def run_quality_checks():
    """运行代码质量检查"""
    print_step("运行代码质量检查")
    
    # 检查是否有开发依赖
    print_info("检查开发依赖...")
    try:
        # 使用 uv 安装开发依赖
        run_command("uv sync --extra dev")
    except subprocess.CalledProcessError:
        print_warning("无法安装开发依赖，跳过代码质量检查")
        return
    
    checks = [
        ("Black 代码格式检查", "uv run black --check smart_finacial_mcp/ --diff"),
        ("isort 导入排序检查", "uv run isort --check-only smart_finacial_mcp/ --diff"),
        ("Flake8 代码规范检查", "uv run flake8 smart_finacial_mcp/"),
    ]
    
    failed_checks = []
    
    for check_name, command in checks:
        print_info(f"运行 {check_name}...")
        try:
            run_command(command)
            print_success(f"{check_name} 通过")
        except subprocess.CalledProcessError:
            failed_checks.append(check_name)
            print_error(f"{check_name} 失败")
    
    if failed_checks:
        print_error(f"以下检查失败: {', '.join(failed_checks)}")
        print_info("建议运行以下命令修复问题:")
        print_info("  uv run black smart_finacial_mcp/")
        print_info("  uv run isort smart_finacial_mcp/")
        
        response = input("是否继续发布？(y/N): ")
        if response.lower() != 'y':
            print_info("发布已取消")
            sys.exit(1)
    else:
        print_success("所有代码质量检查通过")


def build_package():
    """构建包"""
    print_step("构建包")
    
    # 清理旧的构建文件
    print_info("清理旧的构建文件...")
    for path in ["build/", "dist/", "*.egg-info/"]:
        run_command(f"rm -rf {path}", check=False)
    
    # 使用 uv 构建
    run_command("uv build")
    print_success("包构建完成")


def publish_to_pypi(test: bool = False):
    """发布到 PyPI"""
    if test:
        print_step("发布到 TestPyPI")
        repository = "testpypi"
        url = "https://test.pypi.org"
        token_env = "UV_PUBLISH_TESTPYPI_TOKEN"
        publish_url = "https://test.pypi.org/legacy/"
    else:
        print_step("发布到 PyPI")
        repository = "pypi"
        url = "https://pypi.org"
        token_env = "UV_PUBLISH_PYPI_TOKEN"
        publish_url = None  # 使用默认PyPI URL
    
    # 检查Token是否配置
    token = os.getenv(token_env)
    if not token or token in ['your-pypi-token-here', 'your-testpypi-token-here']:
        config_info = f"""
请在 .env 文件中配置 {repository.upper()} API Token:

在 .env 文件中添加:
    {token_env}=your-api-token

获取 API Token:
    访问 {url}/manage/account/token/ 创建 API Token

Token 格式示例:
    pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""
        
        print_info(config_info)
        
        response = input(f"是否继续发布（将手动输入Token）？(y/N): ")
        if response.lower() != 'y':
            print_info("发布已取消")
            sys.exit(1)
        
        # 手动发布模式
        if publish_url:
            run_command(f"uv publish --publish-url {publish_url}")
        else:
            run_command("uv publish")
    else:
        print_success(f"{repository.upper()} Token 已配置，开始发布...")
        
        # 使用环境变量中的Token发布
        if publish_url:
            run_command(f"uv publish --publish-url {publish_url}")
        else:
            run_command("uv publish")
    
    print_success(f"成功发布到 {repository.upper()}")


def create_git_tag(version: str):
    """创建 Git 标签"""
    print_step(f"创建 Git 标签: v{version}")
    
    try:
        # 提交版本更新
        run_command("git add smart_finacial_mcp/__init__.py")
        run_command(f'git commit -m "Bump version to {version}"')
        
        # 创建标签
        run_command(f"git tag -a v{version} -m \"Release version {version}\"")
        
        print_success(f"Git 标签 v{version} 创建成功")
        print_info("记住推送标签到远程仓库: git push origin v{version}")
        
    except subprocess.CalledProcessError:
        print_error("创建 Git 标签失败")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="自动化发布到 PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "--check", 
        action="store_true", 
        help="只运行代码质量检查"
    )
    parser.add_argument(
        "--build", 
        action="store_true", 
        help="只构建包"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="发布到 TestPyPI"
    )
    parser.add_argument(
        "--release", 
        action="store_true", 
        help="发布到 PyPI"
    )
    parser.add_argument(
        "--version", 
        choices=["patch", "minor", "major"], 
        help="递增版本号类型"
    )
    parser.add_argument(
        "--skip-checks", 
        action="store_true", 
        help="跳过代码质量检查"
    )
    parser.add_argument(
        "--skip-git", 
        action="store_true", 
        help="跳过 Git 操作"
    )
    
    args = parser.parse_args()
    
    # 检查是否在项目根目录
    if not Path("pyproject.toml").exists():
        print_error("请在项目根目录运行此脚本")
        sys.exit(1)
    
    # 检查 uv 是否安装
    if not check_uv_installed():
        sys.exit(1)
    
    # 加载环境变量
    load_environment_variables()
    
    # 检查Token配置状态
    pypi_configured, testpypi_configured = check_pypi_tokens()
    
    try:
        # 获取当前版本
        current_version = get_current_version()
        print_info(f"当前版本: {current_version}")
        
        # 版本管理
        new_version = current_version
        if args.version:
            new_version = increment_version(current_version, args.version)
            print_info(f"新版本: {new_version}")
            update_version(new_version)
        
        # Git 状态检查
        if not args.skip_git:
            check_git_status()
        
        # 代码质量检查
        if args.check:
            run_quality_checks()
            return
        
        if not args.skip_checks and not args.build:
            run_quality_checks()
        
        # 构建包
        if args.build or args.test or args.release or args.version:
            build_package()
        
        if args.build:
            return
        
        # 发布
        if args.test:
            publish_to_pypi(test=True)
        elif args.release or args.version:
            publish_to_pypi(test=False)
        
        # 创建 Git 标签
        if (args.release or args.version) and not args.skip_git:
            create_git_tag(new_version)
        
        if args.test or args.release or args.version:
            print_success("🎉 发布完成!")
            
    except KeyboardInterrupt:
        print_info("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print_error(f"发布失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()