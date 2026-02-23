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
import traceback

# 尝试导入AI生成器，如果失败则使用简化版本
try:
    from ai_generator import AIGenerator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    st.error("⚠️ AI生成器模块未找到，将只提供规则分类功能")

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
    .stDataFrame {
        border: 1px solid #e6e9ef;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def classify_by_keywords(problem_desc):
    """基于关键词的规则分类"""
    # 注意：功能完备性只包含"功能完全不存在"的情况，不包含"功能存在但不可用"的情况
    keyword_categories = {
        # 功能完备性：只匹配明确表示"功能完全不存在"的关键词
        # 注意：不包含"无法"、"不能"、"失效"等，因为这些通常表示功能存在但不可用（应归为系统可靠性）
        '功能完备性': ['完全没有', '缺少', '缺失', '没有该功能', '不支持', '未提供', '未设计', '未实现'],
        '信息清晰性': ['不清晰', '看不懂', '不明确', '混乱', '找不到', '隐蔽', '文案', '提示', '显示'],
        '任务高效性': ['操作', '步骤', '流程', '效率', '麻烦', '复杂', '慢', '体验', '繁琐'],
        # 系统可靠性：包含"功能存在但不可用"的情况
        '系统可靠性': ['报错', '错误', '异常', '故障', '崩溃', '卡顿', '加载', '性能', '超时', '无法', '不能', '失效', '不可用', '点击后', '操作后'],
        '一致性': ['不一致', '不统一', '不同', '样式', '格式', '颜色', '字体', '布局', '风格'],
    }
    
    # 关键词匹配（按优先级顺序检查）
    matched_category = None
    matched_keywords = []
    
    # 优先检查系统可靠性（因为"功能存在但不可用"的情况更常见）
    for category in ['系统可靠性', '信息清晰性', '任务高效性', '一致性', '功能完备性']:
        keywords = keyword_categories.get(category, [])
        for keyword in keywords:
            if keyword in problem_desc:
                matched_category = category
                matched_keywords.append(keyword)
                break
        if matched_category:
            break
    
    # 如果没有匹配到，使用默认分类
    if not matched_category:
        matched_category = '功能完备性'
        reason = "未匹配到明确关键词，使用默认分类"
    else:
        reason = f"基于关键词匹配: {', '.join(matched_keywords)}"
    
    return matched_category, reason

# 侧边栏配置
with st.sidebar:
    st.markdown("##### ⚙️ 配置选项")
    
    use_ai = st.checkbox("使用AI分类", value=AI_AVAILABLE, disabled=not AI_AVAILABLE)
    
    if use_ai and AI_AVAILABLE:
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
        use_ai_classification = use_ai and AI_AVAILABLE and 'ai_api_key' in st.session_state
        
        if not use_ai_classification:
            if not AI_AVAILABLE:
                st.warning("⚠️ AI模块不可用，将使用规则分类（准确性较低）")
            else:
                st.warning("⚠️ 未配置AI服务，将使用规则分类（准确性较低）")
        
        if st.button("🚀 开始智能分类", type="primary", use_container_width=True):
            with st.spinner("🤖 正在进行智能分类，请稍候..."):
                try:
                    # 内嵌分类手册（与正式手册保持一致）
                    classification_manual = """
# UI走查问题分类定义手册

## 1. 功能完备性

### 1.1 定义
评价产品是否具备用户对此类产品预期和同类竞品已经具备的核心功能，功能是否满足用户需求。

**关键边界说明**：
- **功能完备性仅关注"有没有这个功能"，不关注"这个功能当前是否可用/是否出故障"**
- **只有以下两种情况才归为功能完备性**：
  1. **竞品已有某功能，但本产品完全没有该功能**（功能在设计阶段就未规划，页面上完全找不到该功能）
  2. **本产品在设计上就缺少某类应有功能**（需求侧预期或行业通用功能缺失，功能在设计阶段就未规划）

**不属于功能完备性的情况（应归为系统可靠性）**：
- ❌ 页面上有该功能按钮/入口，但点击后无法使用 → **系统可靠性 - 系统运行稳定（功能无法正常使用）**
- ❌ 功能存在但报错、异常、失效 → **系统可靠性 - 系统运行稳定（功能无法正常使用）**
- ❌ 功能存在但因接口错误、资源问题导致不可用 → **系统可靠性 - 系统运行稳定（功能无法正常使用）**

**判断方法**：
1. **先判断功能是否存在**：页面上是否有该功能的按钮、入口、菜单项等？
   - 如果**完全没有**（设计上就没有）→ 功能完备性
   - 如果**有但不可用**（存在但出故障）→ 系统可靠性

## 2. 信息清晰性

### 2.1 定义
关注信息传递效率，即产品的页面结构、功能入口、文案、可视化图形等是否清晰明确，是否易于用户理解。

### 2.2 二级指标
- 页面结构清晰：导航结构、层级、分区等
- 功能入口易见：功能入口是否容易找到
- 图文清晰易懂：文案、图形、信息提示是否清晰

## 3. 任务高效性

### 3.1 定义
关注任务完成效率，即产品的操作步骤是否合理、操作方式是否符合认知习惯、是否提供明确的操作反馈。

### 3.2 二级指标
- 任务步骤合理：操作步骤是否冗余、流程是否复杂
- 操作符合认知：交互方式是否符合用户习惯
- 操作反馈明确：操作是否有及时准确的反馈

## 4. 系统可靠性

### 4.1 定义
关注系统整体性能，即系统的响应速度、稳定性、容错力和兼容性，确保系统在各种环境下都能提供持续且可靠的服务。

### 4.2 二级指标
- 系统响应迅速：加载时间、操作响应时间
- 系统运行稳定：功能是否正常可用、是否出现功能失效、报错、异常等
- 容错能力完备：防错、容错、纠错能力

**特别注意**：
- 只要"功能本来存在，但因为系统原因无法正常使用/结果明显异常"，均归入系统运行稳定（系统稳定性），而非功能完备性
- 功能存在但不可用、报错、异常、失效 → 系统可靠性 - 系统运行稳定

## 5. 一致性

### 5.1 定义
产品内部各元素、流程、交互方式和视觉样式的统一性，确保用户在使用产品时获得连贯一致的体验。

### 5.2 二级指标
- 信息传达一致：前后端信息、帮助文档与实际行为是否一致
- 操作流程一致：相同业务场景下的操作流程是否一致
- 交互方式一致：同类组件的交互方式是否一致
- 视觉样式一致：同类信息的视觉样式是否一致
"""
                    
                    # 准备分类结果
                    results = []
                    
                    if use_ai_classification:
                        # 使用AI分类
                        try:
                            generator = AIGenerator(
                                provider=st.session_state.get('ai_provider', 'deepseek'),
                                api_key=st.session_state.get('ai_api_key')
                            )
                            
                            # 批量处理问题
                            valid_problems = df[df["问题描述"].notna()]
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for idx, row in valid_problems.iterrows():
                                problem_desc = str(row["问题描述"])
                                
                                # 更新进度
                                progress = (len(results) + 1) / len(valid_problems)
                                progress_bar.progress(progress)
                                status_text.text(f"正在分类第 {len(results) + 1}/{len(valid_problems)} 个问题...")
                                
                                # AI分类
                                try:
                                    classification_result = generator.classify_problem(problem_desc, classification_manual)
                                    
                                    # 解析结果
                                    try:
                                        result_data = json.loads(classification_result)
                                        category = result_data.get('category', '功能完备性')
                                        reason = result_data.get('reason', '无法确定分类原因')
                                        reference = result_data.get('reference', '')
                                    except json.JSONDecodeError:
                                        # 如果JSON解析失败，使用文本解析
                                        category = '功能完备性'
                                        reason = '分类解析失败'
                                        reference = ''
                                        
                                        # 尝试从文本中提取信息
                                        if '功能完备性' in classification_result:
                                            category = '功能完备性'
                                        elif '信息清晰性' in classification_result:
                                            category = '信息清晰性'
                                        elif '任务高效性' in classification_result:
                                            category = '任务高效性'
                                        elif '系统可靠性' in classification_result:
                                            category = '系统可靠性'
                                        elif '一致性' in classification_result:
                                            category = '一致性'
                                        
                                        reason = f"AI分类结果: {classification_result[:50]}..."
                                    
                                except Exception as ai_error:
                                    # AI分类失败，使用规则分类
                                    category, reason = classify_by_keywords(problem_desc)
                                    reference = ''
                                
                                results.append({
                                    'index': idx,
                                    'category': category,
                                    'reason': reason,
                                    'reference': reference
                                })
                            
                            progress_bar.empty()
                            status_text.empty()
                            
                        except Exception as e:
                            st.error(f"AI分类初始化失败: {str(e)}")
                            # 回退到规则分类
                            use_ai_classification = False
                    
                    if not use_ai_classification:
                        # 使用规则分类（简单关键词匹配）
                        valid_problems = df[df["问题描述"].notna()]
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        for idx, row in valid_problems.iterrows():
                            problem_desc = str(row["问题描述"])
                            
                            # 更新进度
                            progress = (len(results) + 1) / len(valid_problems)
                            progress_bar.progress(progress)
                            status_text.text(f"正在分类第 {len(results) + 1}/{len(valid_problems)} 个问题...")
                            
                            # 关键词匹配
                            category, reason = classify_by_keywords(problem_desc)
                            
                            results.append({
                                'index': idx,
                                'category': category,
                                'reason': reason,
                                'reference': ''  # 规则分类没有参照依据
                            })
                        
                        progress_bar.empty()
                        status_text.empty()
                    
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
                    
                    # 计算统计信息
                    categories_count = df_result['问题分类'].value_counts().to_dict()
                    st.session_state['classification_stats'] = {
                        'total': len([r for r in results if r['category']]),
                        'categories': categories_count
                    }
                    
                    st.success(f"✅ 分类完成！共处理 {len(results)} 个问题")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 分类失败: {str(e)}")
                    with st.expander("🔍 查看错误详情"):
                        st.code(traceback.format_exc())
    
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
    if stats['categories']:
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
        if stats['categories']:
            category_df = pd.DataFrame(list(stats['categories'].items()), columns=['分类', '数量'])
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
