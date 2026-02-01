#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI走查用例生成助手 - Streamlit Cloud版本
"""

import streamlit as st
import os
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import io

from ai_generator import AIGenerator
from module_recognizer import ModuleRecognizer
from module_selector import ModuleSelector
from test_case_coordinator import TestCaseCoordinator
from session_state_utils import SessionStateManager

# 配置页面
st.set_page_config(
    page_title="UI走查用例生成助手",
    page_icon="🎨",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
    /* 一级导航（页面链接）- 最大字号 */
    [data-testid="stSidebarNav"] a {
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    
    /* 二级标题（配置选项、用例类型）- 中等字号 */
    [data-testid="stSidebar"] h5 {
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #666 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p strong {
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    
    /* 三级选项（单选按钮、复选框）- 最小字号 */
    [data-testid="stSidebar"] label[data-baseweb="radio"] {
        font-size: 12px !important;
    }
    
    [data-testid="stSidebar"] label[data-baseweb="checkbox"] {
        font-size: 12px !important;
    }
    
    /* 其他文字 */
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# 初始化Session State
SessionStateManager.init_session_state()

# 标题
st.title("🎨 UI走查用例生成助手")
st.caption("上传需求文档，一键生成UI走查用例，提升走查效率")

# 侧边栏配置
with st.sidebar:
    st.markdown("##### ⚙️ 配置选项")
    
    st.markdown("**用例类型**")
    case_type = st.radio(
        "选择类型",
        options=["标准UI走查", "竞品对标走查"],
        label_visibility="collapsed"
    )
    
    st.session_state['case_type'] = case_type
    
    st.markdown("---")
    
    use_ai = st.checkbox("使用AI生成", value=False)
    
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
tab1, tab2, tab3 = st.tabs(["📤 上传文档", "📊 生成结果", "✅ 在线检验"])

with tab1:
    st.header("上传需求文档")
    
    # 使用指南
    with st.expander("📖 使用指南", expanded=False):
        st.markdown("""
        ### 快速开始
        
        **第一步：上传文档**
        - 支持格式：Markdown (.md)、文本文件 (.txt)、Word文档 (.docx)、PDF文档 (.pdf)
        - 支持同时上传多个文档，系统会自动合并处理
        - 文档应包含清晰的标题结构（如 ## 标题）
        
        **第二步：识别模块**
        - 点击"模块/页面识别"按钮
        - 系统会自动识别文档中的所有模块和页面
        
        **第三步：选择模块**
        - 勾选需要生成用例的模块
        - 可使用搜索功能快速定位模块
        
        **第四步：选择建议选项（可选）**
        - 根据测试需求选择建议的测试类别
        
        **第五步：生成用例**
        - 点击"生成UI走查用例"按钮
        
        **第六步：下载结果**
        - 在"生成结果"标签页中预览和下载生成的用例文件
        """)
    
    # 文件上传
    uploaded_files = st.file_uploader(
        "选择需求文档（最多3个文件）",
        type=['md', 'txt', 'docx', 'pdf'],
        accept_multiple_files=True,
        help="支持格式：Markdown (.md)、文本文件 (.txt)、Word文档 (.docx)、PDF文档 (.pdf)"
    )
    
    # 文件读取函数
    def read_file_content(uploaded_file):
        """读取单个文件的内容"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        try:
            if file_extension == 'docx':
                from docx import Document
                import io
                doc = Document(io.BytesIO(uploaded_file.read()))
                content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            elif file_extension == 'pdf':
                import pdfplumber
                import io
                pdf_bytes = io.BytesIO(uploaded_file.read())
                content = ''
                with pdfplumber.open(pdf_bytes) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + '\n'
                
                if not content.strip():
                    return None, "PDF文件中未找到可提取的文本内容"
            elif file_extension in ['md', 'txt']:
                content = uploaded_file.read().decode('utf-8')
            else:
                return None, f"不支持的文件格式: {file_extension}"
            
            return content, None
        except Exception as e:
            return None, f"文件读取失败: {str(e)}"
    
    # 处理上传的文件
    if uploaded_files:
        if len(uploaded_files) > 3:
            st.error(f"❌ 最多只能上传3个文件，当前选择了 {len(uploaded_files)} 个文件")
            st.stop()
        
        all_content = ''
        file_names = []
        has_error = False
        
        st.info(f"📁 已选择 {len(uploaded_files)} 个文件")
        
        for i, uploaded_file in enumerate(uploaded_files, 1):
            file_names.append(uploaded_file.name)
            content, error = read_file_content(uploaded_file)
            
            if error:
                st.error(f"❌ {uploaded_file.name}: {error}")
                has_error = True
                continue
            
            if i > 1:
                all_content += '\n\n' + '='*80 + '\n\n'
            
            all_content += f'# 文档 {i}: {uploaded_file.name}\n\n'
            all_content += content
            st.success(f"✅ 已读取: {uploaded_file.name}")
        
        if has_error:
            st.stop()
        
        if not all_content.strip():
            st.error("❌ 所有文件都没有可提取的内容")
            st.stop()
        
        # 存储到session state
        SessionStateManager.set_uploaded_document(
            all_content, 
            f"{len(file_names)}个文档", 
            'multiple'
        )
        
        st.divider()
        
        # 显示预览
        st.subheader("📄 文档内容预览")
        preview_length = min(1000, len(all_content))
        preview_text = all_content[:preview_length]
        if len(all_content) > preview_length:
            preview_text += "\n\n... (内容过长，仅显示前1000字符)"
        
        st.text_area("合并后的文档内容", preview_text, height=300)
    
    # 检查是否有已上传的内容
    elif SessionStateManager.get_uploaded_content():
        content = SessionStateManager.get_uploaded_content()
        st.info("📄 已加载文档内容")
        
        preview_length = min(1000, len(content))
        preview_text = content[:preview_length]
        if len(content) > preview_length:
            preview_text += "\n\n... (内容过长，仅显示前1000字符)"
        
        st.text_area("文档预览", preview_text, height=200)
    
    # 模块识别
    if SessionStateManager.get_uploaded_content():
        st.divider()
        
        if not SessionStateManager.is_modules_recognized():
            if st.button("🔍 模块/页面识别", type="primary", use_container_width=True):
                content = SessionStateManager.get_uploaded_content()
                
                if not content or len(content.strip()) < 10:
                    st.error("❌ 文档内容过短或为空，无法识别模块")
                    st.stop()
                
                with st.spinner("🔍 正在分析文档结构，识别模块中..."):
                    try:
                        use_ai_gen = use_ai and 'ai_api_key' in st.session_state
                        case_type = st.session_state.get('case_type', '标准UI走查')
                        
                        if use_ai_gen:
                            st.info("💡 使用AI智能识别模式")
                            generator = AIGenerator(
                                provider=st.session_state.get('ai_provider', 'deepseek'),
                                api_key=st.session_state.get('ai_api_key'),
                                case_type=case_type
                            )
                            recognizer = ModuleRecognizer(ai_generator=generator)
                        else:
                            st.info("💡 使用规则识别模式")
                            recognizer = ModuleRecognizer()
                        
                        modules = recognizer.recognize_modules(content, 'md')
                        
                        if not modules:
                            st.warning("⚠️ 未识别到任何模块，请检查文档格式")
                            st.stop()
                        
                        SessionStateManager.set_modules(modules)
                        st.success(f"✅ 识别成功！共识别到 {len(modules)} 个模块")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ 识别失败: {str(e)}")
        else:
            if st.button("🔄 重新识别", use_container_width=True):
                SessionStateManager.clear_recognition_data()
                st.rerun()
        
        # 模块选择界面
        if SessionStateManager.is_modules_recognized():
            st.divider()
            st.subheader("📋 模块选择")
            
            selector = ModuleSelector()
            modules = SessionStateManager.get_modules()
            case_type = st.session_state.get('case_type', '标准UI走查')
            
            if len(modules) > 10:
                with st.expander(f"📦 模块列表 ({len(modules)} 个)", expanded=True):
                    selector.render_module_list(modules, case_type=case_type)
            else:
                selector.render_module_list(modules, case_type=case_type)
            
            st.divider()
            
            # 生成用例
            selected_modules = selector.get_selected_modules()
            selected_categories = selector.get_selected_categories()
            
            generate_disabled = len(selected_modules) == 0
            
            if generate_disabled:
                st.warning("⚠️ 请至少选择一个模块后再生成用例")
            else:
                st.success(f"✅ 已选择 {len(selected_modules)} 个模块，准备生成用例")
                if case_type == '标准UI走查' and selected_categories:
                    st.info(f"🎯 已选择建议选项: {', '.join(selected_categories)}")
            
            if st.button("🚀 生成UI走查用例", type="primary", use_container_width=True, disabled=generate_disabled):
                with st.spinner("🚀 正在生成用例，请稍候..."):
                    try:
                        use_ai_gen = use_ai and 'ai_api_key' in st.session_state
                        case_type = st.session_state.get('case_type', '标准UI走查')
                        
                        if use_ai_gen:
                            st.info(f"💡 使用AI生成模式（{case_type}）")
                            generator = AIGenerator(
                                provider=st.session_state.get('ai_provider', 'deepseek'),
                                api_key=st.session_state.get('ai_api_key'),
                                case_type=case_type
                            )
                        else:
                            st.info(f"💡 使用模板生成模式（{case_type}）")
                            generator = AIGenerator(case_type=case_type)
                        
                        coordinator = TestCaseCoordinator(ai_generator=generator)
                        
                        content = SessionStateManager.get_uploaded_content()
                        all_cases = coordinator.generate_cases_for_selected(
                            content=content,
                            selected_modules=selected_modules,
                            selected_categories=selected_categories
                        )
                        
                        if not all_cases:
                            st.error("❌ 生成失败：未能生成任何用例")
                            st.stop()
                        
                        # 添加用例编号
                        case_type = st.session_state.get('case_type', '标准UI走查')
                        prefix = 'CP-TC' if case_type == '竞品对标走查' else 'UI-TC'
                        type_label = '竞品对标UI走查用例' if case_type == '竞品对标走查' else 'UI走查用例'
                        
                        for i, case in enumerate(all_cases, 1):
                            case['用例编号'] = f'{prefix}{i:03d}'
                            case['是否通过'] = '待测试'
                            case['截图/备注'] = ''
                        
                        # 生成CSV数据
                        import csv
                        from io import StringIO
                        
                        output = StringIO()
                        headers = ['用例编号', '页面/模块', '检查点', '设计原则', '检查项', 
                                  '优先级', '预期结果/设计标准', '是否通过', '截图/备注']
                        
                        writer = csv.DictWriter(output, fieldnames=headers)
                        writer.writeheader()
                        writer.writerows(all_cases)
                        
                        csv_data = output.getvalue()
                        
                        # 保存到session state
                        SessionStateManager.set_generated_result(csv_data, all_cases)
                        
                        st.success(f"✅ 生成完成！共生成 {len(all_cases)} 个用例，涉及 {len(selected_modules)} 个模块")
                        st.info(f"📋 用例类型: {case_type}")
                        st.toast("用例生成成功！", icon="✅")
                        
                    except Exception as e:
                        st.error(f"❌ 生成失败: {str(e)}")

