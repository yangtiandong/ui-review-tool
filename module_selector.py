#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块选择器UI组件
管理模块选择状态和UI渲染
"""

import streamlit as st
from typing import List
from module import Module
from session_state_utils import SessionStateManager


class ModuleSelector:
    """模块选择器类"""
    
    def __init__(self):
        """初始化选择器"""
        self._init_session_state()
    
    def _init_session_state(self):
        """
        初始化Session State
        确保所有必需的状态都已初始化
        """
        SessionStateManager.init_session_state()
    
    def render_module_list(self, modules: List[Module], case_type: str = '标准UI走查') -> None:
        """
        渲染模块选择列表
        
        Args:
            modules: 模块列表
            case_type: 用例类型（'标准UI走查' 或 '竞品对标走查'）
        """
        if not modules:
            st.warning("未识别到任何模块")
            return
        
        # 显示模块总数和提示
        st.markdown(f"📋 识别到 **{len(modules)}** 个模块")
        st.caption("💡 勾选需要生成用例的模块")
        
        st.divider()
        
        # 搜索框
        search_keyword = self._render_search_box()
        
        # 过滤模块
        filtered_modules = self._filter_modules(modules, search_keyword)
        
        if not filtered_modules:
            st.info("没有匹配的模块")
            return
        
        # 获取当前选中的模块ID集合
        selected_ids = SessionStateManager.get_selected_module_ids()
        
        # 使用容器为模块列表和建议选项添加统一的视觉边界
        with st.container(border=True):
            st.markdown("### 📦 模块列表")
            
            # 获取当前建议选项状态
            categories = SessionStateManager.get_suggested_categories()
            
            # 使用两列布局优化模块显示
            col1, col2 = st.columns(2)
            
            for idx, module in enumerate(filtered_modules):
                # 为每个模块创建唯一的key
                checkbox_key = f"module_checkbox_{module.id}"
                
                # 检查模块是否被选中
                is_selected = module.id in selected_ids
                
                # 交替放置在两列中
                target_col = col1 if idx % 2 == 0 else col2
                
                with target_col:
                    # 构建显示文本
                    label_text = f"**{module.name}**"
                    help_text = module.description if module.description else None
                    
                    # 使用checkbox
                    checked = st.checkbox(
                        label=label_text,
                        value=is_selected,
                        key=checkbox_key,
                        help=help_text
                    )
                    
                    # 实时更新选中状态
                    if checked and module.id not in selected_ids:
                        selected_ids.add(module.id)
                        SessionStateManager.set_selected_module_ids(selected_ids)
                    elif not checked and module.id in selected_ids:
                        selected_ids.discard(module.id)
                        SessionStateManager.set_selected_module_ids(selected_ids)
            
            # 添加自定义模块功能
            st.divider()
            with st.expander("➕ 添加自定义模块", expanded=False):
                st.caption("💡 如果模块过于复杂，可以手动拆分成多个子模块")
                
                new_module_name = st.text_input(
                    "模块名称",
                    key="new_module_name_input",
                    placeholder="例如：订单列表、订单详情"
                )
                
                col_add, col_clear = st.columns([3, 1])
                with col_add:
                    if st.button("添加模块", use_container_width=True, type="primary"):
                        if new_module_name and new_module_name.strip():
                            self._add_custom_module(new_module_name.strip(), modules)
                        else:
                            st.error("请输入模块名称")
                
                with col_clear:
                    if st.button("清空", use_container_width=True):
                        # 清空输入框（通过rerun实现）
                        st.rerun()
            
            # 只在标准UI走查模式下显示建议选项
            if case_type == '标准UI走查':
                st.divider()
                st.markdown("### 🎯 建议选项")
                st.markdown("💡 选择以下选项可以让AI生成更有针对性的测试用例")
                
                # 建议选项说明
                category_descriptions = {
                    '全局页面': '包含导航、头部、底部等通用组件的测试',
                    '场景流程': '包含多步骤操作流程的测试',
                    '异常场景': '包含错误处理、边界条件的测试',
                    '上下游验证': '包含数据流转、接口调用的测试'
                }
                
                # 使用两列布局优化建议选项显示
                col1, col2 = st.columns(2)
                
                items = list(category_descriptions.items())
                for idx, (category_name, description) in enumerate(items):
                    checkbox_key = f"category_{category_name}"
                    is_selected = categories.get(category_name, False)
                    
                    # 交替放置在两列中
                    target_col = col1 if idx % 2 == 0 else col2
                    
                    with target_col:
                        checked = st.checkbox(
                            label=f"**{category_name}**",
                            value=is_selected,
                            key=checkbox_key,
                            on_change=self._on_category_toggle,
                            args=(category_name,),
                            help=description
                        )

        
        # 显示选中数量
        st.divider()
        selected_count = len(selected_ids)
        total_count = len(modules)
        
        # 使用颜色标识选择状态
        if selected_count == 0:
            st.warning(f"⚠️ 已选择: **{selected_count}/{total_count}** 个模块")
        elif selected_count == total_count:
            st.success(f"✅ 已选择: **{selected_count}/{total_count}** 个模块（全选）")
        else:
            st.info(f"📊 已选择: **{selected_count}/{total_count}** 个模块")
    

    
    def _render_search_box(self) -> str:
        """
        渲染搜索框
        
        Returns:
            搜索关键词
        """
        search_keyword = st.text_input(
            "🔍 搜索模块",
            placeholder="输入模块名称或描述进行搜索...",
            help="支持按模块名称和描述搜索"
        )
        return search_keyword.strip()
    
    def _filter_modules(self, modules: List[Module], keyword: str) -> List[Module]:
        """
        根据搜索关键词过滤模块
        
        Args:
            modules: 模块列表
            keyword: 搜索关键词
            
        Returns:
            过滤后的模块列表
        """
        if not keyword:
            return modules
        
        keyword_lower = keyword.lower()
        filtered = []
        
        for module in modules:
            # 在名称和描述中搜索
            if (keyword_lower in module.name.lower() or 
                keyword_lower in module.description.lower()):
                filtered.append(module)
        
        return filtered
    


    
    def _on_category_toggle(self, category_name: str):
        """
        建议选项复选框切换回调
        
        Args:
            category_name: 建议选项名称
        """
        categories = SessionStateManager.get_suggested_categories()
        current_value = categories.get(category_name, False)
        SessionStateManager.set_suggested_category(category_name, not current_value)
    
    def _add_custom_module(self, module_name: str, existing_modules: List[Module]) -> None:
        """
        添加自定义模块
        
        Args:
            module_name: 模块名称
            existing_modules: 现有模块列表
        """
        # 检查是否重复
        for module in existing_modules:
            if module.name == module_name:
                st.warning(f"⚠️ 模块 '{module_name}' 已存在")
                return
        
        # 创建自定义模块
        import uuid
        custom_module = Module(
            id=f"custom_{uuid.uuid4().hex[:8]}",
            name=module_name,
            description="用户自定义模块",
            type="自定义",
            level=2,
            selected=True,  # 默认选中
            is_custom=True
        )
        
        # 添加到模块列表
        existing_modules.append(custom_module)
        
        # 更新session state
        SessionStateManager.set_modules(existing_modules)
        
        # 自动选中新添加的模块
        selected_ids = SessionStateManager.get_selected_module_ids()
        selected_ids.add(custom_module.id)
        SessionStateManager.set_selected_module_ids(selected_ids)
        
        st.success(f"✅ 已添加模块: {module_name}")
        st.rerun()
    
    def get_selected_modules(self) -> List[Module]:
        """
        获取用户选中的模块
        
        Returns:
            选中的Module对象列表
        """
        all_modules = SessionStateManager.get_modules()
        selected_ids = SessionStateManager.get_selected_module_ids()
        
        return [module for module in all_modules if module.id in selected_ids]
    
    def get_selected_categories(self) -> List[str]:
        """
        获取用户选中的建议选项
        
        Returns:
            选中的建议选项名称列表
        """
        return SessionStateManager.get_selected_categories()