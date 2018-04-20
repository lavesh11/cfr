import functools
from collections import defaultdict

NUM_CARDS = 52
WIN_PATTERN = {
		'HIGH_CARD' : 0,
		'PAIR' : 1,
		'PAIR_PLUS_HIGH_CARD' : 2,
		'PAIR_PLUS_HIGH_SUIT' : 3,
		'COLOR' : 4,
		'COLOR_PLUS_HIGH_CARD' : 5,
		'COLOR_PLUS_HIGH_SUIT' : 6,
		'SEQUENCE' : 7,
		'SEQUENCE_PLUS_HIGH_CARD' : 8,
		'SEQUENCE_PLUS_HIGH_SUIT' : 9,
		'PURE_SEQUENCE' : 10,
		'PURE_SEQUENCE_PLUS_HIGH_CARD' : 11,
		'PURE_SEQUENCE_PLUS_HIGH_SUIT' : 12,
		'TRAIL' : 13,
		'TRAIL_PLUS_HIGH_CARD' : 14,
		'LOW_CARD' : 15 }

MILESTONEHANDS = {
		'TRAIL' :[[ 0, 13, 26 ], [ 9, 22, 48 ], [ 5, 18, 31 ], [ 1, 14, 27 ]],
		'PS' : [[ 39, 50, 51 ], [ 8, 9, 10 ], [ 30, 31, 32 ], [ 14, 15, 16 ]],
		'SEQ' : [[ 26, 38, 50 ], [ 9, 21, 49 ], [ 5, 17, 45 ], [ 16, 27, 41 ]],
		'COLOR' :[[ 13, 23, 25 ], [ 45, 47, 51 ], [ 31, 32, 36 ], [ 1, 2, 4 ]],
		'PAIR':[[ 0, 26, 38 ], [ 9, 35, 47 ], [ 18, 43, 44 ], [ 2, 27, 40 ]],
		'HC':[[ 36, 39, 51 ], [ 32, 34, 51 ], [ 6, 10, 44 ], [ 4, 15, 40 ]]}

HAND_STRENGTH = {
		'HIGH_CARD_LOW': 11,
		'HIGH_CARD_MEDIUM1' : 13,
		'HIGH_CARD_MEDIUM2': 15,
		'HIGH_CARD_HIGH': 17,
		'PAIR_LOW': 21,
		'PAIR_MEDIUM1': 23,
		'PAIR_MEDIUM2': 25,
		'PAIR_HIGH': 27,
		'COLOR_LOW': 31,
		'COLOR_MEDIUM1': 33,
		'COLOR_MEDIUM2': 35,
		'COLOR_HIGH':37,
		'SEQUENCE_LOW': 41,
		'SEQUENCE_MEDIUM1': 43,
		'SEQUENCE_MEDIUM2': 45,
		'SEQUENCE_HIGH': 47,
		'PURE_LOW': 51,
		'PURE_MEDIUM1': 53,
		'PURE_MEDIUM2': 55,
		'PURE_HIGH': 57,
		'TRAIL_LOW': 61,
		'TRAIL_MEDIUM1': 63,
		'TRAIL_MEDIUM2': 65,
		'TRAIL_HIGH': 67
}

def ter(cond, retTrue, retFalse):
	if cond:
		return retTrue
	else:
		return retFalse

