import random
import time
import numpy as np
from lib.cardset import carddict
from collections import defaultdict
Dimension = 17
import json
# Player State
BLIND = 0
SEEN = 1

# Player move
NO_MOVE = -1
CALL = [1,2,3,4,5,6,7,8]  # [1,2,4,8,16,32,64,128]
SHOW = 9
PACK = 0

# Initials
Init_money = 0
Init_boot = 0
Init_boot_normal = 0

# Cards Unknown
Unknown = 0

# moves_list
moves_list_normal = ['Pack', 'Chaal', 'Raise', 'Show']
moves_list_normal_10 = ['Pack', 'Chaal 1', 'Chaal 2', 'Chaal 4', 'Chaal 8', 'Chaal 16', 'Chaal 32', 'Chaal 64', 'Chaal 128', 'Show']

Table = \
    {'P0_state': SEEN, 'P0_move': NO_MOVE, 'P0_money': 0, 'P0_cards': Unknown,
     'P1_state': SEEN, 'P1_move': NO_MOVE, 'P1_money': 0, 'P1_cards': Unknown,
     'Pot_amount': 0, 'Boot': 0, 'Last_player_chaal': 0, 'Last_player_state': BLIND
    }

bucketChips = [
    ('Bucket','Boot','Max Chaal','Max Pot','Min Chips','Max Chips','Expected Max Ratio'),
    (1,5,640/16,5120/16,0,10240,2.00),
    (2,10,1280,10240,10241,20480,2.00),
    (3,20,2560,20480,20481,40960,2.00),
    (4,50,6400,51200,40961,102400,2.00),
    (5,100,12800,102400,102401,204800,2.00),
    (6,200,25600,204800,204801,409600,2.00),
    (7,500,64000,512000,409601,1024000,2.00),
    (8,1000,128000,1024000,1024001,2048000,2.00),
    (9,2000,256000,2048000,2048001,4096000,2.00),
    (10,5000,640000,5120000,4096001,10240000,2.00),
    (11,10000,1280000,10240000,10240001,20480000,2.00),
    (12,20000,2560000,20480000,20480001,40960000,2.00),
    (13,50000,6400000,51200000,40960001,102400000,2.00),
    (14,100000,12800000,102400000,102400001,204800000,2.00),
    (15,200000,25600000,204800000,204800001,409600000,2.00),
    (16,500000,64000000,512000000,409600001,1280000000,2.50),
    (17,1000000,128000000,1024000000,1280000001,3072000000,3.00),
    (18,2000000,256000000,2048000000,3072000001,8192000000,4.00),
    (19,5000000,640000000,5120000000,8192000001,28160000000,5.50),
    (20,10000000,1280000000,10240000000,28160000001,71680000000,7.00),
    (21,20000000,2560000000,20480000000,71680000001,163840000000,8.00)]

boot_to_bucket = {5:1, 10:2, 20:3, 50:4, 100:5, 200:6, 500:7, 1000:8, 2000:9, 5000:10, 10000:11, 20000:12,
                  50000:13, 100000:14, 200000:15, 500000:16, 1000000:17, 2000000:18, 5000000:19, 10000000:20, 20000000:21}

def printTable(Table):
    print('------------STATE------------')
    print('Boot: ', Table['Boot'], ' Pot Amount: ', Table['Pot_amount'])
    print('Player 1 -> Move: ', Table['P0_move'], ' Chips: ', Table['P0_money'], ' Cards: ', Table['P0_cards'])
    print('Player 2 -> Move: ', Table['P1_move'], ' Chips: ', Table['P1_money'], ' Cards: ', Table['P1_cards'])

def mapping_move(cur_state, pid, move):
    if move == 0 or move == 3:
        return move
    boot = cur_state['Boot']
    chaal = cur_state['Last_player_chaal']
    player_state = cur_state['P'+str(pid)+'_state']
    last_player_state = cur_state['Last_player_state']

    if player_state == BLIND:
        chaalAmount = chaal if last_player_state == BLIND else max(boot, chaal/2)
    else:
        chaalAmount = chaal if last_player_state == SEEN else 2*chaal

    if move == 2:
        chaalAmount *= 2

    move = int(chaalAmount/cur_state['Boot']).bit_length()
    return move

