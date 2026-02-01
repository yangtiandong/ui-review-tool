# Streamlit Cloud 部署指南

本文档详细说明如何将UI走查工具包部署到Streamlit Cloud。

## 部署概览

### 部署架构
```
GitHub Repository → Streamlit Cloud → 在线应用
```

### 部署优势
- ✅ 零服务器维护成本
- ✅ 自动SSL证书
- ✅ 全球CDN加速
- ✅ 自动扩容
- ✅ GitHub集成部署

## 前置准备

### 1. 账号准备
- **GitHub账号**: 用于代码托管
- **Streamlit Cloud账号**: 可使用GitHub账号登录

### 2. 代码准备
确保以下文件存在且正确：
- `app.py` - 主应用文件
- `requirements.txt` - 依赖列表
- `pages/` - 页面模块目录
- `.streamlit/config.toml` - 配置文件

### 3. 依赖检查
验证 `requirements.txt` 包含所有必要依赖：
```txt
streamlit>=1.28.0
pandas>=1.5.0
openpyxl>=3.1.0
python-docx>=0.8.11
PyPDF2>=3.0.0
requests>=2.28.0
```

## 详细部署步骤

### 步骤1: 准备GitHub仓库

1. **创建新仓库**
   ```bash
   # 在GitHub上创建新仓库，例如: ui-review-tool
   ```

2. **上传代码**
   ```bash
   # 初始化本地仓库
   cd streamlit_cloud_deploy
   git init
   
   # 添加远程仓库
   git remote add origin https://github.com/yourusername/ui-review-tool.git
   
   # 提交代码
   git add .
   git commit -m "Initial commit: Streamlit Cloud deployment"
   git push -u origin main
   ```

3. **验证文件结构**
   确保GitHub仓库包含以下结构：
   ```
   your-repo/
   ├── app.py
   ├── requirements.txt
   ├── pages/
   │   ├── 1_版本UI走查.py
   │   └── 2_问题分类.py
   ├── .streamlit/
   │   └── config.toml
   └── 其他模块文件...
   ```

### 步骤2: 连接Streamlit Cloud

1. **访问Streamlit Cloud**
   - 打开 [share.streamlit.io](https://share.streamlit.io)
   - 点击 "Sign in with GitHub"

2. **授权GitHub**
   - 允许Streamlit访问你的GitHub仓库
   - 选择授权范围（建议选择特定仓库）

### 步骤3: 创建新应用

1. **点击"New app"**
   - 在Streamlit Cloud控制台点击"New app"按钮

2. **配置应用信息**
   ```
   Repository: yourusername/ui-review-tool
   Branch: main
   Main file path: app.py
   App URL: ui-review-tool (自定义)
   ```

3. **高级设置（可选）**
   - Python version: 3.9+ (推荐3.11)
   - 环境变量配置（如需要AI功能）

### 步骤4: 环境变量配置

如果使用AI功能，需要配置API密钥：

1. **在应用设置中添加环境变量**
   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key
   OPENAI_API_KEY=your_openai_api_key (可选)
   ```

2. **API密钥获取方式**
   - DeepSeek: 访问 [platform.deepseek.com](https://platform.deepseek.com)
   - OpenAI: 访问 [platform.openai.com](https://platform.openai.com)

### 步骤5: 部署应用

1. **点击"Deploy!"**
   - 系统开始自动部署
   - 部署过程通常需要2-5分钟

2. **监控部署状态**
   - 查看实时日志
   - 检查依赖安装进度
   - 确认应用启动成功

## 部署后配置

### 1. 应用测试

部署完成后，进行功能测试：

1. **基础功能测试**
   - 访问应用URL
   - 测试页面导航
   - 验证文件上传功能

2. **AI功能测试**（如已配置）
   - 测试用例生成功能
   - 验证AI模型响应
   - 检查生成结果质量

3. **文件处理测试**
   - 上传不同格式文件
   - 测试文件解析功能
   - 验证结果下载

### 2. 性能优化

1. **缓存配置**
   ```python
   # 在代码中使用Streamlit缓存
   @st.cache_data
   def load_data(file):
       return process_file(file)
   ```

2. **内存优化**
   - 及时清理大文件
   - 使用流式处理
   - 避免全局变量

### 3. 监控设置

1. **应用监控**
   - 在Streamlit Cloud控制台查看应用状态
   - 监控资源使用情况
   - 查看访问日志

2. **错误追踪**
   - 配置错误通知
   - 定期检查应用日志
   - 监控API调用状态

## 常见部署问题

### 问题1: 依赖安装失败

**症状**: 部署时提示包安装失败
**解决方案**:
```bash
# 检查requirements.txt格式
# 确保版本号正确
streamlit>=1.28.0
pandas>=1.5.0

# 避免使用本地路径依赖
# 使用PyPI包名
```

### 问题2: 文件路径错误

**症状**: 应用启动后找不到模块文件
**解决方案**:
```python
# 使用相对路径
import os
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, 'module.py')