class CardSet:
	def __init__(self):
		self.value = [13, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

	def sortByValue(self, cards):
		sortedCards = [-1,-1,-1]
		valueCards = [-1,-1,-1]
		valueCards[0] = self.value[cards[0] % 13]
		valueCards[1] = self.value[cards[1] % 13]
		valueCards[2] = self.value[cards[2] % 13]

		maxIndex = -1
		if valueCards[2] > valueCards[1] :
			if valueCards[2] > valueCards[0]:
				maxIndex = 2
			else:
				maxIndex = 0
		else:
			if valueCards[1] > valueCards[0]:
				maxIndex = 1
			else:
				maxIndex = 0

		sortedCards[0] = cards[maxIndex];

		nextMax = -1

		if maxIndex:
			if maxIndex == 1:
				if valueCards[2] > valueCards[0]:
					nextMax = 2
				else:
					nextMax = 0
			else:
				if valueCards[1] > valueCards[0]:
					nextMax = 1
				else:
					nextMax = 0
		else:
			if valueCards[2] > valueCards[1]:
				nextMax = 2
			else:
				nextMax = 1

		sortedCards[1] = cards[nextMax];

		last = -1
		for i in range(0,3):
			if nextMax == i or maxIndex == i:
				continue
			else:
				last = i;
				break;

		sortedCards[2] = cards[last]
		return sortedCards

	def getCardsValue (self, cards):
		value = [-1,-1,-1]
		value[0] = cards[0] % 13
		value[1] = cards[1] % 13
		value[2] = cards[2] % 13
		return value

	def isTrail(self, a, b, c):
		return (a == b and b == c)

	def isSequence(self, a, b, c):
		if (a == b + 1 and b == c + 1):
			return True
		elif (a == 0):
			return ((b == 12 and c == 11) or (b == 2 and c == 1))
		return False

	def isPair(self, a, b, c):
		return (a == b or b == c or a == c)

	def getCategory(self, cards, pure):
		if (self.isTrail(cards[0], cards[1], cards[2])):
			return WIN_PATTERN['TRAIL']
		elif (self.isSequence(cards[0], cards[1], cards[2])):
			if pure:
				return WIN_PATTERN['PURE_SEQUENCE']
			else :
				return WIN_PATTERN['SEQUENCE']
		elif (pure):
			return WIN_PATTERN['COLOR']
		elif (self.isPair(cards[0], cards[1], cards[2])):
			return WIN_PATTERN['PAIR']
		return WIN_PATTERN['HIGH_CARD']

	def compareByValue(self, cardset1, cardset2):
		if (self.value[cardset1[0]] == self.value[cardset2[0]] and \
				self.value[cardset1[1]] == self.value[cardset2[1]] and \
				self.value[cardset1[2]] == self.value[cardset2[2]]):
			return -1

		if (self.value[cardset1[0]] > self.value[cardset2[0]]):
			return 0
		elif (self.value[cardset1[0]] != self.value[cardset2[0]]):
			return 1
		elif (self.value[cardset1[1]] > self.value[cardset2[1]]):
			return 0
		elif (self.value[cardset1[1]] != self.value[cardset2[1]]):
			return 1
		elif (self.value[cardset1[2]] > self.value[cardset2[2]]):
			return 0
		return 1

	def getPairValue(self,card):
		if (card[0] == card[1]):
			return card[0];
		if (card[1] == card[2]):
			return card[1];
		return card[2]

	def getThirdCard(self, card):
		if (card[0] == card[1]):
			return card[2];
		if (card[1] == card[2]):
			return card[0];
		return card[1];

	def getCardsSuit(self, cards):
		suit = [-1,-1,-1];
		suit[0] = int(cards[0] // 13);
		suit[1] = int(cards[1] // 13);
		suit[2] = int(cards[2] // 13);
		return suit


	def compareCards (self, cCards, oCards):
		#print(cCards, oCards)
		oCards = self.sortByValue(oCards)
		cCards = self.sortByValue(cCards)

		val1 = self.getCardsValue(oCards)
		val2 = self.getCardsValue(cCards)
		suit1 = self.getCardsSuit(oCards)
		suit2 = self.getCardsSuit(cCards)

		pure1 = False
		pure2 = False
		if suit1[0] == suit1[2]:
			pure1 = (suit1[1] == suit1[2])
		else:
			pure1 = False

		if suit2[0] == suit2[2]:
			pure2 = (suit2[1] == suit2[2])
		else:
			pure2 = False

		cat1 = self.getCategory(val1, pure1)
		cat2 = self.getCategory(val2, pure2)

		winnerByValue = self.compareByValue(val1, val2)

		winnerByValue = ter((winnerByValue != -1),(ter((winnerByValue), 0, 1)), -1);

		result = {"winner": winnerByValue, "pattern" : WIN_PATTERN['HIGH_CARD'], "tie": False};
		if (cat1 == cat2):
			if (winnerByValue == -1):
				result["pattern"] = ter((cat1 == WIN_PATTERN['HIGH_CARD']) , cat1 , cat1 + 2);
				index = ter((cat1 == WIN_PATTERN['PAIR']) , ter((val1[0] == val2[0]) , 2 , 0) , 0);
				result["winner"] = 1;
				result["tie"] = True;
			else:
				if (cat1 == WIN_PATTERN['HIGH_CARD']):
					result["pattern"] = cat1
				else:
					if (cat1 == WIN_PATTERN['PAIR']):
						pairValue1 = self.getPairValue(val1);
						pairValue2 = self.getPairValue(val2);
						if (self.value[pairValue2] > self.value[pairValue1]):
							result["winner"] = 0;
						elif (self.value[pairValue1] > self.value[pairValue2]):
							result["winner"] = 1;
						elif (self.value[pairValue1] == self.value[pairValue2]):
							if (self.value[self.getThirdCard(val1)] > self.value[self.getThirdCard(val2)]):
								result["winner"] = 1;
							elif (self.value[self.getThirdCard(val1)] < self.value[self.getThirdCard(val2)]):
								result["winner"] = 0;
							else:
								result["winner"] = 1;
						else:
							result["winner"] = 1
					result["pattern"] = cat1 + 1;
		elif (cat1 > cat2):
			result["pattern"] = cat1;
			result["winner"] = 1;
		else:
			result["pattern"] = cat2;
			result["winner"] = 0;
		return result

	def getCardStrength(self, card):
		card = self.sortByValue(card);
		val1 = self.getCardsValue(card);
		suit1 = self.getCardsSuit(card);
		pure1 = ter((suit1[0] == suit1[2]) ,(suit1[1] == suit1[2]), False)
		return self.getCategory(val1, pure1)

	def getCardStrengthV2 (self, card):
		strength = -1;
		card = self.sortByValue(card);
		hand = self.getCardsValue(card);
		suit = self.getCardsSuit(card);
		color = ter((suit[0] == suit[2]) , (suit[1] == suit[2]), False);

		# milestoneHand2 is > milestoneHand1
		if(self.isTrail(hand[0], hand[1], hand[2])):
			mediumHand2 = MILESTONEHANDS['TRAIL'][1];
			mediumHand1 = MILESTONEHANDS['TRAIL'][2];
			result = self.compareCards(card, mediumHand2);
			if (result["winner"] == 0 ):
				strength = HAND_STRENGTH['TRAIL_HIGH'];
			else:
				result2 = self.compareCards(card, mediumHand1);
				if(result2["winner"] == 0):
					strength = HAND_STRENGTH['TRAIL_MEDIUM2'];
				else:
					strength = HAND_STRENGTH['TRAIL_MEDIUM1']

		elif (self.isSequence(hand[0], hand[1], hand[2]) and color):
			mediumHand2 = MILESTONEHANDS['PS'][1];
			mediumHand1 = MILESTONEHANDS['PS'][2];
			result = self.compareCards(card, mediumHand2);
			if (result["winner"] == 0 ):
				strength = HAND_STRENGTH['PURE_HIGH'];
			else:
				result2 = self.compareCards(card, mediumHand1);
				if(result2["winner"] == 0):
					strength = HAND_STRENGTH['PURE_MEDIUM2'];
				else:
					strength = HAND_STRENGTH['PURE_MEDIUM1']

		elif (self.isSequence(hand[0], hand[1], hand[2])):
			mediumHand2 = MILESTONEHANDS['SEQ'][1];
			mediumHand1 = MILESTONEHANDS['SEQ'][2];
			result = self.compareCards(card, mediumHand2);
			if (result["winner"] == 0 ):
				strength = HAND_STRENGTH['SEQUENCE_HIGH'];
			else:
				result2 = self.compareCards(card, mediumHand1);
				if(result2["winner"] == 0):
					strength = HAND_STRENGTH['SEQUENCE_MEDIUM2'];
				else:
					strength = HAND_STRENGTH['SEQUENCE_MEDIUM1']

		elif (color):
			mediumHand2 = MILESTONEHANDS['COLOR'][1];
			mediumHand1 = MILESTONEHANDS['COLOR'][2];
			result = self.compareCards(card, mediumHand2);
			if (result["winner"] == 0 ):
				strength = HAND_STRENGTH['COLOR_HIGH'];
			else:
				result2 = self.compareCards(card, mediumHand1);
				if(result2["winner"] == 0):
					strength = HAND_STRENGTH['COLOR_MEDIUM2'];
				else:
					strength = HAND_STRENGTH['COLOR_MEDIUM1'];

		elif(self.isPair(hand[0], hand[1], hand[2])):
			mediumHand2 = MILESTONEHANDS['PAIR'][1];
			mediumHand1 = MILESTONEHANDS['PAIR'][2];
			result = self.compareCards(card, mediumHand2);
			if (result["winner"] == 0 ):
				strength = HAND_STRENGTH['PAIR_HIGH'];
			else:
				result2 = self.compareCards(card, mediumHand1);
				if(result2["winner"] == 0):
					strength = HAND_STRENGTH['PAIR_MEDIUM2'];
				else:
					strength = HAND_STRENGTH['PAIR_MEDIUM1'];

		else:
			mediumHand2 = MILESTONEHANDS['HC'][1];
			mediumHand1 = MILESTONEHANDS['HC'][2];
			result = self.compareCards( card, mediumHand2);
			if (result["winner"] == 0 ):
				strength = HAND_STRENGTH['HIGH_CARD_HIGH'];
			else:
				result2 = self.compareCards(card, mediumHand1);
				if(result2["winner"] == 0):
					strength = HAND_STRENGTH['HIGH_CARD_MEDIUM2'];
				else:
					strength = HAND_STRENGTH['HIGH_CARD_MEDIUM1'];

		return strength;

	def getAllHands(self):
		allHands = []
		for first_card in range(0,52):
			for second_card in range (first_card+1, 52):
				for third_card in range (second_card+1, 52):
					allHands.append([first_card, second_card, third_card])
		return allHands

	def compareCardsAndArrangeDesc(self, cards1, cards2):  #comparator to be used in sort()
		cards1List = createList(cards1)
		cards2List = createList(cards2)
		result = self.compareCards(cards1List, cards2List)
		if result['winner'] == 0:
			return -1
		elif result['winner'] == 1:
			return 1
		else:
			return 0

def createList(cards): # convert CardString to cardList to be used in comparrator for card Sort
	retLis = cards.split(":")
	for i in range(len(retLis)):
		retLis[i] = int(retLis[i])
	return retLis

import math
def mycmp(cCards, oCards):
	co = CardSet()
	oCards = co.sortByValue(oCards)
	cCards = co.sortByValue(cCards)

	cCards,oCards = oCards,cCards
	val1 = co.getCardsValue(oCards)
	val2 = co.getCardsValue(cCards)
	suit1 = co.getCardsSuit(oCards)
	suit2 = co.getCardsSuit(cCards)

	pure1 = False
	pure2 = False
	if suit1[0] == suit1[2]:
		pure1 = (suit1[1] == suit1[2])
	else:
		pure1 = False

	if suit2[0] == suit2[2]:
		pure2 = (suit2[1] == suit2[2])
	else:
		pure2 = False

	cat1 = co.getCategory(val1, pure1)
	cat2 = co.getCategory(val2, pure2)

	winnerByValue = co.compareByValue(val1, val2)

	winnerByValue = ter((winnerByValue != -1) ,(ter((winnerByValue) , 0 , 1)), -1)

	result = {"winner": winnerByValue, "pattern" : WIN_PATTERN['HIGH_CARD'], "tie": False}
	if (cat1 == cat2):
		if (winnerByValue == -1):
			result["pattern"] = ter((cat1 == WIN_PATTERN['HIGH_CARD']) , cat1 , cat1 + 2)
			index = ter((cat1 == WIN_PATTERN['PAIR']) , ter((val1[0] == val2[0]) , 2 , 0) , 0)
			result["winner"] = 1
			result["tie"] = True
		else:
			if (cat1 == WIN_PATTERN['HIGH_CARD']):
				result["pattern"] = cat1
			else:
				if (cat1 == WIN_PATTERN['PAIR']):
					pairValue1 = co.getPairValue(val1)
					pairValue2 = co.getPairValue(val2)
					if (co.value[pairValue2] > co.value[pairValue1]):
						result["winner"] = 0
					elif (co.value[pairValue1] > co.value[pairValue2]):
						result["winner"] = 1
					elif (co.value[pairValue1] == co.value[pairValue2]):
						if (co.value[co.getThirdCard(val1)] > co.value[co.getThirdCard(val2)]):
							result["winner"] = 1
						elif (co.value[co.getThirdCard(val1)] < co.value[co.getThirdCard(val2)]):
							result["winner"] = 0
						else:
							result["winner"] = 1
					else:
						result["winner"] = 1
				result["pattern"] = cat1 + 1
	elif (cat1 > cat2):
		result["pattern"] = cat1
		result["winner"] = 1
	else:
		result["pattern"] = cat2
		result["winner"] = 0

	if result["tie"] == True:
		return 0
	elif result["winner"] == 0:
		return -1
	else:
		return 1


def carddict():
	co = CardSet()
	card_list = co.getAllHands()
	card_list = sorted(card_list, key=functools.cmp_to_key(mycmp))
	card_value = defaultdict(int)
	for i in range(len(card_list)):
		card_value[tuple(card_list[i])] = i
	return card_value


card_val = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
card_col = ['♠','♥','♣','♦']

def printcards(l):
	print('cards ---> ', card_val[l[0]%13], card_col[l[0]//13],
		  card_val[l[1]%13], card_col[l[1]//13]
		  , card_val[l[2]%13], card_col[l[2]//13], l)

if __name__=='__main__':
	card_dict = carddict()
	co = CardSet()
	card_list = co.getAllHands()
	card_list = sorted(card_list, key=functools.cmp_to_key(mycmp))
	div = 1
	prev = (1,2,17)
	for x in range(len(card_list)):
		if (tuple(card_list[x]) == (39,50,51)):
			print(x,x/22101)
			printcards((39,50,51))
		# samesuit = (card_col[card_list[x][0]//13] == card_col[card_list[x][1]//13]) and (card_col[card_list[x][0]//13] == card_col[card_list[x][2]//13])
		# val = co.getCategory(co.getCardsValue(co.sortByValue(card_list[x])), samesuit)
		# if val != div:
		# 	print(x/22101, val)
		# 	printcards(prev)
		# 	printcards(card_list[x])
		# 	div = val
		# prev = card_list[x]
	# ct = 0
	# for x in card_dict:
	# 	print(x,card_dict[x])
	# 	ct+=1
	# 	if ct>10:
	# 		break
	# cs = CardSet()
	# # print(' ', cs.getCategory([0,13,26],False))
	# val1 = tuple(cs.getCardsValue(list((26,33,39))))
	# val2 = tuple(cs.getCardsValue(list((17,29,41))))
	# print(val1,val2)
	# print(card_dict[(26,33,39)],card_dict[(17,29,41)])
	# print(card_dict[tuple(sorted(createList("27:0:24")))])