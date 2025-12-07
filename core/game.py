# -*- coding: utf-8 -*-
"""
游戏主控制器
"""

import random
from typing import List, Optional, Tuple, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.deck import Deck
from core.player import Player
from core.card import Card
from ai.ai_player import AIPlayer
from rules.score_calculator import ScoreCalculator
from config.game_config import (
    NUM_PLAYERS, NUM_AI_PLAYERS, NUM_HUMAN_PLAYERS,
    INITIAL_HAND_SIZE, DEALER_EXTRA_CARD
)


class Game:
    """
    游戏主控制器
    管理整个游戏流程
    """
    
    def __init__(self):
        """初始化游戏"""
        self.deck = Deck()
        self.players: List[Player] = []
        self.current_player_idx = 0
        self.dealer_idx = 0
        self.last_discarded_card: Optional[Card] = None
        self.last_discard_player_idx: Optional[int] = None
        self.game_over = False
        self.winner: Optional[Player] = None
        self.round_number = 0
        self.just_responded = False  # 标记当前玩家是否刚刚响应了别人的打牌（吃/碰/跑）
        
        self._init_players()
    
    def _init_players(self):
        """初始化玩家"""
        # 创建1个真人玩家
        self.players.append(Player(
            player_id=0,
            name="玩家1",
            is_human=True
        ))
        
        # 创建2个AI玩家
        for i in range(NUM_AI_PLAYERS):
            self.players.append(AIPlayer(
                player_id=i + 1,
                name=f"AI{i + 1}"
            ))
    
    def start_new_round(self):
        """开始新一局"""
        self.round_number += 1
        print(f"\n{'='*50}")
        print(f"第 {self.round_number} 局开始")
        print(f"{'='*50}\n")
        
        # 重置牌堆
        self.deck.reset()
        
        # 清空玩家手牌
        for player in self.players:
            player.reset_hand()
        
        # 设置庄家
        self.players[self.dealer_idx].set_dealer(True)
        self.current_player_idx = self.dealer_idx
        
        # 发牌
        self._deal_initial_cards()
        
        # 庄家摸第一张牌
        dealer = self.players[self.dealer_idx]
        first_card = self.deck.draw()
        dealer.draw_card(first_card)
        
        print(f"庄家：{dealer.name}")
        print(f"剩余牌数：{self.deck.get_remaining_count()}张\n")
        
        self.game_over = False
        self.winner = None
        self.last_discarded_card = None
    
    def _deal_initial_cards(self):
        """发初始手牌"""
        for player in self.players:
            cards = self.deck.deal(INITIAL_HAND_SIZE)
            player.hand.add_cards(cards)
            player.hand.sort_cards()
    
    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.players[self.current_player_idx]
    
    def next_player(self):
        """切换到下一个玩家"""
        self.current_player_idx = (self.current_player_idx + 1) % NUM_PLAYERS
    
    def handle_player_turn(self, player: Player) -> bool:
        """
        处理玩家回合
        
        Args:
            player: 当前玩家
        
        Returns:
            True如果游戏继续，False如果游戏结束
        """
        # 如果玩家刚刚吃/碰/跑，不需要摸牌，直接打牌即可
        if self.just_responded:
            self.just_responded = False  # 重置标志
            return True
        
        # 如果不是庄家且没有摸牌，先摸牌
        if not player.hand.has_drawn_card():
            if self.deck.is_empty():
                print("牌堆已空，流局！")
                return False
            
            card = self.deck.draw()
            player.draw_card(card)
            # 只有摸牌后才显示剩余牌数（其他操作如吃碰跑不减少牌堆数量）
            print(f"\n[剩余牌数: {self.deck.get_remaining_count()}张]\n")
        
        # 检查摸牌后的操作（委、提、胡牌）
        result = self._handle_after_draw(player)
        
        if result == 'win':
            self.winner = player
            self.game_over = True
            return False
        elif result == 'continue':
            # 需要打出一张牌
            pass
        
        return True
    
    def _handle_after_draw(self, player: Player) -> str:
        """
        处理摸牌后的操作
        
        Returns:
            'win': 胡牌
            'continue': 继续（需要打牌）
        """
        # 检查胡牌
        can_win, huxi, combination = player.can_win()
        if can_win:
            if player.is_human:
                print(f"\n🎉 恭喜！你可以胡牌！")
                print(f"胡希：{huxi}")
                score = ScoreCalculator.calculate_score(huxi)
                print(f"得分：{score}分")
                choice = input("是否胡牌？(y/n): ").strip().lower()
                if choice == 'y':
                    return 'win'
            else:
                # AI玩家自动胡牌
                return 'win'
        
        # 检查提
        if player.can_ti():
            if player.is_human:
                print(f"\n你可以提【{player.hand.drawn_card}】")
                choice = input("是否提？(y/n): ").strip().lower()
                if choice == 'y':
                    player.do_ti()
                    print(f"✓ 提了 {player.hand.exposed_groups[-1]['cards'][0]} (四连牌)")
                    return 'continue'
            else:
                # AI决策
                action, param = player.decide_after_draw()
                if action == 'ti':
                    player.do_ti()
                    print(f"{player.name} 提了 {player.hand.exposed_groups[-1]['cards'][0]} (四连牌)")
                    return 'continue'
        
        # 检查委
        if player.can_wei():
            if player.is_human:
                print(f"\n你可以委【{player.hand.drawn_card}】")
                choice = input("是否委？(y/n): ").strip().lower()
                if choice == 'y':
                    player.do_wei()
                    print("✓ 委了（暗牌，其他人看不见）")
                    return 'continue'
            else:
                # AI决策
                action, param = player.decide_after_draw()
                if action == 'wei':
                    player.do_wei()
                    print(f"{player.name} 委了（暗牌）")
                    return 'continue'
                else:
                    # AI不能委或选择不委，显示摸到的牌
                    print(f"{player.name} 摸到：【{player.hand.drawn_card}】")
        else:
            # 不能委，显示AI摸到的牌
            if not player.is_human:
                print(f"{player.name} 摸到：【{player.hand.drawn_card}】")
        
        return 'continue'
    
    def handle_discard(self, player: Player, card: Card) -> bool:
        """
        处理打牌
        
        Args:
            player: 玩家
            card: 打出的牌
        
        Returns:
            True如果有人吃/碰/跑，False继续
        """
        self.last_discarded_card = card
        self.last_discard_player_idx = self.current_player_idx
        
        print(f"\n{player.name} 打出：【{card}】")
        
        # 询问其他玩家是否要吃/碰/跑
        return self._check_responses_to_discard(card, player)
    
    def _check_responses_to_discard(self, card: Card, discard_player: Player) -> bool:
        """
        检查其他玩家对打出牌的响应
        
        重要规则：
        - 碰和跑：可以碰/跑任何玩家的牌
        - 吃：只能吃上家打出的牌
        
        Returns:
            True如果有人响应
        """
        # 按顺序询问其他玩家（优先级：跑 > 碰 > 吃）
        responses = []
        
        # 确定打牌玩家的下家（也就是可以吃这张牌的玩家）
        next_player_idx = (self.last_discard_player_idx + 1) % NUM_PLAYERS
        
        for i, player in enumerate(self.players):
            if player == discard_player:
                continue
            
            # 判断是否是下家（可以吃牌）
            can_chi = (i == next_player_idx)
            
            if player.is_human:
                response = self._ask_human_response(player, card, can_chi)
                if response[0] != 'pass':
                    responses.append((i, response))
            else:
                # AI决策
                response = player.decide_on_discard(card)
                # 如果AI想吃但不是下家，忽略吃的决策
                if response[0] == 'chi' and not can_chi:
                    response = ('pass', None)
                if response[0] != 'pass':
                    responses.append((i, response))
        
        # 处理响应（优先级：跑 > 碰 > 吃）
        if responses:
            # 排序：跑>碰>吃
            priority = {'pao': 3, 'peng': 2, 'chi': 1}
            responses.sort(key=lambda x: priority.get(x[1][0], 0), reverse=True)
            
            player_idx, (action, param) = responses[0]
            acting_player = self.players[player_idx]
            
            if action == 'pao':
                acting_player.do_pao(card)
                print(f"{acting_player.name} 跑了【{card}】(四连牌)")
                self.current_player_idx = player_idx
                self.just_responded = True  # 标记玩家刚刚响应了打牌
                return True
            elif action == 'peng':
                acting_player.do_peng(card)
                print(f"{acting_player.name} 碰了【{card}】")
                self.current_player_idx = player_idx
                self.just_responded = True  # 标记玩家刚刚响应了打牌
                return True
            elif action == 'chi':
                acting_player.do_chi(card, param)
                print(f"{acting_player.name} 吃了【{card}】")
                self.current_player_idx = player_idx
                self.just_responded = True  # 标记玩家刚刚响应了打牌
                return True
        
        return False
    
    def _ask_human_response(self, player: Player, card: Card, can_chi: bool = True) -> Tuple[str, Any]:
        """
        询问真人玩家的响应
        
        Args:
            player: 玩家
            card: 打出的牌
            can_chi: 是否可以吃（只有上家可以吃）
        """
        options = []
        option_map = {}
        
        if player.can_pao(card):
            options.append(f"跑【{card}】")
            option_map[len(options)] = ('pao', None)
        
        if player.can_peng(card):
            options.append(f"碰【{card}】")
            option_map[len(options)] = ('peng', None)
        
        # 只有上家可以吃
        if can_chi:
            chi_options = player.can_chi(card)
            if chi_options:
                # 去重：使用set来存储已经见过的组合
                seen_combinations = set()
                for chi_cards in chi_options:
                    # 将两张牌排序后转换为字符串作为唯一标识
                    sorted_cards = sorted(chi_cards, key=lambda c: (c.value, c.is_red()))
                    combination_key = f"{sorted_cards[0]}_{sorted_cards[1]}"
                    
                    if combination_key not in seen_combinations:
                        seen_combinations.add(combination_key)
                        options.append(f"吃【{card}】+ {sorted_cards[0]} {sorted_cards[1]}")
                        option_map[len(options)] = ('chi', chi_cards)
        
        if not options:
            return ('pass', None)
        
        print(f"\n{player.name}，别人打出【{card}】，你可以：")
        # 将"过"设为选项0
        print(f"0. 过")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        
        while True:
            try:
                choice = int(input("请选择: ").strip())
                if choice == 0:
                    return ('pass', None)
                elif 1 <= choice <= len(options):
                    return option_map[choice]
            except:
                pass
            print("无效选择，请重新输入")
    
    def end_round(self):
        """结束本局"""
        if self.winner:
            can_win, huxi, combination = self.winner.can_win()
            score = ScoreCalculator.calculate_score(huxi)
            self.winner.add_score(score)
            
            print(f"\n{'='*50}")
            print(f"🎉 {self.winner.name} 胡牌！")
            print(f"胡希：{huxi}")
            print(f"本局得分：{score}分")
            print(f"{'='*50}\n")
            
            # 连庄判断
            if self.winner.is_dealer:
                print(f"{self.winner.name} 连庄！")
            else:
                # 换庄
                self.dealer_idx = self.winner.player_id
        else:
            # 流局，换庄
            self.dealer_idx = (self.dealer_idx + 1) % NUM_PLAYERS
        
        # 显示当前分数
        print("当前分数：")
        for player in self.players:
            print(f"  {player}")
    
    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self.game_over