with tab2:
    st.header("生成结果")
    
    if SessionStateManager.get_generated_file():
        all_cases = SessionStateManager.get_all_cases()
        
        # 显示统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("用例总数", len(all_cases))
        with col2:
            modules = set(case.get('页面/模块', '') for case in all_cases)
            st.metric("模块数量", len(modules))
        with col3:
            st.metric("输出格式", "CSV")
        
        st.divider()
        
        # 下载CSV文件
        st.subheader("📥 下载CSV文件")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        case_type = st.session_state.get('case_type', '标准UI走查')
        type_label = '竞品对标UI走查用例' if case_type == '竞品对标走查' else 'UI走查用例'
        default_name = f"{type_label}-{timestamp}"
        
        custom_filename = st.text_input(
            "自定义文件名",
            value=default_name,
            help="修改文件名后点击下载按钮"
        )
        
        csv_data = SessionStateManager.get_generated_file()
        
        st.download_button(
            label="📥 下载CSV文件",
            data=csv_data,
            file_name=f"{custom_filename}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.divider()
        
        # 数据预览
        st.subheader("📊 数据预览")
        df = pd.DataFrame(all_cases)
        st.dataframe(df, use_container_width=True)
        
    else:
        st.info("👈 请先在左侧上传文档并生成用例")

with tab3:
    st.header("在线检验")
    
    if not SessionStateManager.get_all_cases():
        st.info("👈 请先在左侧上传文档并生成用例")
        st.markdown("""
        ### 📋 在线检验功能说明
        
        在线检验功能允许你直接在界面中进行UI走查检验：
        
        - 🔄 **模块切换**: 在不同模块之间切换查看用例
        - ✅ **状态标记**: 为每个用例标记检验状态（待检验/通过/不通过）
        - 📊 **进度统计**: 实时查看检验进度和通过率
        - 📥 **导出结果**: 导出包含检验状态的完整报告
        """)
    else:
        # 初始化检验状态
        if 'verification_status' not in st.session_state:
            st.session_state['verification_status'] = {}
            for case in SessionStateManager.get_all_cases():
                case_id = case.get('用例编号', '')
                if case_id:
                    st.session_state['verification_status'][case_id] = '待检验'
        
        # 按模块分组用例
        cases_by_module = {}
        for case in SessionStateManager.get_all_cases():
            module = case.get('页面/模块', '未分类')
            if module not in cases_by_module:
                cases_by_module[module] = []
            cases_by_module[module].append(case)
        
        modules = list(cases_by_module.keys())
        
        # 计算整体统计
        total_cases = len(SessionStateManager.get_all_cases())
        status_counts = {'待检验': 0, '通过': 0, '不通过': 0}
        for status in st.session_state['verification_status'].values():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        verified_count = status_counts['通过'] + status_counts['不通过']
        pass_rate = (status_counts['通过'] / verified_count * 100) if verified_count > 0 else 0
        
        # 显示整体统计
        st.subheader("📊 整体检验进度")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("总用例数", total_cases)
        with col2:
            st.metric("已检验", verified_count)
        with col3:
            st.metric("通过", status_counts['通过'])
        with col4:
            st.metric("不通过", status_counts['不通过'])
        with col5:
            st.metric("通过率", f"{pass_rate:.1f}%")
        
        # 进度条
        progress = verified_count / total_cases if total_cases > 0 else 0
        st.progress(progress, text=f"检验进度: {verified_count}/{total_cases}")
        
        st.divider()
        
        # 模块选择
        if len(modules) > 1:
            st.subheader("🔄 选择模块")
            selected_module = st.radio(
                "选择要检验的模块",
                modules,
                horizontal=True,
                label_visibility="collapsed"
            )
        else:
            selected_module = modules[0] if modules else None
        
        if selected_module:
            module_cases = cases_by_module[selected_module]
            
            # 模块统计
            module_status_counts = {'待检验': 0, '通过': 0, '不通过': 0}
            for case in module_cases:
                case_id = case.get('用例编号', '')
                status = st.session_state['verification_status'].get(case_id, '待检验')
                module_status_counts[status] = module_status_counts.get(status, 0) + 1
            
            module_verified = module_status_counts['通过'] + module_status_counts['不通过']
            module_pass_rate = (module_status_counts['通过'] / module_verified * 100) if module_verified > 0 else 0
            
            st.markdown(f"### 📋 {selected_module}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("模块用例数", len(module_cases))
            with col2:
                st.metric("已检验", module_verified)
            with col3:
                st.metric("通过", module_status_counts['通过'])
            with col4:
                st.metric("通过率", f"{module_pass_rate:.1f}%")
            
            st.divider()
            
            # 用例列表
            st.subheader("📝 用例列表")
            
            for idx, case in enumerate(module_cases, 1):
                case_id = case.get('用例编号', '')
                current_status = st.session_state['verification_status'].get(case_id, '待检验')
                
                # 状态颜色
                if current_status == '通过':
                    status_color = "🟢"
                elif current_status == '不通过':
                    status_color = "🔴"
                else:
                    status_color = "⚪"
                
                priority = case.get('优先级', '中')
                priority_badge = "🔴" if priority == '高' else "🟡" if priority == '中' else "🟢"
                
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"{status_color} {priority_badge} **{case_id}** {case.get('检查点', '')} · {case.get('设计原则', '')}")
                    st.caption(f"**检查项**: {case.get('检查项', '')} | **预期结果**: {case.get('预期结果/设计标准', '')}")
                
                with col2:
                    new_status = st.selectbox(
                        "状态",
                        ['待检验', '通过', '不通过'],
                        index=['待检验', '通过', '不通过'].index(current_status),
                        key=f"status_{case_id}",
                        label_visibility="collapsed"
                    )
                    
                    if new_status != current_status:
                        st.session_state['verification_status'][case_id] = new_status
                        st.rerun()
                
                if idx < len(module_cases):
                    st.markdown("---")
        
        # 导出检验结果
        st.divider()
        st.subheader("📥 导出检验结果")
        
        if st.button("📥 导出全部检验结果", type="primary", use_container_width=True):
            import csv
            from io import StringIO
            
            output = StringIO()
            headers = ['用例编号', '页面/模块', '检查点', '设计原则', '检查项', 
                      '优先级', '预期结果/设计标准', '检验状态']
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            
            for case in SessionStateManager.get_all_cases():
                case_id = case.get('用例编号', '')
                case_copy = case.copy()
                case_copy['检验状态'] = st.session_state['verification_status'].get(case_id, '待检验')
                writer.writerow(case_copy)
            
            csv_data = output.getvalue()
            st.download_button(
                label="⬇️ 下载完整检验结果CSV",
                data=csv_data,
                file_name=f"UI走查检验结果-{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# 页脚
st.divider()
st.caption("💡 提示：使用AI生成可以获得更智能、更全面的用例")