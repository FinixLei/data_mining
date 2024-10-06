#!/usr/bin/python3

"""
FP-Growth FP means frequent pattern
the FP-Growth algorithm needs:
1. FP-tree (class TreeNode)
2. header table (use dict)

This finds frequent itemsets similar to apriori but does not find association rules.
"""

import json
import os
import sys
from pprint import pprint


FPTreeRuleFile = "./fptree_rules.json"

class TreeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

    def display(self, ind=0):
        print("%s%s %d" % ('  '*ind, self.name, self.count))
        for child in self.children.values():
            child.display(ind+1)

    def __str__(self):
        return '(%s, %s)' % (self.name, str(self.count))


class FPTree(object):
    def __init__(self, minSupport, minConfidence, transactions):
        self.minSupport = minSupport
        self.minConfidence = minConfidence
        self.transactions = transactions

    def createTree(self, dataSet):  # create FP-tree from dataset but don't mine
        headerTable = {}
        # go over dataSet twice
        for trans in dataSet:  # first pass counts frequency of occurrence
            for item in trans:
                headerTable[item] = headerTable.get(item, 0) + dataSet[trans]
        for k in list(headerTable.keys()):  # remove items not meeting minSupport
            if headerTable[k] < self.minSupport:
                del(headerTable[k])
        freqItemSet = set(headerTable.keys())
        if len(freqItemSet) == 0:
            return None, None
        # print("freqItemSet: ", freqItemSet)

        #    headerTable example
        #    {
        #       'r': [3, TreeNode('r', 2, anotherTreeNode)],
        #       'z': [5, TreeNode('z', 1, None)],
        #       't': [4, TreeNode('t', 2, anotherTreeNode)]
        #    }
        for k in headerTable:
            headerTable[k] = [headerTable[k], None]  # reformat headerTable to use nodeLink
        # print("headerTable: ", headerTable)

        retTree = TreeNode('Null Set', 1, None)  # Root Node of FP Tree
        for tranSet, count in dataSet.items():   # go through dataset for the 2nd time
            # store one transaction's frequent items in order of count descending
            # localD example: {'r': 3, 's': 4, 't': 5}
            localD = {}
            for item in tranSet:  # put transaction items in order
                if item in freqItemSet:
                    localD[item] = headerTable[item][0]
            if len(localD) > 0:
                # from localD to orderedItems:  {'r': 3, 's': 4, 't': 5} -> ['t', 's', 'r']
                orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]
                self.updateTree(orderedItems, retTree, headerTable, count)  # populate tree with ordered freq itemset
        return retTree, headerTable  # return tree and header table

    def updateTree(self, items, currNode, headerTable, count):
        if items[0] in currNode.children:  # If exists in current node's children, just increment count by one
            currNode.children[items[0]].inc(count)
        else:   # otherwise, create one TreeNode by items[0], then add it to currNode.children
            currNode.children[items[0]] = TreeNode(items[0], count, currNode)
            if headerTable[items[0]][1] is None: # update header table
                headerTable[items[0]][1] = currNode.children[items[0]]
            else:
                tmpTreeNode = headerTable[items[0]][1]
                while tmpTreeNode.nodeLink is not None:
                    tmpTreeNode = tmpTreeNode.nodeLink
                tmpTreeNode.nodeLink = currNode.children[items[0]]

        if len(items) > 1:  # call updateTree() with remaining ordered items
            self.updateTree(items[1::], currNode.children[items[0]], headerTable, count)

    def ascendTree(self, leafNode, prefixPath): # ascends from leaf node to root
        if leafNode.parent is not None:
            prefixPath.append(leafNode.name)
            self.ascendTree(leafNode.parent, prefixPath)

    def findPrefixPath(self, treeNode):  # treeNode comes from header table
        condPats = {}
        while treeNode is not None:
            prefixPath = []
            self.ascendTree(treeNode, prefixPath)
            if len(prefixPath) > 1:
                condPats[frozenset(prefixPath[1:])] = treeNode.count
                # condPats[tuple(prefixPath[1:])] = treeNode.count
            treeNode = treeNode.nodeLink
        return condPats

    def mineTree(self, fpTree, headerTable, preFix, freqItemList):
        # print("headerTable = ", headerTable)
        # sort header table # code has been changed from p[1] to p[0]
        # v is a tuple, including key and value, i.e. (key, value), so v[0] is key, v[1] is value
        bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[0])]
        for basePat in bigL:  # start from bottom of header table
            newFreqSet = preFix.copy()
            newFreqSet.add(basePat)
            # print('finalFrequentItem: %s' % newFreqSet)  # append to set
            freqItemList.append(newFreqSet)
            condPattBases = self.findPrefixPath(headerTable[basePat][1])
            # print('condPattBases: ', basePat, condPattBases)
            # 2. construct cond FP-tree from cond. pattern base
            myCondTree, myHeadTable = self.createTree(condPattBases)
            # print('head from conditional tree: %s' % myHeadTable)
            if myHeadTable is not None: # 3. mine cond. FP-tree
                # print('conditional tree for: ', newFreqSet)
                # myCondTree.display(1)
                # print("---------------------")
                self.mineTree(myCondTree, myHeadTable, newFreqSet, freqItemList)

    def calculate_support(self, item_set):
        count = 0
        for transaction in self.transactions:
            # set(frozenset({str, str}) is still set({str, str})
            if set(item_set).issubset(set(transaction)):
                count += 1
        return count

    def genFrequentItemSetsToCount(self, frequent_item_sets):
        hashResult = {}
        for item in frequent_item_sets:
            hashResult[item] = self.calculate_support(item)
        return hashResult

    def normalGenRule(self, frequent_item_sets, frequent_item_sets_to_count):
        rules = list()
        pprint(frequent_item_sets_to_count)
        for frequent_item_set in frequent_item_sets:
            if len(frequent_item_set) == 1:
                continue
            support_item_set = frequent_item_sets_to_count.get(frequent_item_set, 0)
            if support_item_set == 0:
                print("Abnormal case: %s" % frequent_item_set)
                continue
            for item in frequent_item_set:
                single_item_set = frozenset([item,])
                # print("single_item_set = %s" % single_item_set)
                single_item_set_count = frequent_item_sets_to_count.get(single_item_set, 0)
                if single_item_set_count == 0:
                    print("Abnormal single item set: %s" % item)
                    continue
                confidence = support_item_set / single_item_set_count
                if confidence >= self.minConfidence:
                    sub_set = list(frequent_item_set)
                    sub_set.remove(item)
                    sub_set = frozenset(sub_set)
                    rules.append((sub_set, item, confidence))
        self.printRules(rules)
        return rules

    @staticmethod
    def printRules(rules):
        for rule in rules:
            print("%s => %s, confidence=%.2f%%" % (list(rule[0]), rule[1], 100*rule[2]))

    def createInitSet(self):
        retDict = {}
        for trans in self.transactions:
            fs = frozenset(trans)
            # fs = tuple(sorted(list(set(trans))))  # use tuple other than frozenset for stable order
            retDict[fs] = retDict.get(fs, 0) + 1
        return retDict

    def calculateAndGenRules(self, DisablePrintRules=True):
        initSet = self.createInitSet()
        # print("---------------------")
        # print("Creating Tree...")
        FPtree, HeaderTable = self.createTree(initSet)
        if FPtree is None:
            return []
        # FPtree.display()
        # print("---------------------")
        # print("Mining Tree...")
        FreqList = []
        self.mineTree(FPtree, HeaderTable, set([]), FreqList)
        FreqList = sorted(FreqList, key=lambda x: len(x))

        frequent_item_sets = list()
        for item in FreqList:
            frequent_item_sets.append(frozenset(item))

        frequent_item_sets_to_count = self.genFrequentItemSetsToCount(frequent_item_sets)
        for k, v in frequent_item_sets_to_count.items():
            print("%s: %d" % (k, v))
        print("---------------------")
        print("Start to generate rules...")
        rules = self.normalGenRule(frequent_item_sets, frequent_item_sets_to_count)
        rules =sorted(rules, key=lambda x: x[2], reverse=True)

        # with open(FPTreeRuleFile, 'w') as OUT_FILE:
        #     json.dump(rules, OUT_FILE, indent=4)
        return rules


def loadTransactions():
    transactions = [['r', 'z', 'h', 'j', 'p'],
               ['z', 'y', 'x', 'w', 'v', 'u', 't', 's'],
               ['z'],
               ['r', 'x', 'n', 'o', 's'],
               ['y', 'r', 'x', 'z', 'q', 't', 'p'],
               ['y', 'z', 'x', 'e', 'q', 's', 't', 'm']]

    transactions = [
        ["dounai", "woju"],
        ["woju", "niaobu", "putaojiu", "tiancai"],
        ["dounai", "niaobu", "putaojiu", "chengzhi"],
        ["woju", "dounai", "niaobu", "putaojiu"],
        ["woju", "dounai", "niaobu", "chengzhi"]
    ]

    return transactions

def main():
    transactions = loadTransactions()
    fpt = FPTree(3, 0.3, transactions)
    fpt.calculateAndGenRules()

if __name__ == '__main__':
    main()
