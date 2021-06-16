import json
from block_timer.timer import Timer
from pathlib import Path

leftTable  = {}
rightTable = {}
#testrTable = {}
#testlTable = {}
scoreTable = {}
#testscoreTable = {}
zeros = []
merges = []*4
def reverse(row:int) -> int:
    output = ((row & 0xf) <<12) | ((row & 0xf0) <<4) | ((row & 0xf00 )>> 4) | ((row & 0xf000) >> 12)
    return output
def isMerge(input:int)-> int:
    a = input >>4 & 0xf
    if a==0:
        return -1
    b = input & 0xf
    if a == b:
        if a>2:
            return a+1
        else: 
            return -1 
    else:
        if a+b == 3:
            return 3
        else:
            return -1
with Timer(title="Right Table + Score"):
    for row in range(0x10000):
        mask = 0
        isOperable = None
        scoreTable[row] = 0
        if row == 0:
            rightTable[row] = -1
            continue
        for i in range(4):
            digit = row>> 4*i & 0xf
            if digit == 15:
                scoreTable[row] = -1
                break
            elif digit >2:
                scoreTable[row] += 3**(digit-2)
                
        for i in range(4):
            digit = row>> 4*i & 0xf
            mergesum = isMerge(row>> 4*i & 0xff)
            if (isOperable is None) and (digit== 0 or mergesum>0):
                isOperable = True
                if mergesum>0:
                    rightTable[row] = row >> 4*i+8<<4*i+4| mergesum << 4*i |  row & mask
                else: 
                    rightTable[row] = row >> 4*i+4<<4*i| row & mask
                    if rightTable[row] == row:
                        rightTable[row] = -1
            mask = mask << 4 | 0xf
        if isOperable is None:
            rightTable[row] = -1
for row in range(0x10000):
    reverseRow = reverse(row)
    leftTable[row] = reverse(rightTable[reverseRow]) if rightTable[reverseRow] != -1 else -1
    #testlTable[hex(row)] = hex(leftTable[row]) if leftTable[row] != -1 else -1
    #testrTable[hex(row)] = hex(rightTable[row]) if rightTable[row] != -1 else -1
    #testscoreTable[hex(row)] = scoreTable[row]
with Timer(title="Saving all .json files"):
    folder = Path(__file__).parent
    print(folder)
    with open(folder/'RightTables.json', 'w') as fp:
        json.dump(rightTable, fp)
    with open(folder/'LeftTables.json', 'w') as fp:
        json.dump(leftTable, fp)
    with open(folder/'scoreTables.json', 'w') as fp:
        json.dump(scoreTable, fp)
    # with open('testRTables.json', 'w') as fp:
    #     json.dump(testrTable, fp)
    # with open('testLTables.json', 'w') as fp:
    #     json.dump(testlTable, fp)
    # with open('testScoreTables.json', 'w') as fp:
    #     json.dump(testscoreTable, fp)
if __name__ == "__main__":
    print("Generating reference table for row operation ... ")