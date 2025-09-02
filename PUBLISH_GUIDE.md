# 自动化发布指南

这是一个完整的自动化UV发布到PyPI的脚本，让您能够轻松发布tushare_MCP包。

## 功能特性

✅ **版本管理** - 自动递增版本号（patch/minor/major）
✅ **代码质量检查** - Black代码格式化、isort导入排序、Flake8规范检查  
✅ **包构建** - 使用现代UV工具构建包
✅ **双环境发布** - 支持TestPyPI（测试）和PyPI（生产）
✅ **Git集成** - 自动创建Git标签和提交
✅ **彩色输出** - 用户友好的控制台界面
✅ **错误处理** - 完善的错误提示和恢复机制

## 使用方法

### 1. 基本命令

```bash
# 查看帮助
python scripts\publish.py --help

# 只运行代码质量检查
python scripts\publish.py --check

# 只构建包（不发布）
python scripts\publish.py --build

# 发布到TestPyPI（测试环境）
python scripts\publish.py --test

# 发布到PyPI（生产环境）
python scripts\publish.py --release
```

### 2. 版本管理

```bash
# 递增补丁版本（0.1.0 -> 0.1.1）并发布到PyPI
python scripts\publish.py --version patch

# 递增次要版本（0.1.0 -> 0.2.0）并发布到PyPI  
python scripts\publish.py --version minor

# 递增主要版本（0.1.0 -> 1.0.0）并发布到PyPI
python scripts\publish.py --version major
```

### 3. 跳过选项

```bash
# 跳过代码质量检查
python scripts\publish.py --release --skip-checks

# 跳过Git操作
python scripts\publish.py --release --skip-git

# 跳过所有检查
python scripts\publish.py --release --skip-checks --skip-git
```

## 发布准备

### 1. 配置PyPI API Token

在发布前，您需要配置PyPI API Token：

**方法1: 环境变量**
```bash
# 设置PyPI Token
$env:UV_PUBLISH_PYPI_TOKEN="your-pypi-api-token"

# 设置TestPyPI Token  
$env:UV_PUBLISH_TESTPYPI_TOKEN="your-testpypi-api-token"
```

**方法2: UV配置**
```bash
# UV会自动提示您输入Token
uv publish --help
```

### 2. 获取API Token

- **PyPI**: 访问 https://pypi.org/manage/account/token/ 
- **TestPyPI**: 访问 https://test.pypi.org/manage/account/token/

创建API Token时：
- Token名称：选择一个描述性名称
- 作用域：选择"Entire account"或特定项目

### 3. 检查项目配置

确保以下文件正确配置：

- `pyproject.toml` - 项目元数据和依赖
- `tushare_mcp/__init__.py` - 版本号定义
- `README.md` - 项目说明
- `.env` - 环境变量（如需要）

## 典型发布流程

### 首次发布流程

```bash
# 1. 检查代码质量
python scripts\publish.py --check

# 2. 修复代码问题（如果有）
uv run black tushare_mcp/
uv run isort tushare_mcp/

# 3. 先发布到测试环境
python scripts\publish.py --test

# 4. 测试安装和功能
pip install -i https://test.pypi.org/simple/ tushare-mcp

# 5. 确认无误后发布到生产环境
python scripts\publish.py --release
```

### 日常更新流程

```bash
# 直接递增版本并发布（推荐）
python scripts\publish.py --version patch

# 或者分步操作
python scripts\publish.py --check
python scripts\publish.py --build  
python scripts\publish.py --release
```

## 常见问题

### Q: 为什么代码质量检查失败？
A: 常见原因包括：
- 代码行太长（>79字符）
- 未使用的导入
- 格式不规范

解决方案：
```bash
uv run black tushare_mcp/    # 自动格式化
uv run isort tushare_mcp/    # 排序导入
```

### Q: 发布时提示认证失败？
A: 检查API Token配置：
- 确认Token有效且未过期
- 检查环境变量设置
- 确认Token作用域权限

### Q: 如何撤销发布？
A: PyPI不支持删除已发布的版本，但可以：
- 发布新的修复版本
- 在PyPI上标记版本为"yanked"

### Q: 构建失败怎么办？
A: 检查：
- `pyproject.toml`配置是否正确
- 依赖版本是否兼容
- Python版本要求是否满足

## 脚本特性

### 安全特性
- 🔒 发布前检查Git状态
- 🔒 代码质量强制检查  
- 🔒 测试环境优先验证
- 🔒 详细的确认提示

### 智能特性  
- 🧠 自动版本号管理
- 🧠 依赖冲突检测
- 🧠 错误自动恢复
- 🧠 彩色状态输出

### 灵活特性
- ⚡ 模块化操作选项
- ⚡ 可跳过各个检查步骤
- ⚡ 支持多种发布场景
- ⚡ 丰富的命令行参数

## 维护建议

1. **定期更新依赖**：`uv sync --upgrade`
2. **保持代码质量**：每次提交前运行 `--check`
3. **测试先行**：生产发布前先用 `--test` 验证
4. **版本管理**：使用语义化版本控制
5. **文档同步**：及时更新README和CHANGELOG

---

📝 **注意**: 这个脚本已经为您的tushare_MCP项目量身定制，包含了完整的现代Python包发布工作流程。