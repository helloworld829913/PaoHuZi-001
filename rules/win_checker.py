# -*- coding: utf-8 -*-
"""
胡牌判定器 - 判断是否能胡牌
"""

from typing import List, Dict, Optional, Tuple
from collections import Counter
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card
from core.hand import Hand
from rules.pattern_matcher import PatternMatcher
from rules.huxi_calculator import HuxiCalculator
from config.game_config import MIN_HUXI_TO_WIN


class WinChecker:
    """
    胡牌判定器
    判断牌型是否满足胡牌条件
    
    重要规则：
    - 如果有3张或4张完全相同的牌，它们必须保持为三连牌或四连牌
    - 不能将三连牌拆开为对子+单张
    """
    
    @staticmethod
    def can_win(hand: Hand) -> Tuple[bool, int, Optional[Dict]]:
        """
        判断是否能胡牌
        
        胡牌条件：
        1. 牌型满足 3x + 3y + 2z = 21（顺子+三连牌+对子）
        2. 胡希 >= 15
        
        Args:
            hand: 玩家手牌
        
        Returns:
            (能否胡牌, 胡希值, 胡牌组合)
        """
        # 获取所有牌（手牌 + 摸到的牌）
        all_cards = hand.cards.copy()
        if hand.drawn_card:
            all_cards.append(hand.drawn_card)
        
        # 检查牌型组合
        win_combination = WinChecker._find_win_combination(all_cards)
        
        if win_combination is None:
            return False, 0, None
        
        # 计算胡希
        huxi = HuxiCalculator.calculate_win_huxi(all_cards, hand.exposed_groups, win_combination)
        
        # 检查是否满足最低胡希要求
        if huxi < MIN_HUXI_TO_WIN:
            return False, huxi, win_combination
        
        return True, huxi, win_combination
    
    @staticmethod
    def _find_win_combination(cards: List[Card]) -> Optional[Dict]:
        """
        寻找胡牌组合
        
        重要规则：三连牌/四连牌不能拆开
        
        算法：
        1. 先识别所有必须的三连牌和四连牌（3张或4张完全相同的牌）
        2. 在剩余的牌中找对子
        3. 剩余的牌组成顺子
        
        Args:
            cards: 所有牌
        
        Returns:
            胡牌组合字典，包含triplets, sequences, pair
            None如果找不到
        """
        if len(cards) != 21:
            return None
        
        # 1. 先找出所有必须保持的三连牌和四连牌
        forced_triplets = []
        forced_quadruplets = []
        remaining = cards.copy()
        
        # 统计每种牌的数量
        card_count = Counter(cards)
        
        for card, count in card_count.items():
            if count == 4:
                # 4张相同，必须作为四连牌（但在胡牌时算作三连牌+单张或其他组合）
                # 实际上4张牌在胡牌时比较特殊，暂时先作为三连牌处理
                card_list = [c for c in remaining if c == card]
                forced_triplets.append(card_list[:3])
                # 移除3张，留1张
                for _ in range(3):
                    remaining.remove(card)
            elif count == 3:
                # 3张相同，必须作为三连牌，不能拆开
                card_list = [c for c in remaining if c == card]
                forced_triplets.append(card_list)
                for c in card_list:
                    remaining.remove(c)
        
        # 2. 现在remaining中没有三连牌了，可以尝试找对子
        # 剩余牌数应该是 21 - len(forced_triplets)*3 = 21 - 3n
        # 需要满足：剩余牌能组成 m个顺子 + 1个对子
        # 即：remaining_count = 3m + 2
        
        if len(remaining) % 3 == 2:
            # 可能的情况：需要1个对子 + 若干顺子
            result = WinChecker._try_find_sequences_and_pair(remaining)
            if result:
                sequences, pair = result
                return {
                    'triplets': forced_triplets,
                    'sequences': sequences,
                    'pair': pair
                }
        
        return None
    
    @staticmethod
    def _try_find_sequences_and_pair(cards: List[Card]) -> Optional[Tuple[List, List]]:
        """
        在剩余牌中找顺子和对子
        
        Args:
            cards: 剩余的牌（已移除强制三连牌）
        
        Returns:
            (顺子列表, 对子) 或 None
        """
        if len(cards) < 2:
            return None
        
        # 尝试所有可能的对子
        pairs = PatternMatcher.find_pairs(cards)
        
        for pair in pairs:
            remaining = PatternMatcher.remove_cards_from_list(cards, pair)
            
            # 剩余的牌必须全部能组成顺子
            if len(remaining) % 3 != 0:
                continue
            
            # 尝试将剩余牌组成顺子
            if WinChecker._can_form_all_sequences(remaining):
                # 找出具体的顺子组合
                sequences = WinChecker._find_all_sequences(remaining)
                if sequences and len(sequences) * 3 == len(remaining):
                    return (sequences, pair)
        
        return None
    
    @staticmethod
    def _can_form_all_sequences(cards: List[Card]) -> bool:
        """
        检查所有牌是否能组成顺子
        
        Args:
            cards: 牌列表
        
        Returns:
            True如果可以全部组成顺子
        """
        if len(cards) == 0:
            return True
        
        if len(cards) % 3 != 0:
            return False
        
        # 尝试递归组成顺子
        return WinChecker._try_form_sequences_recursive(cards)
    
    @staticmethod
    def _try_form_sequences_recursive(cards: List[Card]) -> bool:
        """
        递归尝试将所有牌组成顺子
        
        Args:
            cards: 牌列表
        
        Returns:
            True如果成功
        """
        if len(cards) == 0:
            return True
        
        if len(cards) % 3 != 0:
            return False
        
        # 找所有可能的顺子
        possible_seqs = PatternMatcher.find_sequences(cards)
        
        # 尝试每一个可能的顺子
        for seq in possible_seqs:
            if all(c in cards for c in seq):
                remaining = PatternMatcher.remove_cards_from_list(cards, seq)
                if WinChecker._try_form_sequences_recursive(remaining):
                    return True
        
        return False
    
    @staticmethod
    def _find_all_sequences(cards: List[Card]) -> Optional[List[List[Card]]]:
        """
        找出所有顺子（递归）
        
        Args:
            cards: 牌列表
        
        Returns:
            顺子列表
        """
        if len(cards) == 0:
            return []
        
        if len(cards) % 3 != 0:
            return None
        
        possible_seqs = PatternMatcher.find_sequences(cards)
        
        for seq in possible_seqs:
            if all(c in cards for c in seq):
                remaining = PatternMatcher.remove_cards_from_list(cards, seq)
                rest_seqs = WinChecker._find_all_sequences(remaining)
                if rest_seqs is not None:
                    return [seq] + rest_seqs
        
        return None
    
    @staticmethod
    def estimate_win_probability(hand: Hand) -> float:
        """
        估算胡牌概率（用于AI决策）
        
        这是一个简化的估算，基于：
        - 已有的三连牌/顺子数量
        - 对子数量
        - 当前胡希
        
        Args:
            hand: 玩家手牌
        
        Returns:
            胜率估计 (0.0-1.0)
        """
        all_cards = hand.cards.copy()
        if hand.drawn_card:
            all_cards.append(hand.drawn_card)
        
        # 统计已有的牌型
        card_count = Counter(all_cards)
        
        # 计算评分
        score = 0.0
        
        # 三连牌和四连牌
        for count in card_count.values():
            if count >= 3:
                score += 0.15
            elif count == 2:
                score += 0.05
        
        # 根据已亮牌组调整
        score += len(hand.exposed_groups) * 0.15
        
        return min(score, 1.0)
