#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题智能分类 - Streamlit Cloud版本
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import io

from ai_generator import AIGenerator

st.set_page_config(page_title="问题分类", page_icon="🏷️", layout="wide")

# 自定义CSS
st.markdown("""
<style>
    .main .block-container {padding-top: 2rem; max-width: 1200px;}
    h1 {color: #262730; font-weight: 700; font-size: 2.5rem;}
    h2 {color: #262730; font-weight: 600; margin-top: 2rem;}
    .stButton > button {width: 100%; border-radius: 0.375rem; font-weight: 500;}
    [data-testid="stFileUploader"] {
        border: 2px dashed #d0d5dd;
        border-radius: 0.5rem;
        padding: 2rem;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# 侧边栏配置
with st.sidebar:
    st.markdown("##### ⚙️ 配置选项")
    
    use_ai = st.checkbox("使用AI分类", value=True)
    
    if use_ai:
        ai_provider = st.selectbox(
            "选择AI服务",
            ["deepseek", "openai"],
            index=0
        )
        
        api_key = st.text_input(
            f"{ai_provider.upper()} API Key",
            type="password",
            help=f"输入你的{ai_provider} API密钥"
        )
        
        if api_key:
            st.session_state['ai_api_key'] = api_key
            st.session_state['ai_provider'] = ai_provider
            st.success("✅ API Key已配置")

# 主界面
st.title("🏷️ 问题智能分类")
st.markdown("上传包含'问题描述'列的Excel表格，AI会依据分类手册进行智能分类")

# 使用指南
with st.expander("📖 使用指南", expanded=False):
    st.markdown("""
    ### 使用步骤
    
    1. **准备Excel文件**：确保表格中有'问题描述'列
    2. **上传文件**：支持 .xlsx, .xls, .csv 格式
    3. **预览数据**：检查数据是否正确读取
    4. **配置AI**：在侧边栏配置AI服务（可选）
    5. **开始分类**：点击'开始智能分类'按钮
    6. **查看结果**：预览分类结果和原因说明
    7. **下载结果**：下载包含分类结果的Excel文件
    
    ### 文件要求
    
    - **必须包含'问题描述'列**：系统会自动识别此列
    - **支持格式**：Excel (.xlsx, .xls) 或 CSV (.csv)
    - **编码要求**：CSV文件请使用UTF-8编码
    
    ### 分类依据
    
    系统会根据'UI走查问题分类定义手册'进行分类，包括：
    - 功能完备性
    - 信息清晰性  
    - 任务高效性
    - 系统可靠性
    - 一致性
    """)

st.markdown("---")

# 文件上传
st.markdown("## 📤 上传问题表格")
uploaded_file = st.file_uploader(
    "选择包含问题描述的Excel或CSV文件",
    type=['xlsx', 'xls', 'csv'],
    help="文件必须包含'问题描述'列"
)

if uploaded_file:
    try:
        # 读取文件
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ 文件读取成功: {uploaded_file.name}")
        
        # 检查是否包含'问题描述'列
        if "问题描述" not in df.columns:
            st.error("❌ 文件中未找到'问题描述'列，请检查表格格式")
            st.info("💡 提示：表格必须包含名为'问题描述'的列")
            
            # 显示当前列名
            st.markdown("**当前表格的列名：**")
            st.write(list(df.columns))
            st.stop()
        
        # 数据预览
        st.markdown("## 📊 数据预览")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总行数", len(df))
        with col2:
            st.metric("总列数", len(df.columns))
        with col3:
            st.metric("问题数量", len(df[df["问题描述"].notna()]))
        
        # 显示前几行数据
        st.markdown("**前5行数据：**")
        st.dataframe(df.head(), use_container_width=True)
        
        # 问题描述列统计
        problem_count = len(df[df["问题描述"].notna()])
        empty_count = len(df[df["问题描述"].isna()])
        
        if empty_count > 0:
            st.warning(f"⚠️ 发现 {empty_count} 行问题描述为空，将跳过这些行")
        
        st.markdown("---")
        
        # 分类按钮
        st.markdown("## 🤖 智能分类")
        
        if problem_count == 0:
            st.error("❌ 没有有效的问题描述数据")
            st.stop()
        
        # 检查AI配置
        use_ai_classification = use_ai and 'ai_api_key' in st.session_state
        
        if not use_ai_classification:
            st.warning("⚠️ 未配置AI服务，将使用规则分类（准确性较低）")
        
        if st.button("🚀 开始智能分类", type="primary", use_container_width=True):
            with st.spinner("🤖 正在进行智能分类，请稍候..."):
                try:
                    # 读取分类手册（内嵌版本）
                    classification_manual = """
# UI走查问题分类定义手册

## 1. 功能完备性
### 1.1 功能实现完整性
- 功能缺失或不完整
- 功能无法正常使用
- 功能实现与需求不符

### 1.2 业务逻辑正确性
- 业务流程错误
- 数据处理逻辑错误
- 权限控制问题

## 2. 信息清晰性
### 2.1 信息展示清晰
- 信息显示不清晰
- 信息缺失或不完整
- 信息层级混乱

### 2.2 功能入口易见
- 功能入口隐蔽
- 导航不清晰
- 操作路径不明确

## 3. 任务高效性
### 3.1 任务步骤合理
- 操作步骤冗余
- 任务流程复杂
- 缺少快捷操作

### 3.2 操作效率优化
- 响应速度慢
- 加载时间长
- 批量操作支持不足

## 4. 系统可靠性
### 4.1 错误处理完善
- 错误提示不清晰
- 异常处理不当
- 系统崩溃或卡死

### 4.2 系统运行稳定
- 功能不稳定
- 数据丢失
- 兼容性问题

## 5. 一致性
### 5.1 视觉一致性
- 界面风格不统一
- 颜色使用不一致
- 字体样式混乱

### 5.2 信息传达一致
- 术语使用不统一
- 信息表达不一致
- 交互方式不统一
"""
                    
                    # 准备分类结果
                    results = []
                    
                    if use_ai_classification:
                        # 使用AI分类
                        generator = AIGenerator(
                            provider=st.session_state.get('ai_provider', 'deepseek'),
                            api_key=st.session_state.get('ai_api_key')
                        )
                        
                        # 批量处理问题
                        valid_problems = df[df["问题描述"].notna()]
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in valid_problems.iterrows():
                            problem_desc = row["问题描述"]
                            
                            # 更新进度
                            progress = (len(results) + 1) / len(valid_problems)
                            progress_bar.progress(progress)
                            status_text.text(f"正在分类第 {len(results) + 1}/{len(valid_problems)} 个问题...")
                            
                            # AI分类
                            classification_result = generator.classify_problem(problem_desc, classification_manual)
                            
                            # 解析结果
                            try:
                                result_data = json.loads(classification_result)
                                category = result_data.get('category', '功能完备性')
                                reason = result_data.get('reason', '无法确定分类原因')
                                reference = result_data.get('reference', '')
                            except:
                                # 如果JSON解析失败，使用默认值
                                category = '功能完备性'
                                reason = '分类解析失败'
                                reference = ''
                            
                            results.append({
                                'index': idx,
                                'category': category,
                                'reason': reason,
                                'reference': reference
                            })
                        
                        progress_bar.empty()
                        status_text.empty()
                        
                    else:
                        # 使用规则分类（简单关键词匹配）
                        keyword_categories = {
                            '功能完备性': ['功能', '无法', '不能', '缺失', '不支持', '没有'],
                            '信息清晰性': ['不清晰', '看不懂', '不明确', '混乱', '找不到', '隐蔽', '文案', '提示'],
                            '任务高效性': ['操作', '步骤', '流程', '效率', '麻烦', '复杂', '慢', '体验'],
                            '系统可靠性': ['报错', '错误', '异常', '故障', '崩溃', '卡顿', '加载', '性能'],
                            '一致性': ['不一致', '不统一', '不同', '样式', '格式', '颜色', '字体', '布局'],
                        }
                        
                        valid_problems = df[df["问题描述"].notna()]
                        
                        for idx, row in valid_problems.iterrows():
                            problem_desc = str(row["问题描述"])
                            
                            # 关键词匹配
                            matched_category = '功能完备性'  # 默认分类
                            matched_keywords = []
                            
                            for category, keywords in keyword_categories.items():
                                for keyword in keywords:
                                    if keyword in problem_desc:
                                        matched_category = category
                                        matched_keywords.append(keyword)
                                        break
                                if matched_keywords:
                                    break
                            
                            reason = f"基于关键词匹配: {', '.join(matched_keywords)}" if matched_keywords else "未匹配到明确关键词"
                            
                            results.append({
                                'index': idx,
                                'category': matched_category,
                                'reason': reason,
                                'reference': ''  # 规则分类没有参照依据
                            })
                    
                    # 将结果添加到原始数据
                    df_result = df.copy()
                    df_result['问题分类'] = ''
                    df_result['分类原因'] = ''
                    df_result['参照依据'] = ''
                    
                    for result in results:
                        df_result.loc[result['index'], '问题分类'] = result['category']
                        df_result.loc[result['index'], '分类原因'] = result['reason']
                        df_result.loc[result['index'], '参照依据'] = result['reference']
                    
                    # 保存结果到session state
                    st.session_state['classification_result'] = df_result
                    st.session_state['classification_stats'] = {
                        'total': len(valid_problems),
                        'categories': df_result['问题分类'].value_counts().to_dict()
                    }
                    
                    st.success(f"✅ 分类完成！共处理 {len(results)} 个问题")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 分类失败: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ 文件读取失败: {str(e)}")
        st.info("💡 提示：请检查文件格式是否正确，CSV文件请使用UTF-8编码")

# 显示分类结果
if 'classification_result' in st.session_state:
    st.markdown("---")
    st.markdown("## 📊 分类结果")
    
    df_result = st.session_state['classification_result']
    stats = st.session_state['classification_stats']
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("处理总数", stats['total'])
    with col2:
        st.metric("分类数量", len(stats['categories']))
    with col3:
        if stats['categories']:
    most_common = max(stats['categories'].items(), key=lambda x: x[1])
    st.metric("最多类别", f"{most_common[0]} ({most_common[1]})")
else:
    st.metric("最多类别", "无数据")
    with col4:
        st.metric("输出格式", "Excel")
    
    # 分类统计图表
    st.markdown("### 📈 分类统计")
    category_df = pd.DataFrame(list(stats['categories'].items()), columns=['分类', '数量'])
    st.bar_chart(category_df.set_index('分类'))
    
    # 结果预览
    st.markdown("### 📋 结果预览")
    st.dataframe(df_result, use_container_width=True)
    
    # 下载功能
    st.markdown("### 📥 下载结果")
    
    # 生成Excel文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, sheet_name='分类结果', index=False)
        category_df.to_excel(writer, sheet_name='统计汇总', index=False)
    
    excel_data = output.getvalue()
    
    # 文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"问题分类结果_{timestamp}.xlsx"
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 下载Excel文件",
            data=excel_data,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 重新分类", use_container_width=True):
            # 清除结果
            if 'classification_result' in st.session_state:
                del st.session_state['classification_result']
            if 'classification_stats' in st.session_state:
                del st.session_state['classification_stats']
            st.rerun()

# 页脚
st.markdown("---")
st.caption("💡 提示：AI分类基于'UI走查问题分类定义手册'，准确性取决于问题描述的清晰度")
