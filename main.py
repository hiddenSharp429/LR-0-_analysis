"""
@coding : utf-8
@File   : main.py
@Author : zixian Zhu(hiddensharp)
@Date   : 2023/12/10
@Desc   :
@Version:
@Last_editor
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from read_grammar import ReadGrammar


class LR0Parser:
    def __init__(self, grammar):
        # 初始化LR(0)分析器，接收文法作为参数
        self.grammar = grammar
        # 计算闭包和转移函数
        self.compute_closure_goto()

    def closure(self, items):
        '''
        计算闭包函数
        :param items: 当前项目集的集合
        :return:
        '''

        # 初始化闭包集合，包含输入的项目集
        closure_items = set(items)
        # 标志用于迭代，表示是否有项目被添加到闭包中
        changed = True

        # 循环直到没有新的项目添加到闭包中为止
        while changed:
            # 将标志设为 False，表示没有新的项目添加到闭包中
            changed = False

            # 对当前闭包集合中的每个项目进行遍历
            for item in closure_items.copy():
                # 获取项目中点的位置，如果没有点则使用项目的长度作为点的位置
                dot_index = item[1].index('.') if '.' in item[1] else len(item[1])

                # 如果点的位置不在项目的最后一个位置之前
                if dot_index < len(item[1]) - 1:
                    # 获取点后面的符号
                    next_symbol = item[1][dot_index + 1]

                    # 如果该符号在文法中
                    if next_symbol in self.grammar:
                        # 对该符号的每个产生式进行遍历
                        for production in self.grammar[next_symbol]:
                            # 创建一个新项目，将点移动到产生式的开头
                            new_item = (next_symbol, ('.',) + production)
                            # 如果新项目不在闭包中，则添加到闭包中，并将标志设为 True
                            if new_item not in closure_items:
                                closure_items.add(new_item)
                                changed = True

            # 处理以点结尾的项目的闭包
            for item in closure_items.copy():
                dot_index = item[1].index('.') if '.' in item[1] else len(item[1])

                # 如果点在项目的最后一个位置
                if dot_index == len(item[1]) - 1:
                    # 检查状态集中是否已经存在相同的状态
                    if item not in closure_items:
                        # 添加新项目到闭包中，并将标志设为 True
                        closure_items.add(item)
                        changed = True

        # 返回闭包的冻结集合，确保集合是不可变的
        return frozenset(sorted(closure_items))

    def goto(self, items, symbol):
        '''
        计算转移函数
        :param items: 当前项目集的集合
        :param symbol: 转移的符号
        :return:
        '''

        # 初始化转移后的项目集合
        goto_items = set()

        # 对当前项目集合中的每个项目进行遍历
        for item in items:
            # 获取项目中点的位置，如果没有点则使用项目的长度作为点的位置
            dot_index = item[1].index('.') if '.' in item[1] else len(item[1])

            # 如果点的位置不在项目的最后一个位置之前，并且点后的符号与输入的符号相匹配
            if dot_index < len(item[1]) - 1 and item[1][dot_index + 1] == symbol:
                # 创建一个新项目，将点移动到符号的位置
                new_item = (item[0], item[1][:dot_index] + (symbol, '.') + item[1][dot_index + 2:])
                # 将新项目添加到转移后的项目集合中
                goto_items.add(new_item)

        # 调用闭包函数，计算转移后的闭包
        return self.closure(goto_items)

    def compute_closure_goto(self):
        '''
        计算LR(0)项集规范族中所有状态的闭包和转移函数
        :return:
        '''

        # 初始化状态集合和转移字典
        self.states = []
        self.transitions = {}

        # 获取文法中所有出现的符号，包括终结符和非终结符，并按照大小写顺序排列
        all_symbols = sorted(set(
            symbol for production_list in self.grammar.values() for production in production_list for symbol in
            production))

        # 初始化初始项目和初始状态
        initial_item = ('S', ('.', 'E'))
        initial_state = self.closure({initial_item})
        # 将初始状态添加到状态集合中
        self.states.append(initial_state)

        # 使用队列实现广度优先搜索，初始状态入队
        queue = [initial_state]

        # 循环直到队列为空
        while queue:
            # 出队当前状态
            current_state = queue.pop(0)

            # 对文法中的每个符号进行遍历，包括终结符和非终结符
            for symbol in all_symbols:
                # 计算转移后的项目集
                goto_items = self.goto(current_state, symbol)

                # 如果存在转移后的项目集
                if goto_items:
                    # 计算转移后项目集的闭包
                    closure_goto_items = self.closure(goto_items)

                    # 如果闭包非空且不在已有状态集合中
                    if closure_goto_items and closure_goto_items not in self.states:
                        # 将闭包添加到状态集合中
                        self.states.append(closure_goto_items)
                        # 将闭包入队，以便继续搜索
                        queue.append(closure_goto_items)
                        # 记录当前状态到符号的转移关系
                        self.transitions[(current_state, symbol)] = closure_goto_items

    def is_reduce_state(self, state):
        '''
        判断状态是否为规约状态
        :param state: 状态
        :return: 是否为规约状态
        '''
        # 在这里实现判断状态是否为规约状态的逻辑
        for item in state:
            # 获取项目中点的位置，如果没有点则使用项目的长度作为点的位置
            dot_index = item[1].index('.') if '.' in item[1] else len(item[1])

            # 如果点的位置在项目的最后一个位置之前，说明这是规约状态
            if dot_index < len(item[1]) - 1:
                return False

        # 如果没有任何项目的点在最后，说明这是规约状态
        return True

    def get_reduce_production_index(self, state):
        '''
        获取规约状态对应的产生式的索引
        :param state: 规约状态
        :return: 产生式的索引
        '''
        # 在文法中查找该产生式的位置
        for item in state:
            # 获取项目中点的位置，如果没有点则使用项目的长度作为点的位置
            dot_index = item[1].index('.') if '.' in item[1] else len(item[1])

            # 如果点的位置在产生式右部的最后一个位置，说明这是规约状态
            if dot_index == len(item[1]) - 1:
                # 获取规约项目的产生式左右部
                production_left = item[0]
                production_right = item[1][:dot_index]

                production_index = 0 # 产生式子在文法中的索引
                # 在文法中查找该产生式左右两部分均匹配的位置
                for left_symbol, productions in self.grammar.items():
                    for index, production in enumerate(productions):
                        if left_symbol == production_left and production == production_right:
                            return production_index + index
                    production_index += len(productions)


    def print_states(self):
        '''
        打印所有的状态集
        :return:
        '''
        print("LR(0) Parsing States:")
        # 遍历所有状态
        for i, state in enumerate(self.states):
            # 输出当前状态的编号和项目集
            print(f"State {i}: {state}")

    def print_table(self):
        '''
        打印LR(0)分析表
        :return:
        '''
        # 获取文法中所有出现的符号，包括终结符和非终结符
        all_symbols = sorted(set(
            symbol for production_list in self.grammar.values() for production in production_list for symbol in
            production))

        # 分类大小写字符
        uppercase_symbols = sorted(set(symbol for symbol in all_symbols if symbol.isupper()))
        lowercase_symbols = sorted(set(symbol for symbol in all_symbols if symbol.islower()))
        lowercase_symbols.append('#') # 给ACTION表添加一个#列

        all_sorted_symbols = lowercase_symbols + uppercase_symbols
        # 初始化表格
        self.states_table = [[''] * (len(self.states) + 10) for _ in range(len(all_symbols) + 10)]

        # 设置表头
        self.states_table[0][0] = 'states'

        for row in range(len(self.states)):
            self.states_table[row + 1][0] = row

        for col, symbol in enumerate(all_sorted_symbols, start=1):
            self.states_table[0][col] = symbol

        # 填写表格
        for row in range(1, len(self.states) + 1):
            for col in range(1, len(all_sorted_symbols) + 1):
                # 获取当前符号
                current_states = self.states_table[row][0]
                current_symbol = self.states_table[0][col]

                # 如果是规约状态，则填写规约式的序号
                if self.is_reduce_state(self.states[current_states]):
                    production_index = self.get_reduce_production_index(self.states[current_states])

                    if production_index == 0:  # 增广产生式的索引为0
                        # 只有#列才标注acc
                        if current_symbol == '#':
                            cell_value = 'acc'
                        else:
                            cell_value = ''
                    else: # 除了增广产生式以外的情况
                        if current_symbol in lowercase_symbols: # 只填写终结符栏
                            cell_value = 'r' + str(production_index)
                        else:
                            cell_value = ''

                else:
                    # 计算goto
                    goto_state = self.goto(self.states[current_states], current_symbol)

                    # 如果存在goto状态，填写状态编号，并根据符号类型添加前缀
                    if goto_state:
                        # 查找goto_state在self.states中的索引
                        goto_index = self.states.index(goto_state)
                        cell_value = goto_index
                        if current_symbol.islower():
                            cell_value = 'S' + str(cell_value)
                    else:
                        cell_value = ''

                # 将单元格值填写到表格中
                self.states_table[row][col] = cell_value

        # 打印表格
        for row in range(len(self.states) + 1):
            for col in range(len(all_sorted_symbols) + 1):

                print(f"{self.states_table[row][col]:<10}", end='|')
            print()


    def parse_string(self, input_string):
        '''
        使用LR(0)分析表判断输入字符串是否属于文法
        :param input_string: 输入字符串
        :return: 如果是文法中的句子，返回True；否则，返回False
        '''
        # 将输入字符串添加结束符'#'
        input_string += '#'

        # 初始化分析栈，初始状态，和输入字符串索引
        states_stack = [0]
        symbol_stack = ['#']
        input_index = 0

        step = 1  # 步骤计数
        goto_state = ''  # 初始化goto_state

        while True:


            # 获取当前状态和输入符号
            current_state = states_stack[-1]
            current_symbol = input_string[input_index]

            # 查找LR(0)分析表中的动作
            action = self.get_action(current_state, current_symbol)

            # 打印步骤信息
            print(f"步骤{step:<4} | 状态栈: {str(states_stack):<20} | 符号栈: {str(symbol_stack):<30} | "
                  f"输入串: {input_string[input_index:]:<15} | "
                  f"ACTION: {action:<10} | ", end="")

            # 如果动作为空，说明分析表中无对应的动作，字符串不属于文法
            if not action:
                return False

            # 根据动作类型进行处理
            if action.startswith('S'):
                # 移入动作
                next_state = int(action[1:])
                states_stack.append(next_state)
                symbol_stack += input_string[input_index]
                input_index += 1

                print(f"GOTO: ")

            elif action.startswith('r'):
                # 规约动作
                production_index = int(action[1:])
                production = self.get_production_by_index(production_index)

                # 弹出产生式右部的符号
                for _ in range(len(production[1])):
                    states_stack.pop()
                    symbol_stack.pop()


                # 获取规约后的状态
                goto_state = self.get_action(states_stack[-1], production[0])
                states_stack.append(goto_state)
                symbol_stack.append(production[0])

                print(f"GOTO: {goto_state}")

            elif action == 'acc':

                print(f"GOTO: ")
                # 接受动作，字符串属于文法
                return True

            step += 1  # 步骤计数加一

    def get_action(self, state, symbol):
        '''
        根据状态和符号获取LR(0)分析表中的动作
        :param state: 状态
        :param symbol: 符号
        :return: 动作
        '''
        # 如果状态和符号在分析表中有对应的动作，则返回动作，否则返回空字符串
        symbol_index = self.states_table[0].index(symbol)
        state_index = state + 1

        action = self.states_table[state_index][symbol_index]

        return action

    def get_production_by_index(self, production_index):
        '''
        根据产生式的索引获取产生式
        :param production_index: 产生式的索引
        :return: 产生式
        '''
        # 在文法中查找该产生式的位置
        for left_symbol, productions in self.grammar.items():
            for index, production in enumerate(productions):
                if production_index == 0:
                    return left_symbol, production
                production_index -= 1





if __name__ == '__main__':

    # 创建Tkinter根窗口（不显示）
    root = tk.Tk()
    root.withdraw()  # 隐藏Tkinter根窗口

    # 显示自定义提示窗口
    info_message = """
    导入的文件格式示例:
    E -> aA
    E -> bB
    A -> cA
    A -> d
    B -> cB
    B -> d
    """
    messagebox.showinfo("提示", info_message)

    # 弹出文件选择对话框
    grammar_file_path = filedialog.askopenfilename(
        title="选择文件",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )



    # 定义需要读取的文法文件的路径
    # grammar_file_path = 'src/grammar_2.txt'

    # 语法文件不为空
    if(grammar_file_path):
        grammar = ReadGrammar(grammar_file_path)  # 转换为该解析器能读取的字典格式
        lr0_parser = LR0Parser(grammar)  # 创建LR(0)分析器

    while True:
        print("\n选择你想要的功能:")
        print("1. 查看状态集")
        print("2. 查看状态表")
        print("3. 分析字符串")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            lr0_parser.print_states()  # 打印该文法的状态集合
        elif choice == '2':
            print("-------------------------------")
            lr0_parser.print_table()  # 打印LR(0)的状态表
            print("-------------------------------")
        elif choice == '3':
            # 测试字符串 bccd
            input_string = input("Enter the string to parse: ")
            result = lr0_parser.parse_string(input_string)
            if result:
                print(f'该输入串："{input_string}" 属于该文法')
            else:
                print(f'该输入串："{input_string}" 不属于该文法')
        elif choice == '4':
            print("成功退出程序")
            break
        else:
            print("非法数字！")
