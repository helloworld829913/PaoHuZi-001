# -*- coding: utf-8 -*-
"""
AI玩家
"""

import random
from typing import Optional, List, Tuple, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.player import Player
from core.card import Card
from rules.win_checker import WinChecker


class AIPlayer(Player):
    """
    AI玩家
    使用简单策略进行决策
    """
    
    def __init__(self, player_id: int, name: str):
        """
        初始化AI玩家
        
        Args:
            player_id: 玩家ID
            name: 玩家名称
        """
        super().__init__(player_id, name, is_human=False)
        self.difficulty = "simple"  # 简单难度
    
    def decide_after_draw(self) -> Tuple[str, Any]:
        """
        摸牌后的决策
        
        返回决策：
        - ('win', None): 胡牌
        - ('ti', None): 提
        - ('wei', None): 委
        - ('discard', card): 打出某张牌
        
        Returns:
            (动作类型, 参数)
        """
        # 1. 检查是否能胡牌
        can_win, huxi, combination = self.can_win()
        if can_win:
            return ('win', None)
        
        # 2. 检查是否能提（优先级高，因为是四连牌）
        if self.can_ti():
            return ('ti', None)
        
        # 3. 检查是否能委
        if self.can_wei():
            # AI策略：如果委后可能更容易胡牌，就委
            # 简单策略：总是委
            return ('wei', None)
        
        # 4. 决定打哪张牌
        card_to_discard = self._choose_discard_card()
        return ('discard', card_to_discard)
    
    def _choose_discard_card(self) -> Card:
        """
        选择要打出的牌
        
        策略：
        1. 优先打出孤张（无法组成牌型的牌）
        2. 其次打出不容易组成特殊顺子的牌
        3. 保留对子和可能组成顺子的牌
        
        Returns:
            要打出的牌
        """
        # 如果有摸到的牌，优先考虑打摸到的牌
        drawn = self.hand.drawn_card
        
        # 获取所有可打的牌
        all_cards = self.hand.cards.copy()
        if drawn:
            all_cards.append(drawn)
        
        # 统计每张牌的价值
        card_values = {}
        for card in all_cards:
            value = self._evaluate_card_value(card, all_cards)
            card_values[card] = value
        
        # 选择价值最低的牌打出
        min_value = min(card_values.values())
        candidates = [c for c, v in card_values.items() if v == min_value]
        
        # 在价值相同的牌中随机选择
        return random.choice(candidates)
    
    def _evaluate_card_value(self, card: Card, all_cards: List[Card]) -> int:
        """
        评估一张牌的价值（价值越高越不应该打出）
        
        Args:
            card: 要评估的牌
            all_cards: 所有牌（包括摸到的）
        
        Returns:
            价值分数
        """
        value = 0
        
        # 1. 如果有对子，价值+10
        count = sum(1 for c in all_cards if c == card)
        if count >= 2:
            value += 10
        if count >= 3:
            value += 20
        
        # 2. 如果能组成特殊顺子，价值+15
        if self._can_form_special_sequence(card, all_cards):
            value += 15
        
        # 3. 如果能组成普通顺子，价值+5
        if self._can_form_normal_sequence(card, all_cards):
            value += 5
        
        # 4. 边张（1,10）价值较低
        if card.value in [1, 10]:
            value -= 3
        
        return value
    
    def _can_form_special_sequence(self, card: Card, all_cards: List[Card]) -> bool:
        """检查是否能组成特殊顺子（一二三或二七十）"""
        from config.game_config import SPECIAL_SEQUENCES
        
        for special_seq in SPECIAL_SEQUENCES:
            if card.value in special_seq:
                # 检查是否有其他两个值
                other_values = [v for v in special_seq if v != card.value]
                has_first = any(c.value == other_values[0] and c.is_uppercase == card.is_uppercase 
                               for c in all_cards if c != card)
                has_second = any(c.value == other_values[1] and c.is_uppercase == card.is_uppercase 
                                for c in all_cards if c != card)
                if has_first or has_second:
                    return True
        return False
    
    def _can_form_normal_sequence(self, card: Card, all_cards: List[Card]) -> bool:
        """检查是否能组成普通顺子"""
        # 检查前后连续的牌
        for offset in [-2, -1, 1, 2]:
            target_value = card.value + offset
            if 1 <= target_value <= 10:
                if any(c.value == target_value and c.is_uppercase == card.is_uppercase 
                      for c in all_cards if c != card):
                    return True
        return False
    
    def decide_on_discard(self, discarded_card: Card) -> Tuple[str, Any]:
        """
        别人打牌后的决策
        
        Returns:
            (动作类型, 参数)
            - ('win', None): 胡牌
            - ('pao', None): 跑
            - ('peng', None): 碰
            - ('chi', [card1, card2]): 吃（使用hand_cards）
            - ('pass', None): 过
        """
        # 1. 检查是否能胡牌（接别人打出的牌胡）
        # 暂时简化：只检查自摸胡
        
        # 2. 检查是否能跑（优先级最高）
        if self.can_pao(discarded_card):
            return ('pao', None)
        
        # 3. 检查是否能碰
        if self.can_peng(discarded_card):
            # AI策略：如果碰后更有利，就碰
            # 简单策略：总是碰
            return ('peng', None)
        
        # 4. 检查是否能吃
        chi_options = self.can_chi(discarded_card)
        if chi_options:
            # 简单策略：选择能组成特殊顺子的吃法
            for option in chi_options:
                test_cards = [discarded_card] + option
                if self._is_special_seq(test_cards):
                    return ('chi', option)
            
            # 如果没有特殊顺子，随机选择一个
            # 但AI不太积极吃普通顺子
            if random.random() < 0.3:  # 30%概率吃普通顺子
                return ('chi', random.choice(chi_options))
        
        # 5. 过
        return ('pass', None)
    
    def _is_special_seq(self, cards: List[Card]) -> bool:
        """判断是否是特殊顺子"""
        from rules.pattern_matcher import PatternMatcher
        return PatternMatcher.is_special_sequence(cards)