# 或使用绝对导入
from . import module
```

### 问题3: 内存超限

**症状**: 应用运行时内存不足
**解决方案**:
```python
# 优化文件处理
def process_large_file(file):
    # 分块处理
    for chunk in pd.read_csv(file, chunksize=1000):
        yield process_chunk(chunk)

# 及时清理内存
del large_dataframe
gc.collect()
```

### 问题4: API调用失败

**症状**: AI功能无法正常工作
**解决方案**:
1. 检查环境变量配置
2. 验证API密钥有效性
3. 确认API配额充足
4. 添加错误处理机制

## 更新和维护

### 自动部署

Streamlit Cloud支持自动部署：
1. **推送代码到GitHub**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **自动触发部署**
   - Streamlit Cloud检测到代码变更
   - 自动重新部署应用
   - 通常需要1-3分钟完成

### 手动重启

如需手动重启应用：
1. 访问Streamlit Cloud控制台
2. 找到对应应用
3. 点击"Reboot app"

### 版本管理

建议使用分支管理：
```bash
# 开发分支
git checkout -b develop
# 开发完成后合并到主分支
git checkout main
git merge develop
```

## 安全考虑

### 1. API密钥安全
- 使用环境变量存储敏感信息
- 定期轮换API密钥
- 监控API使用情况

### 2. 文件上传安全
```python
# 文件类型验证
allowed_types = ['.pdf', '.docx', '.xlsx']
if file.type not in allowed_types:
    st.error("不支持的文件类型")

# 文件大小限制
max_size = 200 * 1024 * 1024  # 200MB
if file.size > max_size:
    st.error("文件过大")
```

### 3. 数据隐私
- 不在日志中记录敏感信息
- 及时清理临时文件
- 使用HTTPS传输

## 成本优化

### Streamlit Cloud限制
- **免费版限制**:
  - 1个私有应用
  - 无限公开应用
  - 1GB内存
  - 1个CPU核心

- **付费版优势**:
  - 更多私有应用
  - 更高资源配额
  - 优先支持

### 优化建议
1. **代码优化**: 减少内存使用
2. **缓存策略**: 合理使用缓存
3. **资源监控**: 定期检查资源使用

## 故障排除

### 调试工具
1. **Streamlit Cloud日志**
   - 实时查看应用日志
   - 检查错误信息

2. **本地调试**
   ```bash
   # 本地运行测试
   streamlit run app.py
   ```

3. **健康检查**
   ```python
   # 添加健康检查端点
   def health_check():
       return {"status": "healthy", "timestamp": datetime.now()}
   ```

### 联系支持
如遇到无法解决的问题：
1. 查看Streamlit官方文档
2. 访问Streamlit社区论坛
3. 提交GitHub Issue

---

**部署完成后，你的UI走查工具包将可以通过互联网访问，为团队提供便捷的在线服务！**