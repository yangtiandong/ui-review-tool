# -*- coding: utf-8 -*-
"""
UI走查工具包 - Streamlit Cloud版本
主页面
"""

import streamlit as st
import os

# 页面配置
st.set_page_config(
    page_title="UI走查工具包",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .feature-title {
        color: #333;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        color: #666;
        line-height: 1.6;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 主页内容
def main():
    # 标题
    st.markdown("""
    <div class="main-header">
        <h1>🔍 UI走查工具包</h1>
        <p>专业的UI走查用例生成和问题分类工具</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能介绍
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📋 版本UI走查</div>
            <div class="feature-desc">
                • 智能识别功能模块<br>
                • 自动生成走查用例<br>
                • 支持CSV和Excel多Sheet格式<br>
                • AI增强用例生成
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🎯 问题分类</div>
            <div class="feature-desc">
                • Excel问题智能分类<br>
                • 基于5大分类维度<br>
                • AI自动分析和归类<br>
                • 生成分类原因和参照依据
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🔄 交叉走查</div>
            <div class="feature-desc">
                • 多版本对比分析<br>
                • 交叉验证功能<br>
                • 问题追踪管理<br>
                • 团队协作支持
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">⚡ 快速开始</div>
            <div class="feature-desc">
                • 选择左侧功能模块<br>
                • 上传需求文档或Excel<br>
                • 一键生成结果<br>
                • 下载生成的文件
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 统计信息
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">8</div>
            <div class="stat-label">UI走查原则</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">5</div>
            <div class="stat-label">问题分类维度</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">100+</div>
            <div class="stat-label">用例模板</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">AI</div>
            <div class="stat-label">智能增强</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 使用说明
    st.markdown("---")
    st.markdown("### 📖 使用说明")
    
    with st.expander("🚀 快速开始", expanded=True):
        st.markdown("""
        1. **选择功能**：从左侧导航选择需要的功能模块
        2. **上传文件**：根据功能要求上传相应的文档或Excel文件
        3. **配置选项**：设置生成参数和AI选项
        4. **生成结果**：点击生成按钮，等待处理完成
        5. **下载文件**：下载生成的用例文件或分类结果
        """)
    
    with st.expander("🔧 功能详解"):
        st.markdown("""
        **版本UI走查**
        - 支持Markdown、Word、PDF格式的需求文档
        - 自动识别功能模块和页面结构
        - 基于8大UI走查原则生成用例
        - 支持AI增强生成更精准的用例
        
        **问题分类**
        - 上传包含"问题描述"列的Excel文件
        - 基于UI走查问题分类定义手册进行智能分类
        - 5大分类维度：功能完备性、信息清晰性、任务高效性、系统可靠性、一致性
        - 生成分类结果、分类原因和参照依据
        
        **交叉走查**
        - 多版本功能对比
        - 问题追踪和管理
        - 团队协作功能
        """)
    
    with st.expander("💡 使用技巧"):
        st.markdown("""
        - **需求文档**：结构清晰的文档能生成更好的用例
        - **AI功能**：需要配置API Key，推荐使用DeepSeek（性价比高）
        - **Excel格式**：超过50个用例或3个模块时自动使用Excel多Sheet格式
        - **问题分类**：确保Excel中有"问题描述"列
        - **文件下载**：生成的文件会自动下载到浏览器默认下载目录
        """)
    
    # 版本信息
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>UI走查工具包 v2.0</p>
            <p>Powered by Streamlit Cloud</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()