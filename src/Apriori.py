#!/usr/bin/python3

import os
import sys
from pprint import pprint


class Apriori(object):
    def __init__(self, minSupport, minConfidence, transactions):
        self.minSupport = minSupport
        self.minConfidence = minConfidence
        self.transactions = transactions

    def calculate_support(self, item_set):
        count = 0
        for transaction in self.transactions:
            if set(item_set).issubset(set(transaction)):
                count += 1
        return count

    def genOneFrequentItemSet(self):
        # a set of all items
        single_item_set = set([item for transaction in self.transactions for item in transaction])

        # a list of frozenset-s, each contains one item
        candidate_1 = [frozenset([item]) for item in single_item_set]

        # a list of frozenset-s, each contains one item, and each satisfies minSupport
        one_frequent_item_set_list = [one_item_frozenset for one_item_frozenset in candidate_1
                                      if self.calculate_support(one_item_frozenset) >= self.minSupport]
        one_frequent_item_list = [list(item)[0] for item in one_frequent_item_set_list]
        return one_frequent_item_set_list, one_frequent_item_list

    def genFrequentItemSets(self, one_frequent_item_frozenset_list, one_frequent_item_list):
        # a list of frozenset-s
        frequent_item_sets = one_frequent_item_frozenset_list.copy()
        result = one_frequent_item_frozenset_list.copy()

        k = 2
        while len(frequent_item_sets) != 0:
            # a list of frozenset-s, each contains k items
            candidate_k = list()
            for frequent_item_set in frequent_item_sets:
                for item in one_frequent_item_list:
                    if item not in frequent_item_set:
                        tmp_list = list(frequent_item_set)
                        tmp_list.append(item)
                        candidate_k.append(frozenset(tmp_list))

            # remove redundancy, still a list of frozenset-s, each contains k items
            candidate_k = list(set(candidate_k))

            # a list of frozenset-s
            frequent_item_sets = [item_set for item_set in candidate_k
                                  if self.calculate_support(item_set) >= self.minSupport]
            # print("K=%d, frequent_item_set: %s" % (k, frequent_item_sets))
            if len(frequent_item_sets) == 0:
                break
            result += frequent_item_sets
            k += 1

        return result

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
        return rules

    def printRules(self, rules):
        for rule in rules:
            print("%s -> %s, confidence = %.2f%%" % (rule[0], rule[1], 100*rule[2]))

    def calculateAndGenRules(self):
        one_frequent_item_frozenset_list, one_frequent_item_list = self.genOneFrequentItemSet()

        # a list of frozenset-s
        frequent_item_sets = self.genFrequentItemSets(one_frequent_item_frozenset_list, one_frequent_item_list)

        for item_set in frequent_item_sets:
            print(item_set)
        print("--------------------")

        frequent_item_sets_to_count = self.genFrequentItemSetsToCount(frequent_item_sets)
        
        for k, v in frequent_item_sets_to_count.items():
            print("%s: %d" % (k, v))
        print("--------------------")
        print("Generating rules...")
        rules = self.normalGenRule(frequent_item_sets, frequent_item_sets_to_count)
        rules = sorted(rules, key=lambda x: x[2], reverse=True)
        self.printRules(rules)
        return rules


transactions = [
        {"dounai", "woju"},
        {"woju", "niaobu", "putaojiu", "tiancai"},
        {"dounai", "niaobu", "putaojiu", "chengzhi"},
        {"woju", "dounai", "niaobu", "putaojiu"},
        {"woju", "dounai", "niaobu", "chengzhi"}
    ]


def main():
    minSupport = 3
    minConfidence = 0.7
    ap = Apriori(minSupport, minConfidence, transactions)
    ap.calculateAndGenRules()

if __name__ == '__main__':
    main()
