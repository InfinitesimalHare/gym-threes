""" Generate three .json tables in /envs/ 
    Generate three test .json tables in gym_threes/testoutput  """
import json
from pathlib import Path

leftTable  = {}
rightTable = {}
scoreTable = {}

testrTable = {}
testlTable = {}
testscoreTable = {}
zeros = []
merges = []*4
def reverse(row:int) -> int:
    # Example: reverse(0xf123) = 0x321f)
    output = ((row & 0xf) <<12) | ((row & 0xf0) <<4) | ((row & 0xf00 )>> 4) | ((row & 0xf000) >> 12)
    return output
def isMerge(input:int)-> int:
    """ input format 0xff, if can merge, output the merge result (recall the board is recorded in hex), else output -1.
    Example: isMerge(0x12) = 3. Here a = 1, b = 2
             isMerge(0x33) = 4
             isMerge(0x03) = -1
             isMerge(0x30) = 3
             Notice that we also require isMerge(0xff) = -1
     """
    a = input >>4 & 0xf
    if a==0:
        return -1
    b = input & 0xf
    if a == b:
        if a>2 and a<15:
            return a+1
        else: 
            return -1 
    else:
        if a+b == 3:
            return 3
        else:
            return -1

if __name__ == "__main__":
    print("Generating reference table for row operation ... ")
# First generate the rightTable
    for row in range(0x10000):
        mask = 0
        isOperable = None
        scoreTable[row] = 0
        if row == 0:
            rightTable[row] = -1
            continue
        for i in range(4):
            digit = row>> 4*i & 0xf
            if digit >2:
                scoreTable[row] += 3**(digit-2)
                
        for i in range(3):
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
        testlTable[hex(row)] = hex(leftTable[row]) if leftTable[row] != -1 else -1
        testrTable[hex(row)] = hex(rightTable[row]) if rightTable[row] != -1 else -1
        testscoreTable[hex(row)] = scoreTable[row]

    folder = Path(__file__).parent
    print(folder)
    with open(folder / 'RightTables.json', 'w') as fp:
        json.dump(rightTable, fp)
    with open(folder / 'LeftTables.json', 'w') as fp:
        json.dump(leftTable, fp)
    with open(folder / 'scoreTables.json', 'w') as fp:
        json.dump(scoreTable, fp)
    testfolder = folder.parent.parent/'testoutput'
    with open(testfolder /'testRTables.json', 'w') as fp:
        json.dump(testrTable, fp)
    with open(testfolder /'testLTables.json', 'w') as fp:
        json.dump(testlTable, fp)
    with open(testfolder /'testScoreTables.json', 'w') as fp:
        json.dump(testscoreTable, fp)