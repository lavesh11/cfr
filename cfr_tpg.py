from collections import defaultdict
import random
import lib.game as game
from lib.cardset import carddict
import copy
import numpy as np
import time
import sys
import pickle
# potAmount, currentChaal and last actions for the last 2 rounds
sys.setrecursionlimit(2000)

Log = False
PACK = 0
CALL = 1
RAISE = 2
SHOW = 3
NUM_ACTIONS = 4
nodeMap = {}
card_dict = carddict()

def actionChar(action):
    if action == PACK:
        return 'p'
    elif action == CALL:
        return 'c'
    elif action == RAISE:
        return 'r'
    else:
        return 's'

def currentState():
    train_for_buckets = [1]
    train_for_bucket = random.choice(train_for_buckets)
    cur_state = copy.deepcopy(game.Table)
    # distributing cards
    cardsTuple = game.distributeCards(numberOfPlayers=2)
    for i in range(len(cardsTuple)):
        cur_state['P'+str(i)+'_cards'] = card_dict[tuple(sorted(cardsTuple[i]))]
    # distributing money
    for player in range(2):
        cur_state['P'+str(player)+'_money'] = random.randint(game.bucketChips[train_for_bucket][4], game.bucketChips[train_for_bucket][5])
    cur_state['Boot'] = game.bucketChips[train_for_bucket][1]
    cur_state['Last_player_chaal'] = cur_state['Boot']
    cur_state['Last_player_state'] = game.SEEN
    return cur_state

def performAction(cur_state, player, a):
    if a == PACK:
        cur_state['P'+str(player)+'_move'] = game.PACK
    elif a == CALL or a == RAISE:
        temp_move = game.mapping_move(cur_state, player, a)
        amt = int(np.math.pow(2,temp_move-1)) * cur_state['Boot']
        cur_state['P'+str(player)+'_move'] = temp_move
        cur_state['P'+str(player)+'_money'] -= amt
        cur_state['Last_player_chaal'] = amt
        cur_state['Pot_amount'] += amt
    else:
        cur_state['P'+str(player)+'_move'] = 9
        cur_state['P'+str(player)+'_money'] -= cur_state['Last_player_chaal']
        cur_state['Pot_amount'] += cur_state['Last_player_chaal']
    return cur_state

def toInput(cur_state, player, history):
    # ret = str(game.map_cards(cur_state['P'+str(player)+'_cards'])) + history
    ret = str(game.map_cards(cur_state['P'+str(player)+'_cards'])) + '-' + str(cur_state['Pot_amount']//cur_state['Boot'])
    ret = ret + '-' + str(cur_state['Last_player_chaal']//cur_state['Boot']) + history
    return ret

class KuhnTrainer(object):
    class Node:
        def __init__(self):
            self.infoSet = ""
            self.regretSum = [0.0]*NUM_ACTIONS
            self.strategy = [0.0]*NUM_ACTIONS
            self.strategySum = [0.0]*NUM_ACTIONS

        def getStrategy(self, realizationWeight, cur_state, pid):
            normalizingSum = 0
            available_moves = game.available_moves(cur_state, pid)
            for a in range(NUM_ACTIONS):
                self.strategy[a] = self.regretSum[a] if (self.regretSum[a] > 0 and available_moves[a]) else 0
                normalizingSum += self.strategy[a]
            for a in range(NUM_ACTIONS):
                if (normalizingSum > 0):
                    self.strategy[a] /= normalizingSum
                else:
                    self.strategy[a] = (1.0*available_moves[a]) / sum(available_moves)
                self.strategySum[a] += realizationWeight * self.strategy[a]
            return self.strategy
        

        def getAverageStrategy(self):
            avgStrategy = [0.0]*NUM_ACTIONS
            normalizingSum = 0
            for a in range(NUM_ACTIONS):
                normalizingSum += self.strategySum[a]
            for a in range(NUM_ACTIONS):
                if (normalizingSum > 0):
                    avgStrategy[a] = self.strategySum[a] / normalizingSum
                else:
                    avgStrategy[a] = 1.0 / NUM_ACTIONS
            return avgStrategy
        

        def toString(self):
                return String.format("%4s: %s", self.infoSet, Arrays.toString(getAverageStrategy()))

    def train(self, iterations):
        util = 0.0
        for i in range(iterations):
            if i and i % 100000 == 0:
                input_file = 'cfrStrategy'+str(i)+'.pickle'
                with open(input_file, 'wb') as f:
                    pickle.dump(nodeMap,f)
                ct = 0
                for k,n in nodeMap.items():
                    ct+=1
                    if ct > 10:
                        break
                    print(k, n.getAverageStrategy())
            cur_state = currentState()
            if Log:
                game.printTable(cur_state)
            player = 0
            util += self.cfr(player, cur_state, "", 1, 1)
        
        print("Average game value: ",util / iterations)
        print("iterations: ", iterations)
        print(len(nodeMap))
        ct = 0
        for k,n in nodeMap.items():
            ct+=1
            if ct > 10:
                break
            print(k, n.getAverageStrategy())
    
    def cfr(self, player, cur_state, history, p0, p1):
        opponent = 1 - player
        gameEnd = game.gameover(cur_state)
        winner = gameEnd-1
        if Log:
            print('player chance: ', player)
            print('history: ', history)
            # game.printTable(cur_state)
            print('Game over: ', gameEnd)
            time.sleep(1)

        if gameEnd:
            if Log:
                print('Return!!!')
            return 1 if player == winner else -1

        infoSet = toInput(cur_state, player, history)
        node = nodeMap.get(infoSet)
        if (node == None):
            node = self.Node()
            node.infoSet = infoSet
            nodeMap[infoSet] = node

        strategy = node.getStrategy(p0 if player == 0 else p1, cur_state, player)

        if Log:
            print('strategy: ', strategy)
        util = [0.0]*NUM_ACTIONS
        nodeUtil = 0.0
        for a in range(NUM_ACTIONS):
            nextHistory = history + actionChar(a)
            if len(nextHistory) > 4:
                nextHistory = nextHistory[1:]
            modified_state = performAction(copy.deepcopy(cur_state), player, a)
            util[a] = -self.cfr(opponent, modified_state, nextHistory, p0 * strategy[a], p1) if player == 0 else -self.cfr(opponent, modified_state, nextHistory, p0, p1 * strategy[a])
            nodeUtil += strategy[a] * util[a]

        for a in range(NUM_ACTIONS):
            regret = util[a] - nodeUtil
            node.regretSum[a] += (p1 if player == 0 else p0) * regret

        return nodeUtil

if __name__ == '__main__':
        iterations = 2000000
        KuhnTrainer().train(iterations)
