# UV Publish 发布指南

本指南介绍如何使用 UV 命令行工具发布包到 Test PyPI 和正式 PyPI。

## 前置要求

- Python 3.10+
- UV 工具已安装
- PyPI/Test PyPI 账号和 API Token

## 获取 API Token

### Test PyPI
1. 访问 https://test.pypi.org/manage/account/token/
2. 创建新的 API Token，选择 "Entire account" 作用域
3. 复制生成的 Token（格式：`pypi-...`）

### 正式 PyPI
1. 访问 https://pypi.org/manage/account/token/
2. 创建新的 API Token，选择 "Entire account" 作用域
3. 复制生成的 Token（格式：`pypi-...`）

## 发布步骤

### 1. 构建包
```bash
uv build
```

### 2. 发布到 Test PyPI
```bash
# 使用 Token
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-your-testpypi-token

# 或使用环境变量
$env:UV_PUBLISH_TOKEN="pypi-your-testpypi-token"
uv publish --publish-url https://test.pypi.org/legacy/
```

### 3. 验证 Test PyPI
```bash
pip install -i https://test.pypi.org/simple/ smart-financial-mcp
python -c "import smart_financial_mcp; print(smart_financial_mcp.__version__)"
```

### 4. 发布到正式 PyPI
```bash
# 使用 Token
uv publish --token pypi-your-pypi-token

# 或使用环境变量
$env:UV_PUBLISH_TOKEN="pypi-your-pypi-token"
uv publish
```

### 5. 验证正式 PyPI
```bash
pip install smart-financial-mcp
python -c "import smart_financial_mcp; print(smart_financial_mcp.__version__)"
```

## 完整发布示例

```bash
# 构建
uv build

# 发布到 Test PyPI
uv publish --publish-url https://test.pypi.org/legacy/ --token pypi-your-testpypi-token

# 验证
pip install -i https://test.pypi.org/simple/ smart-financial-mcp

# 发布到正式 PyPI  
uv publish --token pypi-your-pypi-token

# 验证
pip install smart-financial-mcp
```