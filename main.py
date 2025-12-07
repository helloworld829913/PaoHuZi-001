# -*- coding: utf-8 -*-
"""
跑胡子游戏 - 主程序入口
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game import Game
from ui.cli_interface import CLIInterface
from ai.ai_player import AIPlayer


def main():
    """主函数"""
    # 显示欢迎信息
    CLIInterface.display_welcome()
    
    # 创建游戏实例
    game = Game()
    
    try:
        # 游戏主循环
        while True:
            # 开始新一局
            game.start_new_round()
            
            # 局内循环
            while not game.is_game_over():
                current_player = game.get_current_player()
                
                # 显示当前玩家手牌
                CLIInterface.display_player_hand(current_player, show_all=current_player.is_human)
                
                # 处理玩家回合
                if not game.handle_player_turn(current_player):
                    break
                
                # 玩家打牌
                if current_player.is_human:
                    # 真人玩家选择打牌
                    card_to_discard = CLIInterface.ask_discard_card(current_player)
                    discarded = current_player.discard_card(card_to_discard)
                else:
                    # AI玩家决策打牌
                    action, param = current_player.decide_after_draw()
                    if action == 'discard':
                        discarded = current_player.discard_card(param)
                    elif action == 'win':
                        # AI胡牌已在handle_player_turn中处理
                        break
                    else:
                        # 如果AI做了委或提，需要继续打牌
                        action2, param2 = current_player.decide_after_draw()
                        if action2 == 'discard':
                            discarded = current_player.discard_card(param2)
                        else:
                            # 安全措施：如果还没决定打牌，随机打一张
                            all_cards = current_player.hand.cards.copy()
                            if current_player.hand.drawn_card:
                                all_cards.append(current_player.hand.drawn_card)
                            if all_cards:
                                discarded = current_player.discard_card(all_cards[0])
                            else:
                                break
                
                # 检查其他玩家响应（吃/碰/跑）
                has_response = game.handle_discard(current_player, discarded)
                
                # 如果有人响应，当前玩家已经切换
                # 否则切换到下一个玩家
                if not has_response:
                    game.next_player()
            
            # 本局结束
            game.end_round()
            
            # 询问是否继续
            if not CLIInterface.ask_continue():
                break
        
        # 显示游戏结束信息
        CLIInterface.display_game_over(game)
        print("感谢游玩！")
    
    except KeyboardInterrupt:
        print("\n\n游戏被中断，感谢游玩！")
    except Exception as e:
        print(f"\n发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
