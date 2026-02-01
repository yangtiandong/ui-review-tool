# UI走查工具包 - Streamlit Cloud部署版

这是UI走查工具包的Streamlit Cloud部署版本，专门为云端部署优化，支持通过GitHub直接部署到Streamlit Cloud。

## 功能特性

### 🎯 核心功能
- **AI生成UI走查用例**：基于13大设计原则，智能生成CSV格式的UI走查用例
- **竞品对标用例生成**：基于10大竞品对标原则，生成针对性的对标检查用例
- **问题智能分类**：基于5大分类体系，自动分类UI走查发现的问题
- **Excel多Sheet导出**：支持将分类结果导出为多Sheet的Excel文件

### 🚀 技术特点
- **云端部署**：专为Streamlit Cloud优化，支持GitHub一键部署
- **智能AI引擎**：集成DeepSeek等多种AI模型，提供智能化用例生成
- **多格式支持**：支持PDF、Word、Excel、Markdown等多种文档格式
- **实时处理**：在线生成和处理，无需本地安装

## 快速开始

### 在线使用
1. 访问部署的Streamlit Cloud应用
2. 选择功能模块（版本UI走查/问题分类/交叉走查）
3. 上传需求文档或设计稿
4. 配置生成参数
5. 获取生成结果

### 本地运行
```bash
# 克隆仓库
git clone <your-repo-url>
cd streamlit_cloud_deploy

# 安装依赖
pip install -r requirements.txt

# 运行应用
streamlit run app.py
```

## 部署到Streamlit Cloud

### 前置条件
- GitHub账号
- Streamlit Cloud账号（可用GitHub登录）

### 部署步骤
1. **准备代码仓库**
   - 将此目录内容推送到GitHub仓库
   - 确保包含所有必要文件

2. **连接Streamlit Cloud**
   - 访问 [share.streamlit.io](https://share.streamlit.io)
   - 使用GitHub账号登录
   - 点击"New app"

3. **配置部署**
   - Repository: 选择你的GitHub仓库
   - Branch: main (或你的主分支)
   - Main file path: app.py
   - App URL: 自定义应用URL

4. **部署应用**
   - 点击"Deploy!"
   - 等待部署完成（通常需要2-5分钟）

### 环境变量配置
如果使用AI功能，需要在Streamlit Cloud中配置以下环境变量：
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `OPENAI_API_KEY`: OpenAI API密钥（可选）

## 目录结构

```
streamlit_cloud_deploy/
├── app.py                              # 主应用入口
├── pages/                              # 页面模块
│   ├── 1_版本UI走查.py                 # UI走查用例生成
│   └── 2_问题分类.py                   # 问题分类功能
├── .streamlit/                         # Streamlit配置
│   └── config.toml                     # 应用配置
├── requirements.txt                    # Python依赖
├── AI生成UI走查用例规则.md             # UI走查规则文档
├── AI生成竞品对标UI走查用例规则.md      # 竞品对标规则文档
├── UI走查问题分类定义手册.md           # 问题分类手册
└── 核心模块文件...                     # 业务逻辑模块
```

## 核心模块

### AI生成模块 (ai_generator.py)
- 支持多种AI模型（DeepSeek、OpenAI等）
- 智能解析需求文档
- 生成结构化UI走查用例

### 模块识别 (module_recognizer.py)
- 自动识别文档中的功能模块
- 支持多种文档格式解析
- 智能提取关键信息

### 问题分类 (test_case_coordinator.py)
- 基于5大分类体系
- 智能问题识别和分类
- 支持批量处理

### 会话管理 (session_state_utils.py)
- Streamlit会话状态管理
- 数据持久化
- 用户交互状态保持

## 使用指南

### 1. 版本UI走查
1. 上传需求文档或设计稿
2. 选择AI模型和生成参数
3. 配置UI走查原则
4. 生成CSV格式用例文件
5. 下载结果文件

### 2. 问题分类
1. 上传包含问题描述的Excel文件
2. 选择分类模式（智能分类/手动分类）
3. 配置分类参数
4. 执行分类处理
5. 导出分类结果

### 3. 交叉走查（如果支持）
1. 上传多个版本的走查结果
2. 配置对比参数
3. 执行交叉分析
4. 生成对比报告

## 配置说明

### AI模型配置
支持以下AI模型：
- **DeepSeek-V2**: 推荐用于中文场景，理解能力强
- **DeepSeek-Coder**: 适合技术文档分析
- **OpenAI GPT**: 通用性强，需要API密钥

### 文件格式支持
- **输入格式**: PDF, DOCX, XLSX, MD, TXT
- **输出格式**: CSV, XLSX (多Sheet)
- **最大文件大小**: 200MB

### 性能优化
- 使用Streamlit缓存机制
- 异步处理大文件
- 智能内存管理

## 常见问题

### Q: 部署失败怎么办？
A: 检查以下项目：
- requirements.txt是否包含所有依赖
- 文件路径是否正确
- 是否有语法错误

### Q: AI功能不可用？
A: 确认：
- API密钥是否正确配置
- 网络连接是否正常
- API配额是否充足

### Q: 文件上传失败？
A: 检查：
- 文件大小是否超限（200MB）
- 文件格式是否支持
- 文件是否损坏

### Q: 生成结果不理想？
A: 尝试：
- 调整AI模型参数
- 优化输入文档质量
- 使用更详细的需求描述

## 技术支持

### 问题反馈
如遇到问题，请提供：
- 错误信息截图
- 操作步骤描述
- 输入文件示例（脱敏后）

### 功能建议
欢迎提出改进建议：
- 新功能需求
- 用户体验优化
- 性能改进建议

## 更新日志

### v2.0.0 (Streamlit Cloud版)
- ✨ 适配Streamlit Cloud部署
- 🚀 优化云端性能
- 📱 改进移动端体验
- 🔧 简化配置流程

### v1.x.x (本地版)
- 基础功能实现
- 本地文件处理
- 命令行工具

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 贡献指南

欢迎贡献代码和建议：
1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

---

**注意**: 这是专为Streamlit Cloud优化的版本，如需本地部署版本，请参考主项目目录。