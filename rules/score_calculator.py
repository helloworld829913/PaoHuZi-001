# -*- coding: utf-8 -*-
"""
得分计算器 - 计算胡牌得分
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.game_config import MIN_HUXI_TO_WIN, BASE_SCORE, HUXI_PER_EXTRA_SCORE


class ScoreCalculator:
    """
    得分计算器
    根据胡希计算最终得分
    """
    
    @staticmethod
    def calculate_score(huxi: int) -> int:
        """
        计算得分
        
        规则：
        - 基础分：1分
        - 额外分：(总胡希 - 15) ÷ 3 的整数部分
        - 公式：得分 = 1 + (总胡希 - 15) // 3
        
        Args:
            huxi: 胡希值
        
        Returns:
            得分
        
        Examples:
            15胡希 → 1 + 0 = 1分
            18胡希 → 1 + 1 = 2分
            22胡希 → 1 + 2 = 3分
            27胡希 → 1 + 4 = 5分
        """
        if huxi < MIN_HUXI_TO_WIN:
            return 0
        
        extra_score = (huxi - MIN_HUXI_TO_WIN) // HUXI_PER_EXTRA_SCORE
        total_score = BASE_SCORE + extra_score
        
        return total_score
    
    @staticmethod
    def get_score_description(huxi: int) -> str:
        """
        获取得分描述
        
        Args:
            huxi: 胡希值
        
        Returns:
            得分描述字符串
        """
        if huxi < MIN_HUXI_TO_WIN:
            return f"{huxi}胡希（未达到15胡希门槛，无法胡牌）"
        
        score = ScoreCalculator.calculate_score(huxi)
        extra = (huxi - MIN_HUXI_TO_WIN) // HUXI_PER_EXTRA_SCORE
        
        if extra == 0:
            return f"{huxi}胡希 → {score}分（基础分）"
        else:
            return f"{huxi}胡希 → {score}分（基础{BASE_SCORE}分 + 额外{extra}分）"
