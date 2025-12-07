# -*- coding: utf-8 -*-
"""
胡希计算器 - 计算牌型的胡希分数
"""

from typing import List, Dict
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.card import Card
from rules.pattern_matcher import PatternMatcher
from config.game_config import SPECIAL_SEQUENCES


class HuxiCalculator:
    """
    胡希计算器
    根据牌型计算胡希分数
    """
    
    @staticmethod
    def calculate_triplet_huxi(cards: List[Card], is_exposed: bool) -> int:
        """
        计算三连牌的胡希
        
        规则：
        - 在手里：小写3胡希，大写6胡希
        - 不在手里（已亮出）：小写1胡希，大写3胡希
        
        Args:
            cards: 三连牌（3张完全相同的牌）
            is_exposed: 是否已亮出（不在手里）
        
        Returns:
            胡希值
        """
        if len(cards) != 3:
            raise ValueError("三连牌必须是3张牌")
        
        if not all(c == cards[0] for c in cards):
            raise ValueError("三连牌必须是完全相同的牌")
        
        is_uppercase = cards[0].is_uppercase
        
        if is_exposed:
            # 不在手里
            return 3 if is_uppercase else 1
        else:
            # 在手里
            return 6 if is_uppercase else 3
    
    @staticmethod
    def calculate_quadruplet_huxi(cards: List[Card], is_exposed: bool) -> int:
        """
        计算四连牌的胡希
        
        规则：
        - 在手里：小写9胡希，大写12胡希
        - 不在手里（已亮出）：小写6胡希，大写9胡希
        
        Args:
            cards: 四连牌（4张完全相同的牌）
            is_exposed: 是否已亮出（不在手里）
        
        Returns:
            胡希值
        """
        if len(cards) != 4:
            raise ValueError("四连牌必须是4张牌")
        
        if not all(c == cards[0] for c in cards):
            raise ValueError("四连牌必须是完全相同的牌")
        
        is_uppercase = cards[0].is_uppercase
        
        if is_exposed:
            # 不在手里
            return 9 if is_uppercase else 6
        else:
            # 在手里
            return 12 if is_uppercase else 9
    
    @staticmethod
    def calculate_sequence_huxi(cards: List[Card]) -> int:
        """
        计算顺子的胡希
        
        规则：
        - 一二三/壹贰叁：小写3胡希，大写6胡希
        - 二七十/贰柒拾：小写3胡希，大写6胡希
        - 其他顺子：0胡希
        
        Args:
            cards: 顺子（3张连续的牌）
        
        Returns:
            胡希值
        """
        if len(cards) != 3:
            return 0
        
        if not PatternMatcher.is_valid_sequence(cards):
            return 0
        
        # 检查是否是特殊顺子
        if PatternMatcher.is_special_sequence(cards):
            is_uppercase = cards[0].is_uppercase
            return 6 if is_uppercase else 3
        
        # 普通顺子不计胡希
        return 0
    
    @staticmethod
    def calculate_hand_huxi(hand_cards: List[Card], exposed_groups: List[Dict]) -> int:
        """
        计算手牌的总胡希（用于判断是否能胡牌）
        
        这个函数会尝试找出能产生最大胡希的牌型组合
        
        Args:
            hand_cards: 手牌
            exposed_groups: 已亮出的牌组
        
        Returns:
            总胡希值
        """
        total_huxi = 0
        
        # 1. 计算已亮出牌组的胡希
        for group in exposed_groups:
            group_type = group['type']
            cards = group['cards']
            is_concealed = group.get('is_concealed', False)
            
            if group_type == 'peng':  # 碰：三连牌，已亮出
                total_huxi += HuxiCalculator.calculate_triplet_huxi(cards, is_exposed=True)
            elif group_type == 'wei':  # 委：三连牌，未亮出（算在手里）
                total_huxi += HuxiCalculator.calculate_triplet_huxi(cards, is_exposed=False)
            elif group_type in ['pao', 'ti']:  # 跑/提：四连牌
                # 跑是碰后别人又打出，所以是亮出的
                # 提是自己摸的，算在手里
                is_exposed = (group_type == 'pao')
                total_huxi += HuxiCalculator.calculate_quadruplet_huxi(cards, is_exposed=is_exposed)
            elif group_type == 'chi':  # 吃：顺子
                total_huxi += HuxiCalculator.calculate_sequence_huxi(cards)
        
        # 2. 计算手牌的胡希
        # 这里需要找出最优的牌型组合来最大化胡希
        # 简化处理：直接查找所有可能的三连牌、四连牌和特殊顺子
        remaining_cards = hand_cards.copy()
        
        # 优先找四连牌（胡希最高）
        quadruplets = PatternMatcher.find_quadruplets(remaining_cards)
        for quad in quadruplets:
            total_huxi += HuxiCalculator.calculate_quadruplet_huxi(quad, is_exposed=False)
            remaining_cards = PatternMatcher.remove_cards_from_list(remaining_cards, quad)
        
        # 然后找三连牌
        triplets = PatternMatcher.find_triplets(remaining_cards)
        for triplet in triplets:
            total_huxi += HuxiCalculator.calculate_triplet_huxi(triplet, is_exposed=False)
            remaining_cards = PatternMatcher.remove_cards_from_list(remaining_cards, triplet)
        
        # 最后找特殊顺子
        sequences = PatternMatcher.find_sequences(remaining_cards)
        for seq in sequences:
            huxi = HuxiCalculator.calculate_sequence_huxi(seq)
            if huxi > 0:  # 只计算特殊顺子
                total_huxi += huxi
                remaining_cards = PatternMatcher.remove_cards_from_list(remaining_cards, seq)
        
        return total_huxi
    
    @staticmethod
    def calculate_win_huxi(all_cards: List[Card], exposed_groups: List[Dict],
                          win_combination: Dict) -> int:
        """
        计算胡牌时的精确胡希
        
        Args:
            all_cards: 所有牌（手牌+摸到的牌）
            exposed_groups: 已亮出的牌组
            win_combination: 胡牌组合（包含triplets, sequences, pair）
        
        Returns:
            总胡希值
        """
        total_huxi = 0
        
        # 1. 已亮出牌组的胡希
        for group in exposed_groups:
            group_type = group['type']
            cards = group['cards']
            
            if group_type == 'peng':
                total_huxi += HuxiCalculator.calculate_triplet_huxi(cards, is_exposed=True)
            elif group_type == 'wei':
                total_huxi += HuxiCalculator.calculate_triplet_huxi(cards, is_exposed=False)
            elif group_type in ['pao', 'ti']:
                is_exposed = (group_type == 'pao')
                total_huxi += HuxiCalculator.calculate_quadruplet_huxi(cards, is_exposed=is_exposed)
            elif group_type == 'chi':
                total_huxi += HuxiCalculator.calculate_sequence_huxi(cards)
        
        # 2. 手牌中的三连牌胡希
        for triplet in win_combination.get('triplets', []):
            total_huxi += HuxiCalculator.calculate_triplet_huxi(triplet, is_exposed=False)
        
        # 3. 手牌中的顺子胡希
        for sequence in win_combination.get('sequences', []):
            total_huxi += HuxiCalculator.calculate_sequence_huxi(sequence)
        
        # 对子不计胡希
        
        return total_huxi
