# search optimization

## Quiescence Search

https://www.chessprogramming.org/Quiescence_Search

- Quiescence Search（静态搜索）是博弈树搜索中的一个优化技术，尤其常用于像国际象棋这样的对抗性游戏中，来解决所谓的“视野地平线效应（horizon effect）”问题。
- 为什么需要 Quiescence Search？
    - 在常规的 Alpha-Beta 剪枝搜索中，我们搜索到某一个深度（比如 5 步）就会停止，然后用评估函数来评估当前局面。但是，有些局面在表面看起来还不错，但再往前走一步就会发生剧烈变化（比如丢子、将军、吃子等），这时我们就会因为没搜索到那个“突变”而错误地评估局面。
    - 这就是视野地平线效应——因为我们不能“看得更远”，所以错误地高估了一个实际上会崩盘的局面。
- Quiescence Search 的核心思想
    - 只在“宁静”（Quiescent）的位置停止搜索。在搜索到达普通最大深度之后，如果当前局面不稳定（比如还有可能吃子、被将军等），我们就继续深入搜索这些“战术性变招”，直到局面变得稳定为止。
    - 这个补充搜索过程就是 Quiescence Search。
- 怎么实现（概念上）
    - 在正常 Alpha-Beta 搜索达到最大深度 d 时，检查当前局面是否“宁静”。
    - 如果局面不宁静（例如当前有吃子、将军等操作）：
        - 继续搜索这些战术性走法（如吃子），直到局面变得宁静为止。
    - 如果局面已经“宁静”了，则调用评估函数进行评估。
    ```

for project4

- Evaluating at a fixed depth can leave a board position in the middle of a capture(吃子) exchange
- At a 'leaf' node, continue the search using only captures -- **quiet** the position
- Each side has the option of "standing pat."


## Best-first Order in Alpha-Beta pruning

Theorem [KM75]. For a game tree with branching factor b and depth d, an alpha-beta search with moves searched in **best-first order** takes b^(d/2) + b^(d/2) -1 nodes at ply d, almostly square-rooted.

- Variation: Principal Variation Search Pruning
    - PVS 要求走法排序效果好，否则会频繁触发重搜索，反而降低性能。
    - 它和 Alpha-Beta 剪枝、Iterative Deepening（迭代加深）、Move Ordering（走法排序） 等一起使用效果最好。
    - 在现代棋类引擎（如 Stockfish）中，PVS 是基本标配。


## MOVE ORDERING

- Alpha-Beta 剪枝的效率很大程度上依赖于走法排序（Move Ordering）。
- putting the best move at the front to trigger an early cutoff.
- How do we determine which moves are best without evaluation at every level.
    - moves are represented in 28bits, if we want to make them sortable, we use 64 bits, and use the upper 32 as the sort key.


## Transposition Table

- Chess programs often encounter the same position repeatedly during their search.
- A transposition table stores results of previous searches in a hash table to avoid unnecessary work.
- normally a hash table, which value pointers to another structure which contains the computed result of this position.
    - e.g. best move, evaluation, alpha, beta, etc.

## Zobrist Hashing

- Zobrist Hashing 是一种专为棋盘类游戏设计的哈希技术，通过预生成随机数和异或操作实现高效的哈希值更新，适用于快速状态比较和重复检测。以下是其详细说明：
- 核心思想
    - 预生成随机数表：为棋盘每个位置的所有可能状态（包括棋子类型、颜色及空）生成唯一随机数。
    - XOR 操作更新：通过XOR旧状态和新状态的随机数快速更新哈希值，避免重新计算整个棋盘。
- 实现步骤
    1. 初始化随机数表：
        - 创建三(二)维数组 Z[(x,y)][state]，其中x,y (pos) 表示棋盘位置，state 表示可能的状态（如棋子类型、颜色或空）。
        - 使用高质量伪随机数生成器（如64位或128位数）填充该表，确保不同状态对应的随机数独立且均匀分布。
    2. 初始哈希计算：
        - 遍历棋盘每个位置，根据当前状态选择对应的随机数。
        - 将所有随机数进行异或操作，得到初始哈希值。
    3. 更新哈希值：
        - 当棋盘状态发生变化时（如棋子移动），找到旧状态和新状态对应的随机数。
        - 使用异或操作更新哈希值：`hash = hash ^ Z[i][j][old_state] ^ Z[i][j][new_state]`。
        - 例如，棋子从位置A移动到B： 
            - 移除A的原棋子：hash = hash ^= Z[A][原棋子]
            - 添加A的空状态：hash = hash ^= Z[A][空]
            - 移除B的空状态: hash = hash ^= Z[B][空]
            - 添加B的新棋子: hash = hash ^= Z[B][新棋子]
- 关键特性
    - 高效性：每次状态更新仅需常数时间（O(1)），适合频繁变动的游戏局面。
    - 可逆性：异或操作可逆，便于撤销移动（如回溯搜索）。
    - 低冲突概率：使用足够长的随机数（如64位）降低不同状态哈希冲突概率。
- 示例（国际象棋）
    - 随机数表：8x8棋盘，每个位置对应12种棋子（6种类型×2种颜色）和空状态，共13种状态。
    - 初始哈希：遍历初始布局，异或所有位置的对应随机数。
    - 移动更新：移动棋子时异或旧位置和新位置的随机数，吃子时额外异或被吃棋子随机数。
- 注意事项
    - 随机数质量：需确保随机数独立均匀分布，避免可预测性。
    - 冲突处理：哈希表需存储额外信息（如校验和或完整状态）以应对极少数冲突。
    - 状态完整性：若游戏规则包含额外状态（如易位权、过路兵），需扩展哈希计算以涵盖这些信息。
- 变体与扩展
    - 组合键：结合玩家轮次等信息生成复合哈希键，区分相同局面的不同游戏阶段。



