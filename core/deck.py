# -*- coding: utf-8 -*-
"""
牌堆管理
"""

import random
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card
from config.game_config import CARD_VALUES, TOTAL_CARDS


class Deck:
    """
    牌堆管理类
    负责创建、洗牌、发牌
    """
    
    def __init__(self):
        """初始化牌堆"""
        self.cards: List[Card] = []
        self.remaining_cards: List[Card] = []
        self._create_cards()
    
    def _create_cards(self):
        """
        创建80张牌
        每个值(1-10)有8张：4张小写 + 4张大写
        """
        self.cards = []
        for value in CARD_VALUES:
            # 每个值创建4张小写和4张大写
            for _ in range(4):
                self.cards.append(Card(value=value, is_uppercase=False))
                self.cards.append(Card(value=value, is_uppercase=True))
        
        if len(self.cards) != TOTAL_CARDS:
            raise ValueError(f"牌的数量不正确！期望{TOTAL_CARDS}张，实际{len(self.cards)}张")
        
        self.remaining_cards = self.cards.copy()
    
    def shuffle(self):
        """
        洗牌 - 使用Fisher-Yates算法确保随机性
        """
        random.shuffle(self.remaining_cards)
    
    def deal(self, num: int) -> List[Card]:
        """
        发牌
        
        Args:
            num: 要发的牌数
        
        Returns:
            发出的牌列表
        
        Raises:
            ValueError: 如果剩余牌数不足
        """
        if num > len(self.remaining_cards):
            raise ValueError(
                f"剩余牌数不足！需要{num}张，剩余{len(self.remaining_cards)}张"
            )
        
        dealt_cards = self.remaining_cards[:num]
        self.remaining_cards = self.remaining_cards[num:]
        return dealt_cards
    
    def draw(self) -> Card:
        """
        摸一张牌
        
        Returns:
            摸到的牌
        
        Raises:
            ValueError: 如果没有剩余牌
        """
        if not self.remaining_cards:
            raise ValueError("牌堆已空，无法摸牌！")
        
        card = self.remaining_cards[0]
        self.remaining_cards = self.remaining_cards[1:]
        return card
    
    def get_remaining_count(self) -> int:
        """
        获取剩余牌数
        
        Returns:
            剩余牌的数量
        """
        return len(self.remaining_cards)
    
    def is_empty(self) -> bool:
        """
        判断牌堆是否为空
        
        Returns:
            True如果为空，否则False
        """
        return len(self.remaining_cards) == 0
    
    def reset(self):
        """重置牌堆（用于新一局）"""
        self.remaining_cards = self.cards.copy()
        self.shuffle()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Deck(总牌数={TOTAL_CARDS}, 剩余={self.get_remaining_count()})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return self.__str__()
