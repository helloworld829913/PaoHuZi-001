# -*- coding: utf-8 -*-
"""
游戏配置文件
"""

# 游戏基础配置
NUM_PLAYERS = 3  # 玩家数量
NUM_AI_PLAYERS = 2  # AI玩家数量
NUM_HUMAN_PLAYERS = 1  # 真人玩家数量

# 牌局配置
TOTAL_CARDS = 80  # 总牌数
INITIAL_HAND_SIZE = 20  # 初始手牌数
DEALER_EXTRA_CARD = 1  # 庄家额外摸牌数

# 胡牌配置
MIN_HUXI_TO_WIN = 15  # 最低胡希门槛
BASE_SCORE = 1  # 基础分
HUXI_PER_EXTRA_SCORE = 3  # 每3胡希额外得1分

# 牌的配置
CARD_VALUES = list(range(1, 11))  # 1-10
RED_CARD_VALUES = [2, 7, 10]  # 红色牌的值

# 显示名称映射
LOWERCASE_NAMES = {
    1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
    6: '六', 7: '七', 8: '八', 9: '九', 10: '十'
}

UPPERCASE_NAMES = {
    1: '壹', 2: '贰', 3: '叁', 4: '肆', 5: '伍',
    6: '陆', 7: '柒', 8: '捌', 9: '玖', 10: '拾'
}

# 特殊顺子配置
SPECIAL_SEQUENCES = [
    [1, 2, 3],  # 一二三
    [2, 7, 10]  # 二七十
]
