#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块识别器
从需求文档中识别功能模块/页面
"""

import re
import hashlib
from typing import List, Optional
from module import Module
from ai_generator import AIGenerator


class ModuleRecognizer:
    """模块识别器 - 从需求文档中识别功能模块"""
    
    def __init__(self, ai_generator: Optional[AIGenerator] = None):
        """
        初始化识别器
        
        Args:
            ai_generator: 可选的AIGenerator实例，用于AI识别
        """
        self.ai_generator = ai_generator
    
    def recognize_modules(self, content: str, file_type: str) -> List[Module]:
        """
        识别文档中的模块
        
        Args:
            content: 文档内容
            file_type: 文件类型 (md, txt, docx)
            
        Returns:
            模块列表
        """
        modules = []
        
        # 优先使用AI识别（如果配置了AI生成器）
        if self.ai_generator and self.ai_generator.client:
            try:
                modules = self._recognize_with_ai(content)
                if modules:
                    print(f"AI识别成功，识别到 {len(modules)} 个模块")
                    return self._validate_and_filter(modules)
            except Exception as e:
                print(f"AI识别失败，降级到规则识别: {e}")
        
        # 降级到规则识别
        if file_type in ['md', 'txt']:
            modules = self._recognize_from_markdown(content)
        elif file_type == 'docx':
            modules = self._recognize_from_docx(content)
        else:
            # 默认使用Markdown识别
            modules = self._recognize_from_markdown(content)
        
        print(f"规则识别完成，识别到 {len(modules)} 个模块")
        return self._validate_and_filter(modules)

    def _recognize_from_markdown(self, content: str) -> List[Module]:
        """
        从Markdown标题识别模块
        
        Args:
            content: Markdown文档内容
            
        Returns:
            模块列表
        """
        modules = []
        lines = content.split('\n')
        
        # 正则匹配Markdown标题 (##, ###, ####等)
        heading_pattern = re.compile(r'^(#{2,6})\s+(.+)')
        
        for line in lines:
            match = heading_pattern.match(line.strip())
            if match:
                level_marks = match.group(1)
                title = match.group(2).strip()
                
                # 计算层级 (## = 2, ### = 3, etc.)
                level = len(level_marks)
                
                # 过滤掉数字开头的标题（如：## 1. 概述 或 ## 2.1 基本信息）
                # 提取实际的模块名称
                title_clean = re.sub(r'^\d+(\.\d+)*[\.\、]?\s*', '', title)
                
                if title_clean:
                    # 生成唯一ID
                    module_id = self._generate_module_id(title_clean)
                    
                    # 推断模块类型
                    module_type = self._infer_module_type(title_clean)
                    
                    module = Module(
                        id=module_id,
                        name=title_clean,
                        description='',  # 规则识别暂不提供描述
                        type=module_type,
                        level=level,
                        selected=True
                    )
                    modules.append(module)
        
        return modules
    
    def _recognize_from_docx(self, content: str) -> List[Module]:
        """
        从Word文档标题样式识别模块
        
        注意：由于content已经是提取后的纯文本，
        这里使用与Markdown相同的策略
        
        Args:
            content: Word文档内容（纯文本）
            
        Returns:
            模块列表
        """
        # Word文档转换为纯文本后，通常标题会保留
        # 这里使用简单的启发式规则：
        # 1. 短行（< 50字符）
        # 2. 不以标点结尾
        # 3. 可能包含数字编号
        
        modules = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行和过长的行
            if not line or len(line) > 100:
                continue
            
            # 检查是否像标题（短、不以句号结尾）
            if len(line) < 50 and not line.endswith(('。', '.', '，', ',')):
                # 移除数字编号（支持多级编号如 1.1, 2.3.1）
                title_clean = re.sub(r'^\d+(\.\d+)*[\.\、]?\s*', '', line)
                
                # 检查是否包含关键词（页面、模块、功能等）
                if any(keyword in title_clean for keyword in ['页面', '模块', '功能', '管理', '列表', '详情', '创建', '编辑']):
                    module_id = self._generate_module_id(title_clean)
                    module_type = self._infer_module_type(title_clean)
                    
                    module = Module(
                        id=module_id,
                        name=title_clean,
                        description='',
                        type=module_type,
                        level=2,  # Word文档默认层级为2
                        selected=True
                    )
                    modules.append(module)
        
        return modules
    
    def _generate_module_id(self, name: str) -> str:
        """
        为模块生成唯一ID
        
        Args:
            name: 模块名称
            
        Returns:
            唯一ID（使用MD5哈希）
        """
        # 使用MD5哈希生成唯一ID
        hash_obj = hashlib.md5(name.encode('utf-8'))
        return hash_obj.hexdigest()[:12]  # 取前12位
    
    def _infer_module_type(self, name: str) -> str:
        """
        根据模块名称推断模块类型
        
        Args:
            name: 模块名称
            
        Returns:
            模块类型
        """
        name_lower = name.lower()
        
        # 类型关键词映射
        type_keywords = {
            '列表页': ['列表', 'list', '管理'],
            '详情页': ['详情', 'detail', '查看'],
            '创建页': ['创建', '新建', 'create', 'add', '添加'],
            '编辑页': ['编辑', 'edit', '修改', '更新'],
            '弹窗': ['弹窗', 'dialog', 'modal', '对话框'],
            '首页': ['首页', 'home', 'index', '主页'],
            '登录页': ['登录', 'login', '注册', 'register'],
        }
        
        for module_type, keywords in type_keywords.items():
            if any(keyword in name_lower for keyword in keywords):
                return module_type
        
        return '页面'  # 默认类型

    def _recognize_with_ai(self, content: str) -> List[Module]:
        """
        使用AI识别模块
        
        Args:
            content: 文档内容
            
        Returns:
            模块列表
        """
        try:
            # 调用AIGenerator的analyze_requirement方法
            result = self.ai_generator.analyze_requirement(content)
            
            if not result or 'modules' not in result:
                print("AI返回结果格式错误")
                return []
            
            modules = []
            for idx, module_data in enumerate(result['modules']):
                # 生成唯一ID
                module_id = self._generate_module_id(module_data['name'])
                
                # 推断模块类型（如果AI没有提供）
                module_type = module_data.get('type', '')
                if not module_type:
                    module_type = self._infer_module_type(module_data['name'])
                
                module = Module(
                    id=module_id,
                    name=module_data['name'],
                    description=module_data.get('description', ''),
                    type=module_type,
                    level=2,  # AI识别默认层级为2
                    selected=True
                )
                modules.append(module)
            
            return modules
            
        except Exception as e:
            print(f"AI识别过程出错: {e}")
            # 抛出异常，让上层降级到规则识别
            raise

    def _validate_and_filter(self, modules: List[Module]) -> List[Module]:
        """
        验证和过滤识别结果
        
        Args:
            modules: 原始模块列表
            
        Returns:
            验证后的模块列表
        """
        if not modules:
            print("警告：未识别到任何模块")
            return []
        
        # 1. 过滤重复模块（基于name去重）
        seen_names = set()
        unique_modules = []
        
        for module in modules:
            if module.name not in seen_names:
                seen_names.add(module.name)
                unique_modules.append(module)
            else:
                print(f"过滤重复模块: {module.name}")
        
        # 2. 验证模块数量（至少1个，最多50个）
        if len(unique_modules) < 1:
            print("警告：过滤后没有有效模块")
            return []
        
        if len(unique_modules) > 50:
            print(f"警告：识别到 {len(unique_modules)} 个模块，超过最大限制50个，将截取前50个")
            unique_modules = unique_modules[:50]
        
        # 3. 为模块添加默认描述（如果没有描述）
        for module in unique_modules:
            if not module.description:
                module.description = f"{module.type} - {module.name}"
        
        print(f"验证完成：保留 {len(unique_modules)} 个有效模块")
        return unique_modules


# 使用示例
if __name__ == '__main__':
    # 测试规则识别
    test_content = """
# 跨域训练系统

## 1. 跨域训练首页
展示训练任务列表

## 2. 新建训练任务
创建新的训练任务

### 2.1 基本信息
填写任务基本信息

### 2.2 参数配置
配置训练参数

## 3. 任务详情页
查看任务详细信息

## 4. 编辑任务
修改现有任务
"""
    
    recognizer = ModuleRecognizer()
    modules = recognizer.recognize_modules(test_content, 'md')
    
    print(f"\n识别到 {len(modules)} 个模块:")
    for module in modules:
        print(f"- [{module.type}] {module.name} (Level {module.level}, ID: {module.id})")