def map_cards(card_value):
    if card_value <= 4620:
        return 1
    elif card_value <= 12615:
        return 2
    elif card_value <= 14715:
        return 3
    elif card_value <= 16439:
        return 4
    elif card_value <= 18744:
        return 5
    elif card_value <= 19560:
        return 6
    elif card_value <= 20183:
        return 7
    elif card_value <= 20384:
        return 8
    elif card_value <= 21024:
        return 9
    elif card_value <= 21279:
        return 10
    elif card_value <= 21640:
        return 11
    elif card_value <= 21999:
        return 12
    elif card_value <= 22024:
        return 13
    elif card_value <= 22047:
        return 14
    else:
        return 15


def table_to_input_f28(Table, order, pid):
    '''
        Features: pot, lastChaal, selfCards, selfChips, selfInvested, selfLastChaal, selfState, selfVelocity, otherChips, otherInvested, otherChaal, otherState, otherVelocity
    '''
    input_layer = []

    # adding pot
    input_layer.append(Table['Pot_amount']/Table['Boot'])

    # Adding lastChaal
    input_layer.append(Table['Last_player_chaal']/Table['Boot'])

    # ensuring pid's data inserted next in the input
    order_modified = order[:]
    order_modified.insert(0, pid)
    for id in range(1,6):
        if id not in order_modified:
            order_modified.append(id)

    for id in order_modified:
        # Insert cards only for self
        if id == pid:
            input_layer.append(Table['P'+str(id)+'_cards'])

        # inserting Chips
        input_layer.append(Table['P'+str(id)+'_money']/Table['Boot'])

        # Inserting investment
        input_layer.append(Table['P'+str(id)+'_turn_money']/Table['Boot'])

        # Inserting Chaal
        chaal = 2**(Table['P'+str(id)+'_move'] -1)
        input_layer.append(chaal)

        # Inserting State [SEEN/BLIND]
        input_layer.append(Table['P'+str(id)+'_state'])

        # Inserting Velocity
        if Table['Chaals_played'+str(id)] != 0  and Table['P'+str(id)+'_move'] != 0:
            v_initial = Table['distance'+str(id)]/Table['Chaals_played'+str(id)]
        else:
            v_initial = 0
        input_layer.append(v_initial)

    return input_layer

def distributeCards(numberOfPlayers):
    ret = [[0]*3 for _ in range(numberOfPlayers)]
    cards = [i for i in range(52)]
    for card_number in range(3):
        for player_number in range(numberOfPlayers):
            # print(cards)
            index = random.randrange(len(cards))
            ret[player_number][card_number]=cards.pop(index)
    return ret


def tableToBucket(Table):
    boot = Table['Boot']
    return boot_to_bucket[boot]

def gameover(Table):
    """
    :param Table:
    :return:
        return 0 if game not over yet
        o.w. return I (Player I wins) b/w 1-2
    """
    # print('In game over')
    # printTable(Table)

    total = int(Table['P0_move'] == PACK)+int(Table['P1_move'] == PACK) \
    + int(Table['P0_move'] == SHOW) + int(Table['P1_move'] == SHOW) \
    + int(Table['Pot_amount'] > bucketChips[tableToBucket(Table)][3])

    # print('total: ', total)

    if total == 0:
        return 0
    else:
        if Table['P0_move'] == PACK:
            return 2
        elif Table['P1_move'] == PACK:
            return 1
        if Table['P0_cards'] > Table['P1_cards']:
            return 1
        else:
            return 2

# Assumption Last_player_chaal is considered multiple of boot whereas in case of all_in it need to be different excluding Pack action also
def available_moves(Table, pid):
    """
    :param pid:
    :return:
        returns list of available moves for player pid
    """
    boot = Table['Boot']
    chaal = Table['Last_player_chaal']
    player_state = Table['P'+str(pid)+'_state']
    player_money = Table['P'+str(pid)+'_money']
    last_player_state = Table['Last_player_state']
    bucket = boot_to_bucket[Table['Boot']]

    if player_state == BLIND:
        min_amount = chaal if last_player_state == BLIND else max(boot, chaal/2)
    else:
        min_amount = chaal if last_player_state == SEEN else 2*chaal

    max_amount = min(bucketChips[bucket][2], 2*min_amount)
    if player_state == BLIND:
        max_amount /= 2

    actions = []
    actions.append(1)
    if player_money >= min_amount:
        actions.append(1)
    else:
        actions.append(0)
    if min_amount != min(player_money,max_amount):
        actions.append(1)
    else:
        actions.append(0)
    money_required_show = chaal if last_player_state == SEEN else 2*chaal
    actions.append(int(player_money >= money_required_show))
    return actions

card_dict = carddict()

if __name__ == '__main__':
    print(distributeCards(3))
    # table_to_input(Table, order=[1, 2, 4, 5], pid=3)