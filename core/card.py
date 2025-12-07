# -*- coding: utf-8 -*-
"""
牌的基础类
"""

from dataclasses import dataclass
from typing import ClassVar
import sys
import os
# 这段代码的功能是将当前脚本文件所在目录的上一级目录添加到Python模块搜索路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.game_config import (
    LOWERCASE_NAMES, UPPERCASE_NAMES, RED_CARD_VALUES
)


@dataclass(frozen=True)
class Card:
    """
    表示一张牌
    
    Attributes:
        value: 牌值 (1-10)
        is_uppercase: 是否大写
    """
    value: int
    is_uppercase: bool
    
    def __post_init__(self):
        """验证牌的有效性"""
        if not 1 <= self.value <= 10:
            raise ValueError(f"牌值必须在1-10之间，当前值: {self.value}")
    
    @property
    def color(self) -> str:
        """返回牌的颜色"""
        return "红" if self.is_red() else "黑"
    
    @property
    def display_name(self) -> str:
        """返回牌的显示名称"""
        if self.is_uppercase:
            return UPPERCASE_NAMES[self.value]
        else:
            return LOWERCASE_NAMES[self.value]
    
    def is_red(self) -> bool:
        """判断是否为红色牌（2、7、10）"""
        return self.value in RED_CARD_VALUES
    
    def is_same_value(self, other: 'Card') -> bool:
        """判断两张牌是否相同值（忽略大小写）"""
        if not isinstance(other, Card):
            return False
        return self.value == other.value
    
    def __str__(self) -> str:
        """字符串表示"""
        return self.display_name
    
    def __repr__(self) -> str:
        """详细表示"""
        case = "大" if self.is_uppercase else "小"
        return f"Card({self.display_name}, {case}写, {self.color})"
    
    def __lt__(self, other: 'Card') -> bool:
        """用于排序：先按值，再按大小写"""
        if self.value != other.value:
            return self.value < other.value
        # 小写在前
        return not self.is_uppercase and other.is_uppercase
    
    def __eq__(self, other) -> bool:
        """判断两张牌是否完全相同"""
        if not isinstance(other, Card):
            return False
        return self.value == other.value and self.is_uppercase == other.is_uppercase
    
    def __hash__(self) -> int:
        """哈希值，用于集合和字典"""
        return hash((self.value, self.is_uppercase))
