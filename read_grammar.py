"""
@coding : utf-8
@File   : read_grammar.py
@Author : zixian Zhu(hiddensharp)
@Date   : 2023/12/10
@Desc   : 返回一个能够给lr0分析器分析的字典并自动变成增广文法
@Version:
@Last_editor
"""

import re

class ReadGrammar(dict):
    def __init__(self, grammar_file_path):
        super().__init__()
        self.file_path = grammar_file_path
        self.translate()
        self.add_augmented_production()

    def translate(self):
        # 从文件中读取规则
        with open(self.file_path, 'r', encoding='utf-8') as file:
            rules = file.readlines()

        # 遍历每一条规则
        for rule in rules:
            # 使用正则表达式匹配规则的左部和右部
            match = re.match(r'\s*(\w+)\s*->\s*(.+)\s*', rule)
            if match:
                left = match.group(1)
                right = match.group(2)

                # 如果左部非终结符还不存在于字典中，则添加
                if left not in self:
                    self[left] = []

                # 将右部按照单个字符拆分并添加到左部的规则中
                productions = [symbol for symbol in right]
                self[left].append(tuple(productions))

    def add_augmented_production(self):
        # 获取原始文法的起始符号
        original_start_symbol = list(self.keys())[0]

        # 生成新的起始符号
        new_start_symbol = 'S'

        # 创建新的字典，将新的起始产生式添加到新的字典中
        new_dict = {new_start_symbol: [(original_start_symbol,)]}

        # 将原始字典的内容添加到新的字典后面
        new_dict.update(self)

        # 将新的字典设置为当前字典
        self.clear()
        self.update(new_dict)

        # 返回新的起始符号
        return new_start_symbol

if __name__ == '__main__':
    # 定义需要读取的文法文件的路径
    grammar_file_path = 'src/grammar_2.txt'  # 使用非拓广的文法

    # 转换为该解析器能读取的字典格式
    grammar_reader = ReadGrammar(grammar_file_path)

    print("Original Grammar:")
    print(grammar_reader)

