# -*- coding: utf-8 -*-
"""
玩家类
"""

from typing import Optional, List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card
from core.hand import Hand
from rules.win_checker import WinChecker


class Player:
    """
    玩家基类
    """
    
    def __init__(self, player_id: int, name: str, is_human: bool = False):
        """
        初始化玩家
        
        Args:
            player_id: 玩家ID
            name: 玩家名称
            is_human: 是否是真人玩家
        """
        self.player_id = player_id
        self.name = name
        self.is_human = is_human
        self.hand = Hand()
        self.score = 0  # 总分
        self.is_dealer = False  # 是否是庄家
    
    def set_dealer(self, is_dealer: bool):
        """设置是否为庄家"""
        self.is_dealer = is_dealer
    
    def add_score(self, points: int):
        """增加分数"""
        self.score += points
    
    def draw_card(self, card: Card):
        """
        摸牌
        
        Args:
            card: 摸到的牌
        """
        self.hand.draw_card(card)
    
    def can_win(self) -> tuple:
        """
        检查是否能胡牌
        
        Returns:
            (能否胡牌, 胡希值, 胡牌组合)
        """
        return WinChecker.can_win(self.hand)
    
    def can_wei(self) -> bool:
        """检查是否能委"""
        return self.hand.can_wei()
    
    def can_ti(self) -> bool:
        """检查是否能提"""
        return self.hand.can_ti()
    
    def can_peng(self, card: Card) -> bool:
        """
        检查是否能碰（手里有2张相同的牌）
        
        Args:
            card: 别人打出的牌
        
        Returns:
            True如果能碰
        """
        return self.hand.count_exact_card(card, include_drawn=False) >= 2
    
    def can_pao(self, card: Card) -> bool:
        """
        检查是否能跑（手里有3张相同的牌，别人打第4张）
        注意：需要考虑委牌的情况（委1张+手里2张+别人打的1张=4张）
        
        Args:
            card: 别人打出的牌
        
        Returns:
            True如果能跑
        """
        # 统计手牌中的相同牌数
        hand_count = self.hand.count_exact_card(card, include_drawn=False)
        
        # 检查是否委过这张牌
        wei_count = 0
        for group in self.hand.exposed_groups:
            if group['type'] == 'wei' and group['cards'] and group['cards'][0] == card:
                wei_count = len(group['cards'])
                break
        
        # 可以跑的情况：
        # 1. 手里有3张（正常跑）
        # 2. 委了3张，手里0张（从委牌升级到跑）
        # 3. 委了1张，手里2张（不可能委3张还有手牌，委的是3张一组）
        # 实际上委是3张（手里2张+摸到1张），所以：
        # - 如果委了3张，手里有0张，总共3张，+别人打的1张=4张，可以跑
        # - 如果手里有3张，没有委，总共3张，+别人打的1张=4张，可以跑
        total_count = hand_count + wei_count
        return total_count == 3
    
    def can_chi(self, card: Card) -> List[List[Card]]:
        """
        检查是否能吃（能和手牌组成顺子）
        
        Args:
            card: 别人打出的牌
        
        Returns:
            所有可能的吃牌组合列表（每个组合包含手牌中的2张牌）
        """
        from rules.pattern_matcher import PatternMatcher
        
        possible_chis = []
        
        # 遍历手牌，找能和card组成顺子的牌
        for i in range(len(self.hand.cards)):
            for j in range(i + 1, len(self.hand.cards)):
                card1 = self.hand.cards[i]
                card2 = self.hand.cards[j]
                
                # 检查这3张牌是否能组成顺子
                test_cards = [card, card1, card2]
                if PatternMatcher.is_valid_sequence(test_cards):
                    possible_chis.append([card1, card2])
        
        return possible_chis
    
    def do_wei(self):
        """
        执行委操作（手里2张+摸到1张）
        """
        if not self.can_wei():
            raise ValueError("无法执行委操作")
        
        # 从手牌中取出2张
        drawn_card = self.hand.drawn_card
        same_cards = [c for c in self.hand.cards if c == drawn_card][:2]
        
        # 移除这2张牌
        for card in same_cards:
            self.hand.remove_card(card)
        
        # 添加到已亮牌组（委是暗的）
        wei_cards = same_cards + [drawn_card]
        self.hand.add_exposed_group('wei', wei_cards, is_concealed=True)
        
        # 清除摸到的牌
        self.hand.clear_drawn_card()
    
    def do_ti(self):
        """
        执行提操作（手里3张+摸到1张，或从委升级到提）
        """
        if not self.can_ti():
            raise ValueError("无法执行提操作")
        
        drawn_card = self.hand.drawn_card
        
        # 检查是否有委过这张牌
        wei_group_idx = None
        for i, group in enumerate(self.hand.exposed_groups):
            if group['type'] == 'wei' and group['cards'] and group['cards'][0] == drawn_card:
                wei_group_idx = i
                break
        
        if wei_group_idx is not None:
            # 从委升级到提：取出委的3张牌
            wei_cards = self.hand.exposed_groups[wei_group_idx]['cards']
            ti_cards = wei_cards + [drawn_card]
            # 移除原来的委牌组
            self.hand.exposed_groups.pop(wei_group_idx)
        else:
            # 正常提：从手牌中取出3张
            same_cards = [c for c in self.hand.cards if c == drawn_card][:3]
            
            # 移除这3张牌
            for card in same_cards:
                self.hand.remove_card(card)
            
            ti_cards = same_cards + [drawn_card]
        
        # 添加到已亮牌组（提是明的，算四连牌）
        self.hand.add_exposed_group('ti', ti_cards, is_concealed=False)
        
        # 清除摸到的牌
        self.hand.clear_drawn_card()
    
    def do_peng(self, card: Card):
        """
        执行碰操作
        
        Args:
            card: 别人打出的牌
        """
        if not self.can_peng(card):
            raise ValueError("无法执行碰操作")
        
        # 从手牌中取出2张相同的牌
        same_cards = [c for c in self.hand.cards if c == card][:2]
        
        # 移除这2张牌
        for card_to_remove in same_cards:
            self.hand.remove_card(card_to_remove)
        
        # 添加到已亮牌组
        peng_cards = same_cards + [card]
        self.hand.add_exposed_group('peng', peng_cards, is_concealed=False)
    
    def do_pao(self, card: Card):
        """
        执行跑操作（支持从委升级到跑）
        
        Args:
            card: 别人打出的牌
        """
        if not self.can_pao(card):
            raise ValueError("无法执行跑操作")
        
        # 检查是否有委过这张牌
        wei_group_idx = None
        for i, group in enumerate(self.hand.exposed_groups):
            if group['type'] == 'wei' and group['cards'] and group['cards'][0] == card:
                wei_group_idx = i
                break
        
        if wei_group_idx is not None:
            # 从委升级到跑：取出委的3张牌
            wei_cards = self.hand.exposed_groups[wei_group_idx]['cards']
            pao_cards = wei_cards + [card]
            # 移除原来的委牌组
            self.hand.exposed_groups.pop(wei_group_idx)
        else:
            # 正常跑：从手牌中取出3张相同的牌
            same_cards = [c for c in self.hand.cards if c == card][:3]
            
            # 移除这3张牌
            for card_to_remove in same_cards:
                self.hand.remove_card(card_to_remove)
            
            pao_cards = same_cards + [card]
        
        # 添加到已亮牌组（跑是明牌，算四连牌）
        self.hand.add_exposed_group('pao', pao_cards, is_concealed=False)
    
    def do_chi(self, card: Card, hand_cards: List[Card]):
        """
        执行吃操作
        
        Args:
            card: 别人打出的牌
            hand_cards: 手牌中用于吃的2张牌
        """
        from rules.pattern_matcher import PatternMatcher
        
        # 验证是否能组成顺子
        test_cards = [card] + hand_cards
        if not PatternMatcher.is_valid_sequence(test_cards):
            raise ValueError("这些牌无法组成顺子")
        
        # 移除手牌中的2张牌
        for card_to_remove in hand_cards:
            if not self.hand.remove_card(card_to_remove):
                raise ValueError(f"手牌中没有这张牌: {card_to_remove}")
        
        # 添加到已亮牌组
        chi_cards = [card] + hand_cards
        self.hand.add_exposed_group('chi', chi_cards, is_concealed=False)
    
    def discard_card(self, card: Card) -> Card:
        """
        打出一张牌
        
        Args:
            card: 要打出的牌
        
        Returns:
            打出的牌
        """
        # 如果打的是摸到的牌
        if self.hand.drawn_card and card == self.hand.drawn_card:
            return self.hand.discard_drawn_card()
        # 如果打的是手牌中的牌
        elif card in self.hand.cards:
            return self.hand.discard_hand_card(card)
        else:
            raise ValueError(f"无法打出这张牌: {card}")
    
    def reset_hand(self):
        """重置手牌（新一局）"""
        self.hand.clear()
        self.is_dealer = False
    
    def get_total_cards(self) -> int:
        """获取总牌数"""
        return self.hand.get_total_count()
    
    def __str__(self) -> str:
        """字符串表示"""
        dealer_mark = "🏵庄" if self.is_dealer else ""
        human_mark = "👤" if self.is_human else "🤖"
        return f"{human_mark}{self.name}{dealer_mark}(分数:{self.score})"
    
    def __repr__(self) -> str:
        """详细表示"""
        return self.__str__()
