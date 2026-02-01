#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块数据模型
用于表示从需求文档中识别出的模块/页面
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Module:
    """模块数据模型"""
    id: str                    # 唯一标识
    name: str                  # 模块名称
    description: str           # 模块描述
    type: str                  # 模块类型（列表页、详情页等）
    level: int                 # 标题层级（1-6）
    selected: bool = True      # 是否选中（默认选中）
    is_custom: bool = False    # 是否为用户自定义模块
    
    def to_dict(self) -> Dict:
        """
        转换为字典
        
        Returns:
            包含所有字段的字典
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'level': self.level,
            'selected': self.selected,
            'is_custom': self.is_custom
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Module':
        """
        从字典创建Module实例
        
        Args:
            data: 包含模块数据的字典
            
        Returns:
            Module实例
        """
        return cls(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            type=data.get('type', ''),
            level=data.get('level', 1),
            selected=data.get('selected', True),
            is_custom=data.get('is_custom', False)
        )