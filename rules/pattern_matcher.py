# -*- coding: utf-8 -*-
"""
模式匹配器 - 识别顺子、三连牌、四连牌等
"""

from typing import List, Tuple, Set
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card
from config.game_config import SPECIAL_SEQUENCES


class PatternMatcher:
    """
    模式匹配器
    用于识别各种牌型组合
    """
    
    @staticmethod
    def find_triplets(cards: List[Card]) -> List[List[Card]]:
        """
        找出所有三连牌（3张完全相同的牌）
        
        Args:
            cards: 牌列表
        
        Returns:
            三连牌列表
        """
        triplets = []
        card_counts = {}
        
        for card in cards:
            key = (card.value, card.is_uppercase)
            if key not in card_counts:
                card_counts[key] = []
            card_counts[key].append(card)
        
        for key, card_list in card_counts.items():
            if len(card_list) >= 3:
                triplets.append(card_list[:3])
        
        return triplets
    
    @staticmethod
    def find_quadruplets(cards: List[Card]) -> List[List[Card]]:
        """
        找出所有四连牌（4张完全相同的牌）
        
        Args:
            cards: 牌列表
        
        Returns:
            四连牌列表
        """
        quadruplets = []
        card_counts = {}
        
        for card in cards:
            key = (card.value, card.is_uppercase)
            if key not in card_counts:
                card_counts[key] = []
            card_counts[key].append(card)
        
        for key, card_list in card_counts.items():
            if len(card_list) == 4:
                quadruplets.append(card_list)
        
        return quadruplets
    
    @staticmethod
    def is_valid_sequence(cards: List[Card]) -> bool:
        """
        判断3张牌是否构成顺子
        
        顺子规则：
        1. 必须是同样的大小写
        2. 连续的值（如123, 456）
        3. 特殊顺子：一二三(123)、二七十(2,7,10)
        
        Args:
            cards: 3张牌
        
        Returns:
            True如果是顺子
        """
        if len(cards) != 3:
            return False
        
        # 必须是同样的大小写
        if not all(c.is_uppercase == cards[0].is_uppercase for c in cards):
            return False
        
        # 按值排序
        values = sorted([c.value for c in cards])
        
        # 检查特殊顺子
        if values in SPECIAL_SEQUENCES:
            return True
        
        # 检查普通连续顺子
        return values[1] == values[0] + 1 and values[2] == values[1] + 1
    
    @staticmethod
    def is_special_sequence(cards: List[Card]) -> bool:
        """
        判断是否是特殊顺子（一二三 或 二七十）
        
        Args:
            cards: 3张牌
        
        Returns:
            True如果是特殊顺子
        """
        if len(cards) != 3:
            return False
        
        if not all(c.is_uppercase == cards[0].is_uppercase for c in cards):
            return False
        
        values = sorted([c.value for c in cards])
        return values in SPECIAL_SEQUENCES
    
    @staticmethod
    def find_sequences(cards: List[Card]) -> List[List[Card]]:
        """
        找出所有可能的顺子
        
        Args:
            cards: 牌列表
        
        Returns:
            顺子列表
        """
        sequences = []
        
        # 分别处理小写和大写
        for is_uppercase in [False, True]:
            uppercase_cards = [c for c in cards if c.is_uppercase == is_uppercase]
            
            # 按值分组
            value_cards = {}
            for card in uppercase_cards:
                if card.value not in value_cards:
                    value_cards[card.value] = []
                value_cards[card.value].append(card)
            
            # 检查特殊顺子 [1,2,3] 和 [2,7,10]
            for special_seq in SPECIAL_SEQUENCES:
                if all(v in value_cards for v in special_seq):
                    # 取每个值的一张牌组成顺子
                    seq = [value_cards[v][0] for v in special_seq]
                    sequences.append(seq)
            
            # 检查普通连续顺子
            sorted_values = sorted(value_cards.keys())
            for i in range(len(sorted_values) - 2):
                v1, v2, v3 = sorted_values[i], sorted_values[i+1], sorted_values[i+2]
                if v2 == v1 + 1 and v3 == v2 + 1:
                    # 排除已经在特殊顺子中的
                    if [v1, v2, v3] not in SPECIAL_SEQUENCES:
                        seq = [value_cards[v1][0], value_cards[v2][0], value_cards[v3][0]]
                        sequences.append(seq)
        
        return sequences
    
    @staticmethod
    def find_pairs(cards: List[Card]) -> List[List[Card]]:
        """
        找出所有对子（2张完全相同的牌）
        
        Args:
            cards: 牌列表
        
        Returns:
            对子列表
        """
        pairs = []
        card_counts = {}
        
        for card in cards:
            key = (card.value, card.is_uppercase)
            if key not in card_counts:
                card_counts[key] = []
            card_counts[key].append(card)
        
        for key, card_list in card_counts.items():
            if len(card_list) >= 2:
                pairs.append(card_list[:2])
        
        return pairs
    
    @staticmethod
    def remove_cards_from_list(cards: List[Card], to_remove: List[Card]) -> List[Card]:
        """
        从牌列表中移除指定的牌
        
        Args:
            cards: 原牌列表
            to_remove: 要移除的牌
        
        Returns:
            移除后的牌列表
        """
        remaining = cards.copy()
        for card in to_remove:
            if card in remaining:
                remaining.remove(card)
        return remaining
