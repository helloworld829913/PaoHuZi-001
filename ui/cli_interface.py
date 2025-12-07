# -*- coding: utf-8 -*-
"""
命令行界面
"""

from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.player import Player
from core.card import Card
from core.game import Game
from ai.ai_player import AIPlayer


class CLIInterface:
    """
    命令行界面
    负责显示游戏信息和接收用户输入
    """
    
    @staticmethod
    def display_welcome():
        """显示欢迎信息"""
        print("\n" + "="*60)
        print(" " * 20 + "跑胡子游戏")
        print("="*60)
        print("\n游戏规则：")
        print("  - 3人游戏（1个真人玩家 + 2个AI玩家）")
        print("  - 胡牌需要达到15胡希")
        print("  - 得分 = 1 + (胡希-15)÷3")
        print("  - 吃只能吃上家，碰跑可以碰跑任何玩家")
        print("\n" + "="*60 + "\n")
    
    @staticmethod
    def display_player_hand(player: Player, show_all: bool = True):
        """
        显示玩家手牌
        
        Args:
            player: 玩家
            show_all: 是否显示所有信息（AI玩家只显示部分）
        """
        print(f"\n【{player.name}的手牌】")
        
        if player.is_human or show_all:
            # 显示手牌
            player.hand.sort_cards()
            
            # 按颜色分组显示
            red_cards = [c for c in player.hand.cards if c.is_red()]
            black_cards = [c for c in player.hand.cards if not c.is_red()]
            
            if red_cards:
                print(f"  红牌({len(red_cards)}张): {' '.join(str(c) for c in sorted(red_cards))}")
            if black_cards:
                print(f"  黑牌({len(black_cards)}张): {' '.join(str(c) for c in sorted(black_cards))}")
            
            # 显示摸到的牌
            if player.hand.drawn_card:
                print(f"  摸到: 【{player.hand.drawn_card}】")
            
            # 显示已亮牌组
            if player.hand.exposed_groups:
                print("\n  【已亮牌组】")
                for group in player.hand.exposed_groups:
                    group_type = group['type']
                    cards = group['cards']
                    is_concealed = group.get('is_concealed', False)
                    
                    type_name = {
                        'chi': '吃',
                        'peng': '碰',
                        'pao': '跑',
                        'wei': '委',
                        'ti': '提'
                    }.get(group_type, group_type)
                    
                    if is_concealed:
                        print(f"    [{type_name}] ???（暗牌）")
                    else:
                        cards_str = ' '.join(str(c) for c in cards)
                        print(f"    [{type_name}] {cards_str}")
            
            print(f"\n  总牌数: {player.hand.get_total_count()}张")
        else:
            # AI玩家只显示牌数
            print(f"  手牌: {player.hand.get_card_count()}张")
            if player.hand.drawn_card:
                print(f"  摸到: 1张")
            
            # 显示已亮牌组
            if player.hand.exposed_groups:
                print("\n  【已亮牌组】")
                for group in player.hand.exposed_groups:
                    group_type = group['type']
                    cards = group['cards']
                    is_concealed = group.get('is_concealed', False)
                    
                    type_name = {
                        'chi': '吃',
                        'peng': '碰',
                        'pao': '跑',
                        'wei': '委',
                        'ti': '提'
                    }.get(group_type, group_type)
                    
                    if is_concealed:
                        print(f"    [{type_name}] ???（暗牌）")
                    else:
                        cards_str = ' '.join(str(c) for c in cards)
                        print(f"    [{type_name}] {cards_str}")
    
    @staticmethod
    def display_all_players(game: Game):
        """显示所有玩家信息"""
        print(f"\n{'='*60}")
        print(f"第{game.round_number}局 - 剩余牌数: {game.deck.get_remaining_count()}张")
        print(f"{'='*60}")
        
        for i, player in enumerate(game.players):
            is_current = (i == game.current_player_idx)
            marker = ">>> " if is_current else "    "
            print(f"{marker}{player}")
        
        print(f"{'='*60}\n")
    
    @staticmethod
    def ask_discard_card(player: Player) -> Card:
        """
        询问玩家要打哪张牌
        
        重要规则：如果有摸到的牌（drawn_card），且没有进行委、提等操作，
        则必须打掉摸到的牌，不能打手牌中的其他牌。
        
        Args:
            player: 玩家
        
        Returns:
            要打出的牌
        """
        # 如果有摸到的牌，必须打掉摸到的牌
        if player.hand.drawn_card:
            print(f"\n你必须打掉刚摸到的牌：【{player.hand.drawn_card}】")
            input("按回车键继续...")
            return player.hand.drawn_card
        
        # 如果没有摸到的牌（说明进行了委、提等操作），可以打手牌中的任意牌
        while True:
            print("\n请选择要打出的牌：")
            
            # 显示可选的牌（只有手牌）
            available_cards = player.hand.cards.copy()
            available_cards.sort()
            
            # 整合显示：序号.牌面
            print("  ", end="")
            for i, card in enumerate(available_cards):
                print(f"{i+1}.{card} ", end="")
            print()  # 换行
            
            try:
                choice = int(input(f"\n请输入序号 (1-{len(available_cards)}): ").strip())
                if 1 <= choice <= len(available_cards):
                    return available_cards[choice - 1]
                else:
                    print("无效的选择，请重新输入")
            except ValueError:
                print("请输入有效的数字")
            except KeyboardInterrupt:
                print("\n游戏中断")
                sys.exit(0)
    
    @staticmethod
    def display_game_over(game: Game):
        """显示游戏结束信息"""
        print("\n" + "="*60)
        print(" " * 20 + "游戏结束")
        print("="*60)
        
        # 按分数排序
        sorted_players = sorted(game.players, key=lambda p: p.score, reverse=True)
        
        print("\n最终排名：")
        for i, player in enumerate(sorted_players, 1):
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else "🥉")
            print(f"{medal} {i}. {player.name}: {player.score}分")
        
        print("\n" + "="*60 + "\n")
    
    @staticmethod
    def ask_continue() -> bool:
        """询问是否继续游戏"""
        while True:
            choice = input("\n是否继续下一局？(y/n): ").strip().lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            else:
                print("请输入 y 或 n")
