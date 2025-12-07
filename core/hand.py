# -*- coding: utf-8 -*-
"""
手牌管理
"""

from typing import List, Tuple, Dict, Optional
from collections import Counter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card


class Hand:
    """
    手牌管理类
    负责管理玩家的手牌和已亮出的牌组
    
    重要规则：
    - 摸到的牌不能直接插入手牌，需要单独存放在drawn_card中
    - 摸牌后必须判断：委、提、胡牌，或者打出一张牌
    """
    
    def __init__(self):
        """初始化手牌"""
        self.cards: List[Card] = []  # 手中的牌（不包括刚摸的牌）
        self.drawn_card: Optional[Card] = None  # 刚摸到的牌（单独存放）
        self.exposed_groups: List[Dict] = []  # 已亮出的牌组（吃、碰、跑、委、提）
    
    def add_card(self, card: Card):
        """
        添加一张牌到手牌（用于初始发牌）
        
        Args:
            card: 要添加的牌
        """
        self.cards.append(card)
    
    def add_cards(self, cards: List[Card]):
        """
        添加多张牌到手牌（用于初始发牌）
        
        Args:
            cards: 要添加的牌列表
        """
        self.cards.extend(cards)
    
    def draw_card(self, card: Card):
        """
        摸一张牌（放在drawn_card中，不插入手牌）
        
        Args:
            card: 摸到的牌
        """
        if self.drawn_card is not None:
            raise ValueError("已经有摸到的牌未处理！")
        self.drawn_card = card
    
    def clear_drawn_card(self):
        """清除摸到的牌"""
        self.drawn_card = None
    
    def has_drawn_card(self) -> bool:
        """检查是否有摸到的牌"""
        return self.drawn_card is not None
    
    def remove_card(self, card: Card) -> bool:
        """
        从手牌中移除一张牌
        
        Args:
            card: 要移除的牌
        
        Returns:
            True如果成功移除，False如果牌不存在
        """
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False
    
    def remove_cards(self, cards: List[Card]) -> bool:
        """
        从手牌中移除多张牌
        
        Args:
            cards: 要移除的牌列表
        
        Returns:
            True如果全部成功移除，False如果有牌不存在
        """
        for card in cards:
            if card not in self.cards:
                return False
        
        for card in cards:
            self.cards.remove(card)
        return True
    
    def discard_drawn_card(self) -> Card:
        """
        打出摸到的牌
        
        Returns:
            打出的牌
        """
        if self.drawn_card is None:
            raise ValueError("没有摸到的牌可以打出！")
        card = self.drawn_card
        self.drawn_card = None
        return card
    
    def discard_hand_card(self, card: Card) -> Card:
        """
        从手牌中打出一张牌（摸牌后打出手牌中的牌）
        
        Args:
            card: 要打出的牌
        
        Returns:
            打出的牌
        """
        if card not in self.cards:
            raise ValueError(f"手牌中没有这张牌: {card}")
        self.cards.remove(card)
        # 摸到的牌进入手牌
        if self.drawn_card is not None:
            self.cards.append(self.drawn_card)
            self.drawn_card = None
        return card
    
    def sort_cards(self):
        """对手牌进行排序（按值和大小写）"""
        self.cards.sort()
    
    def get_card_count(self) -> int:
        """
        获取手牌数量（不包括摸到的牌）
        
        Returns:
            手牌的数量
        """
        return len(self.cards)
    
    def get_total_count(self) -> int:
        """
        获取总牌数（手牌 + 摸到的牌 + 已亮牌组）
        
        Returns:
            总牌数
        """
        exposed_count = sum(len(group['cards']) for group in self.exposed_groups)
        drawn_count = 1 if self.drawn_card is not None else 0
        return len(self.cards) + drawn_count + exposed_count
    
    def has_card(self, card: Card) -> bool:
        """
        检查手牌中是否有某张牌
        
        Args:
            card: 要检查的牌
        
        Returns:
            True如果有，否则False
        """
        return card in self.cards
    
    def count_value(self, value: int, include_drawn: bool = False) -> int:
        """
        统计某个值的牌数（不区分大小写）
        
        Args:
            value: 牌值
            include_drawn: 是否包括摸到的牌
        
        Returns:
            该值的牌数
        """
        count = sum(1 for card in self.cards if card.value == value)
        if include_drawn and self.drawn_card and self.drawn_card.value == value:
            count += 1
        return count
    
    def count_exact_card(self, target_card: Card, include_drawn: bool = False) -> int:
        """
        统计完全相同的牌数（包括大小写）
        
        Args:
            target_card: 目标牌
            include_drawn: 是否包括摸到的牌
        
        Returns:
            相同牌的数量
        """
        count = sum(1 for card in self.cards if card == target_card)
        if include_drawn and self.drawn_card == target_card:
            count += 1
        return count
    
    def can_wei(self) -> bool:
        """
        检查是否可以委（手里有2张，摸到第3张）
        
        Returns:
            True如果可以委
        """
        if self.drawn_card is None:
            return False
        # 检查hand里是否有该牌的2张
        return self.count_exact_card(self.drawn_card, include_drawn=False) == 2
    
    def can_ti(self) -> bool:
        """
        检查是否可以提（手里有3张，摸到第4张）
        或者从委升级到提（委了3张，又摸到第4张）
        
        Returns:
            True如果可以提
        """
        if self.drawn_card is None:
            return False
        
        # 检查hand里是否有该牌的3张（正常提）
        hand_count = self.count_exact_card(self.drawn_card, include_drawn=False)
        if hand_count == 3:
            return True
        
        # 检查是否委过这张牌（从委升级到提）
        for group in self.exposed_groups:
            if group['type'] == 'wei' and group['cards'] and group['cards'][0] == self.drawn_card:
                return True
        
        return False
    
    def add_exposed_group(self, group_type: str, cards: List[Card], is_concealed: bool = False):
        """
        添加已亮出的牌组
        
        Args:
            group_type: 牌组类型（'chi'吃, 'peng'碰, 'pao'跑, 'wei'委, 'ti'提）
            cards: 牌组的牌
            is_concealed: 是否暗牌（委的情况）
        """
        self.exposed_groups.append({
            'type': group_type,
            'cards': cards.copy(),
            'is_concealed': is_concealed
        })
    
    def get_cards_by_value(self, value: int) -> List[Card]:
        """
        获取指定值的所有牌（仅手牌）
        
        Args:
            value: 牌值
        
        Returns:
            该值的所有牌
        """
        return [card for card in self.cards if card.value == value]
    
    def group_by_value(self) -> Dict[int, List[Card]]:
        """
        按值分组手牌
        
        Returns:
            字典，键为牌值，值为该值的牌列表
        """
        groups = {}
        for card in self.cards:
            if card.value not in groups:
                groups[card.value] = []
            groups[card.value].append(card)
        return groups
    
    def clear(self):
        """清空手牌和已亮牌组"""
        self.cards = []
        self.drawn_card = None
        self.exposed_groups = []
    
    def __str__(self) -> str:
        """字符串表示"""
        self.sort_cards()
        cards_str = ' '.join(str(card) for card in self.cards)
        result = f"Hand({self.get_card_count()}张): {cards_str}"
        if self.drawn_card:
            result += f" | 摸到: [{self.drawn_card}]"
        return result
    
    def __repr__(self) -> str:
        """详细表示"""
        return self.__str__()
