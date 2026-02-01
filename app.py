#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI生成工具集 - Streamlit Cloud部署版本
"""

import streamlit as st

# 页面配置
st.set_page_config(
    page_title="AI生成工具集",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"  # 确保侧边栏默认展开
)

# 自定义CSS和JavaScript
st.markdown("""
<style>
    /* 隐藏默认的页面装饰 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 确保折叠按钮可见 */
    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    button[kind="header"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #262730;
        padding: 0;
        margin-bottom: 2rem;
    }
    
    /* 主内容区 */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* 标题样式 */
    h1 {
        color: #262730;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #262730;
        font-weight: 600;
        font-size: 1.75rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #262730;
        font-weight: 600;
        font-size: 1.25rem;
    }
    
    /* 卡片样式 */
    [data-testid="stExpander"] {
        border: 1px solid #e6e9ef;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* 按钮样式 */
    .stButton > button {
        width: 100%;
        border-radius: 0.375rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* 文件上传器样式 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #d0d5dd;
        border-radius: 0.5rem;
        padding: 2rem;
        background-color: #fafafa;
    }
    
    /* 成功/警告/错误消息 */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    /* 指标卡片 */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e6e9ef;
    }
    
    /* 选择框样式 */
    .stSelectbox, .stMultiSelect {
        border-radius: 0.375rem;
    }
    
    /* 间距优化 */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* 分隔线 */
    hr {
        margin: 2rem 0;
        border-color: #e6e9ef;
    }
</style>

<script>
// 强制显示侧边栏折叠按钮
function showCollapseButton() {
    // 查找折叠按钮
    const collapseBtn = document.querySelector('[data-testid="collapsedControl"]');
    const headerBtn = document.querySelector('button[kind="header"]');
    
    if (collapseBtn) {
        collapseBtn.style.display = 'flex';
        collapseBtn.style.visibility = 'visible';
        collapseBtn.style.opacity = '1';
    }
    
    if (headerBtn) {
        headerBtn.style.display = 'block';
        headerBtn.style.visibility = 'visible';
        headerBtn.style.opacity = '1';
    }
}

// 页面加载后执行
setTimeout(showCollapseButton, 100);
setTimeout(showCollapseButton, 500);
setTimeout(showCollapseButton, 1000);

// 监听DOM变化
const observer = new MutationObserver(showCollapseButton);
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# 侧边栏添加标题
with st.sidebar:
    st.markdown("## 🎯 功能导航")

# 主页内容
st.title("🎯 AI生成工具集")
st.markdown("### 让AI助力你的工作，从3小时到3分钟")

st.markdown("---")

# 功能卡片 - 只显示两个核心功能
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📋 版本UI走查")
    st.markdown("上传需求文档，自动生成专业的UI走查用例")
    if st.button("开始使用", key="btn1"):
        st.switch_page("pages/1_版本UI走查.py")

with col2:
    st.markdown("### 🏷️ 问题智能分类")
    st.markdown("上传问题表格，AI自动进行智能分类和统计")
    if st.button("开始使用", key="btn2"):
        st.switch_page("pages/2_问题分类.py")

# 可选：添加即将推出的功能预告
st.markdown("---")
st.markdown("### 🚀 即将推出")

with st.expander("更多功能开发中...", expanded=False):
    st.markdown("""
    **🔄 交叉走查任务**
    - 多版本对比分析
    - 智能任务分配
    - 团队协作管理
    
    **📊 数据分析报告**
    - 走查质量统计
    - 问题趋势分析
    - 团队效率评估
    
    **⚙️ 自定义配置**
    - 个性化走查规则
    - 团队标准模板
    - API集成配置
    
    *敬请期待后续版本更新！*
    """)
