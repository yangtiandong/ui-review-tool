#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Session State工具类
封装Streamlit Session State的初始化和管理逻辑
"""

import streamlit as st
from typing import List, Dict, Set, Any
from module import Module


class SessionStateManager:
    """Session State管理器"""
    
    # Session State键名常量
    KEY_UPLOADED_CONTENT = 'uploaded_content'
    KEY_UPLOADED_FILENAME = 'uploaded_filename'
    KEY_FILE_TYPE = 'file_type'
    KEY_MODULES_RECOGNIZED = 'modules_recognized'
    KEY_MODULES = 'modules'
    KEY_MODULE_COUNT = 'module_count'
    KEY_SELECTED_MODULE_IDS = 'selected_module_ids'
    KEY_SELECT_ALL = 'select_all'
    KEY_SUGGESTED_CATEGORIES = 'suggested_categories'
    KEY_GENERATED_FILE = 'generated_file'
    KEY_ALL_CASES = 'all_cases'
    KEY_DATA_CLEARED = 'data_cleared'
    KEY_AI_API_KEY = 'ai_api_key'
    KEY_AI_PROVIDER = 'ai_provider'
    
    @staticmethod
    def init_session_state():
        """
        初始化Session State
        设置所有必需的默认值
        """
        # 文档相关
        if SessionStateManager.KEY_UPLOADED_CONTENT not in st.session_state:
            st.session_state[SessionStateManager.KEY_UPLOADED_CONTENT] = None
        
        if SessionStateManager.KEY_UPLOADED_FILENAME not in st.session_state:
            st.session_state[SessionStateManager.KEY_UPLOADED_FILENAME] = None
        
        if SessionStateManager.KEY_FILE_TYPE not in st.session_state:
            st.session_state[SessionStateManager.KEY_FILE_TYPE] = None
        
        # 模块识别相关
        if SessionStateManager.KEY_MODULES_RECOGNIZED not in st.session_state:
            st.session_state[SessionStateManager.KEY_MODULES_RECOGNIZED] = False
        
        if SessionStateManager.KEY_MODULES not in st.session_state:
            st.session_state[SessionStateManager.KEY_MODULES] = []
        
        if SessionStateManager.KEY_MODULE_COUNT not in st.session_state:
            st.session_state[SessionStateManager.KEY_MODULE_COUNT] = 0
        
        # 模块选择相关
        if SessionStateManager.KEY_SELECTED_MODULE_IDS not in st.session_state:
            st.session_state[SessionStateManager.KEY_SELECTED_MODULE_IDS] = set()
        
        if SessionStateManager.KEY_SELECT_ALL not in st.session_state:
            st.session_state[SessionStateManager.KEY_SELECT_ALL] = True
        
        # 建议选项相关
        if SessionStateManager.KEY_SUGGESTED_CATEGORIES not in st.session_state:
            st.session_state[SessionStateManager.KEY_SUGGESTED_CATEGORIES] = {
                '全局页面': False,
                '场景流程': False,
                '异常场景': False,
                '上下游验证': False
            }
        
        # 生成结果相关
        if SessionStateManager.KEY_GENERATED_FILE not in st.session_state:
            st.session_state[SessionStateManager.KEY_GENERATED_FILE] = None
        
        if SessionStateManager.KEY_ALL_CASES not in st.session_state:
            st.session_state[SessionStateManager.KEY_ALL_CASES] = []
        
        # 其他
        if SessionStateManager.KEY_DATA_CLEARED not in st.session_state:
            st.session_state[SessionStateManager.KEY_DATA_CLEARED] = False
    
    @staticmethod
    def set_uploaded_document(content: str, filename: str, file_type: str):
        """
        设置上传的文档信息
        
        Args:
            content: 文档内容
            filename: 文件名
            file_type: 文件类型
        """
        st.session_state[SessionStateManager.KEY_UPLOADED_CONTENT] = content
        st.session_state[SessionStateManager.KEY_UPLOADED_FILENAME] = filename
        st.session_state[SessionStateManager.KEY_FILE_TYPE] = file_type
    
    @staticmethod
    def get_uploaded_content() -> str:
        """获取上传的文档内容"""
        return st.session_state.get(SessionStateManager.KEY_UPLOADED_CONTENT)
    
    @staticmethod
    def set_modules(modules: List[Module]):
        """
        设置识别出的模块列表
        
        Args:
            modules: 模块列表
        """
        # 将Module对象转换为字典存储
        modules_dict = [module.to_dict() for module in modules]
        st.session_state[SessionStateManager.KEY_MODULES] = modules_dict
        st.session_state[SessionStateManager.KEY_MODULE_COUNT] = len(modules)
        st.session_state[SessionStateManager.KEY_MODULES_RECOGNIZED] = True
        
        # 默认选中所有模块
        module_ids = {module.id for module in modules}
        st.session_state[SessionStateManager.KEY_SELECTED_MODULE_IDS] = module_ids
    
    @staticmethod
    def get_modules() -> List[Module]:
        """
        获取识别出的模块列表
        
        Returns:
            Module对象列表
        """
        modules_dict = st.session_state.get(SessionStateManager.KEY_MODULES, [])
        return [Module.from_dict(m) for m in modules_dict]
    
    @staticmethod
    def is_modules_recognized() -> bool:
        """检查是否已识别模块"""
        return st.session_state.get(SessionStateManager.KEY_MODULES_RECOGNIZED, False)
    
    @staticmethod
    def get_module_count() -> int:
        """获取模块总数"""
        return st.session_state.get(SessionStateManager.KEY_MODULE_COUNT, 0)
    
    @staticmethod
    def set_selected_module_ids(module_ids: Set[str]):
        """
        设置选中的模块ID集合
        
        Args:
            module_ids: 模块ID集合
        """
        st.session_state[SessionStateManager.KEY_SELECTED_MODULE_IDS] = module_ids
    
    @staticmethod
    def get_selected_module_ids() -> Set[str]:
        """获取选中的模块ID集合"""
        return st.session_state.get(SessionStateManager.KEY_SELECTED_MODULE_IDS, set())
    
    @staticmethod
    def toggle_module_selection(module_id: str):
        """
        切换模块的选中状态
        
        Args:
            module_id: 模块ID
        """
        selected_ids = SessionStateManager.get_selected_module_ids()
        if module_id in selected_ids:
            selected_ids.remove(module_id)
        else:
            selected_ids.add(module_id)
        SessionStateManager.set_selected_module_ids(selected_ids)
    
    @staticmethod
    def select_all_modules():
        """选中所有模块"""
        modules = SessionStateManager.get_modules()
        module_ids = {module.id for module in modules}
        SessionStateManager.set_selected_module_ids(module_ids)
        st.session_state[SessionStateManager.KEY_SELECT_ALL] = True
    
    @staticmethod
    def deselect_all_modules():
        """取消选中所有模块"""
        SessionStateManager.set_selected_module_ids(set())
        st.session_state[SessionStateManager.KEY_SELECT_ALL] = False
    
    @staticmethod
    def set_suggested_category(category: str, selected: bool):
        """
        设置建议选项的选中状态
        
        Args:
            category: 建议选项名称
            selected: 是否选中
        """
        categories = st.session_state.get(SessionStateManager.KEY_SUGGESTED_CATEGORIES, {})
        categories[category] = selected
        st.session_state[SessionStateManager.KEY_SUGGESTED_CATEGORIES] = categories
    
    @staticmethod
    def get_suggested_categories() -> Dict[str, bool]:
        """获取建议选项的选中状态"""
        return st.session_state.get(SessionStateManager.KEY_SUGGESTED_CATEGORIES, {})
    
    @staticmethod
    def get_selected_categories() -> List[str]:
        """
        获取选中的建议选项列表
        
        Returns:
            选中的建议选项名称列表
        """
        categories = SessionStateManager.get_suggested_categories()
        return [name for name, selected in categories.items() if selected]
    
    @staticmethod
    def set_generated_result(file_path: str, cases: List[Dict]):
        """
        设置生成结果
        
        Args:
            file_path: 生成的CSV文件路径
            cases: 用例列表
        """
        st.session_state[SessionStateManager.KEY_GENERATED_FILE] = file_path
        st.session_state[SessionStateManager.KEY_ALL_CASES] = cases
    
    @staticmethod
    def get_generated_file() -> str:
        """获取生成的CSV文件路径"""
        return st.session_state.get(SessionStateManager.KEY_GENERATED_FILE)
    
    @staticmethod
    def get_all_cases() -> List[Dict]:
        """获取所有生成的用例"""
        return st.session_state.get(SessionStateManager.KEY_ALL_CASES, [])
    
    @staticmethod
    def clear_all_data():
        """清除所有数据"""
        keys_to_clear = [
            SessionStateManager.KEY_UPLOADED_CONTENT,
            SessionStateManager.KEY_UPLOADED_FILENAME,
            SessionStateManager.KEY_FILE_TYPE,
            SessionStateManager.KEY_MODULES_RECOGNIZED,
            SessionStateManager.KEY_MODULES,
            SessionStateManager.KEY_MODULE_COUNT,
            SessionStateManager.KEY_SELECTED_MODULE_IDS,
            SessionStateManager.KEY_GENERATED_FILE,
            SessionStateManager.KEY_ALL_CASES
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # 重置建议选项
        st.session_state[SessionStateManager.KEY_SUGGESTED_CATEGORIES] = {
            '全局页面': False,
            '场景流程': False,
            '异常场景': False,
            '上下游验证': False
        }
        
        st.session_state[SessionStateManager.KEY_DATA_CLEARED] = True
    
    @staticmethod
    def clear_recognition_data():
        """清除识别数据（保留上传的文档）"""
        keys_to_clear = [
            SessionStateManager.KEY_MODULES_RECOGNIZED,
            SessionStateManager.KEY_MODULES,
            SessionStateManager.KEY_MODULE_COUNT,
            SessionStateManager.KEY_SELECTED_MODULE_IDS,
            SessionStateManager.KEY_GENERATED_FILE,
            SessionStateManager.KEY_ALL_CASES
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # 重置建议选项
        st.session_state[SessionStateManager.KEY_SUGGESTED_CATEGORIES] = {
            '全局页面': False,
            '场景流程': False,
            '异常场景': False,
            '上下游验证': False
        }