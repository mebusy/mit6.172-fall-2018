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


## killer-move table

- 通过“记住”曾引发剪枝的强力移动，让程序在后续搜索中优先尝试这些走法，从而显著减少计算量。这是国际象棋引擎实现高效搜索的核心技术之一。
    - the table is indexed by ply, because you tend to see the same moves at the same depth.
    - the killer move table, basically, just stores moves that tirgger the beta cutoff in your search.
- 工作原理示例
    - 假设程序在搜索深度为 5 的节点时，发现移动 Nf3（马走到 f3）触发了 beta 剪枝（即该移动足够好，无需继续搜索其他分支）。此时：
        - Killer-move table 会在深度 5 的记录中保存 Nf3。
        - 当程序搜索同一层（深度 5）的其他分支时，会优先尝试 Nf3，而不是按默认顺序（如兵、马、象等）遍历所有可能移动。


## BEST MOVE table

- The best move is stored at the root of a search and is the move that gained the maximum score.
- The best-move table is indexed by color, piece, square, and orientation

## Null-Move Pruning

- 空着剪枝 通过模拟一方“放弃走棋”（即走一步“空着”）来判断当前局面是否足够安全，从而跳过对该节点的深入搜索。
- 其核心思想是：如果一方即使让对手连续走两步（自己走一步空着），对手仍无法改善局面，那么当前局面大概率已足够好，可以提前剪枝。
- 核心原理
    - 空着（Null Move）的定义
        - 在搜索过程中，假设当前轮到某一方（例如白方）走棋，但白方选择“不走任何步”（即空着），直接让对手（黑方）连续走两步。如果即使在这种极端不利的情况下（白方放弃一步），黑方仍然无法找到比当前已知的评估值更好的结果，则可以判定当前节点的搜索价值较低，直接剪枝。
    - 剪枝条件
        - 空着后的对手响应搜索值 ≥ β
        - 其中 β 是当前 alpha-beta 剪枝的上界。如果对手在连续走两步后仍无法突破 β，说明当前局面已经足够好，无需继续搜索。
    - 搜索深度调整（R值）
        - 为避免剪枝过度，空着后的对手响应搜索会减少深度（通常减少 2-3 层）。例如：
            - 原始搜索深度为 depth，空着后的搜索深度为 depth - R（R 通常取 2 或 3）。
- 简化版的 Null-Move Pruning 实现逻辑：
    ```python
    NULL_MOVE_R = 2  # 空着剪枝的深度减少量（通常取 2 或 3）
    def value(state, alpha, beta, depth, can_null_move):
        if state.is_terminal():
            return state.utility()
        if state.next_player() == MAX:
            return max_value(state, alpha, beta, depth, can_null_move)
        else:
            return min_value(state, alpha, beta, depth, can_null_move)

    def max_value(state, alpha, beta, depth, can_null_move):
        # 尝试空着剪枝（仅在 MAX 层触发）
        if can_null_move and depth >= NULL_MOVE_R + 1:
            # 走空着：让 MIN 连续走两次（深度减少 R）
            null_state = state.apply_null_move()  # 模拟 MAX 不走棋，直接轮到 MIN
            null_eval = value(null_state, beta, beta, depth - NULL_MOVE_R - 1, can_null_move=False)
            if null_eval >= beta:
                return beta  # 剪枝

        # 正常搜索 MAX 的移动
        v = -inf
        for move in state.generate_moves():
            next_state = state.apply_move(move)
            v = max(v, value(next_state, alpha, beta, depth - 1, can_null_move=True))
            if v >= beta:
                return v  # Beta 剪枝
            alpha = max(alpha, v)
        return v

    def min_value(state, alpha, beta, depth, can_null_move):
        # MIN 层不应用空着剪枝（通常仅用于 MAX 层）
        v = inf
        for move in state.generate_moves():
            next_state = state.apply_move(move)
            v = min(v, value(next_state, alpha, beta, depth - 1, can_null_move=True))
            if v <= alpha:
                return v  # Alpha 剪枝
            beta = min(beta, v)
        return v
    ```
    - 禁止连续空着
        - 为避免无限递归（例如双方反复走空着），通常限制空着剪枝后必须至少走一步真实移动后才能再次使用空着（通过参数 can_null_move 控制）。
    - 残局禁用
        - 在残局中，空着剪枝可能导致漏算关键将杀路径（例如逼和或长将），因此某些引擎会在剩余棋子较少时关闭此技术。
    - Zugzwang 局面的风险
        - Zugzwang（被迫走劣招的局面）是空着剪枝的主要弱点。例如，如果当前局面下“不走棋”反而更好，但引擎强制剪枝，可能导致评估错误。因此，引擎通常结合其他技术（如检查是否处于 zugzwang 敏感阶段）来规避风险。
- 实际效果
    - 加速搜索：空着剪枝可减少 30%-50% 的节点搜索量，显著提升引擎速度。
    - 适用场景：对非 zugzwang 的中局和复杂局面效果最佳。
    - 典型实现：Stockfish、Komodo 等主流引擎均使用空着剪枝，但会根据局面动态调整 R 值或禁用条件。
- 触发场景示例
    - 假设白方当前 alpha = +1.5，beta = +2.0：
    - 1. 白方尝试空着
        - 黑方连走两步后的局面，从黑方（MIN）视角评估为 -2.5（即白方优势 +2.5）。
        - 转换为白方（MAX）视角：null_value = 2.5。
    - 2. 剪枝判断
        - null_value >= beta → 2.5 >= 2.0 → 成立。
        - 触发剪枝，不再搜索白方的实际走法。

## Futility Pruning

- 无用剪枝, 提前终止对“无希望分支”
- 核心思想是：如果某个节点的评估值（即使加上乐观估计的增益）仍无法改变当前剪枝边界（alpha/beta），则无需浪费计算资源继续搜索该分支。
- 核心原理
    1. 基本假设
        - 在博弈树搜索中，当搜索到某一节点时，如果当前局面的静态评估值（Static Evaluation）与预期最大可能增益（Margin）之和仍无法突破当前玩家的剪枝边界（alpha 或 beta），则认为继续搜索该分支是“无用的”（Futile），可以直接剪枝。
    2. 适用范围
        - 通常用于 叶子节点附近（剩余搜索深度较浅，如 depth <= 1）。
        - 主要针对非关键路径（非主变路径，Non-PV Nodes）。
        - 常用于 Min节点（对手回合）的剪枝，因为对手的目标是最小化我方收益。
    3. 数学条件
        - 对 Min 节点剪枝（对手回合）： 
            - 如果 `eval(state) + margin <= alpha`，则剪枝。
            - 若成立，则对手无法通过后续走法将局面恶化到 alpha 以下，直接剪枝。
        - 对 Max 节点剪枝（我方回合）：
            - 如果 `eval(state) - margin >= beta`，则剪枝。
            - 若成立，则我方无法通过后续走法将局面优化到 beta 以上，直接剪枝。
- 实际应用与优化
    - 边际值（Margin）通常与剩余深度成正比，例如： margin = 100 x depth
        - 深度越大，允许的增益范围越广，避免过度剪枝。
    - 排除高风险移动
        - 对吃子、将军、升变等可能大幅改变局面的移动，禁用 Futility Pruning。
    - 结合其他技术
        - 与静态搜索（Quiescence Search）结合，确保剪枝后局面的“稳定性”（避免因未计算吃子而漏算关键变化）。
    - 残局处理
        - 在残局中，由于单兵升变等微小优势可能决定胜负，通常减小边际或禁用剪枝。
- 代码示例（伪代码）
    ```python
    def futility_pruning(state, alpha, beta, depth, is_max_node):
        static_eval = evaluate(state)
        margin = 150 * depth  # 定义安全边际

        if is_max_node:
            # Max 节点：若 static_eval - margin >= beta，剪枝
            if static_eval - margin >= beta:
                return beta
        else:
            # Min 节点：若 static_eval + margin <= alpha，剪枝
            if static_eval + margin <= alpha:
                return alpha

        # 不满足条件，继续正常搜索
        return None
    ```

## Late-Move Reduction

- 对排序靠后的移动（Late Moves）减少搜索深度，从而大幅减少计算量
- 核心原理
    1. 基本假设
        - 假设移动排序良好，前面的移动通常更有可能触发剪枝。
        - 排序靠后的移动（Late Moves） 通常质量较低，即使跳过或浅层搜索，也不太可能改变最终结果。
    2. 操作逻辑
        - 对每个节点的移动列表，先全深度搜索前 N 个高优先级移动（如杀手着法、吃子、将军）。
        - 对后续的 Late Moves，减少其搜索深度（例如从剩余深度 d 缩减为 d-1 或 d-2）。
        - 若某个被缩减的移动意外表现出色（如大幅提升 alpha），则重新以全深度搜索（称为 re-search）。
- 实现步骤
    1. 生成并排序移动
        1. 置换表最佳移动（来自历史缓存）
        2. 吃子/将军移动（按 MVV-LVA 排序）
        3. 杀手着法（Killer Moves）
        4. 历史启发式高分移动
        5. 其他移动
    2. 动态缩减深度
        ```python
        # 全局常量
        LMR_CUTOFF = 3      # 前 N 个移动不缩减深度
        LMR_REDUCTION = 1   # 缩减的深度层数

        def value(state, alpha, beta, depth, can_reduce):
            if state.is_terminal():
                return state.utility()
            if state.next_player() == MAX:
                return max_value(state, alpha, beta, depth, can_reduce)
            else:
                return min_value(state, alpha, beta, depth, can_reduce)

        def max_value(state, alpha, beta, depth, can_reduce):
            # 生成所有合法移动，并按优先级排序（例如：置换表移动 → 吃子 → 杀手着法 → 历史启发式）
            moves = order_moves(state.generate_moves(), state)  # 假设已实现排序逻辑
            
            best_value = -inf
            for i, move in enumerate(moves):
                # 动态决定是否应用 LMR（非前 N 个移动且允许缩减）
                reduced = False
                search_depth = depth - 1  # 默认全深度
                
                if can_reduce and i >= LMR_CUTOFF and depth >= LMR_REDUCTION + 1:
                    search_depth = depth - 1 - LMR_REDUCTION
                    reduced = True
                
                # 递归搜索子节点
                next_state = state.apply_move(move)
                current_value = value(next_state, alpha, beta, search_depth, can_reduce=True)
                
                # 如果缩减搜索后触发 alpha 提升，重新以全深度搜索
                if reduced and current_value > alpha:
                    current_value = value(next_state, alpha, beta, depth - 1, can_reduce=False)
                
                # 更新 alpha 和 best_value
                best_value = max(best_value, current_value)
                alpha = max(alpha, best_value)
                
                # Beta 剪枝
                if alpha >= beta:
                    break
            
            return best_value

        def min_value(state, alpha, beta, depth, can_reduce):
            moves = order_moves(state.generate_moves(), state)
            
            best_value = inf
            for i, move in enumerate(moves):
                # 对 MIN 层同样应用 LMR（可选，根据引擎设计）
                reduced = False
                search_depth = depth - 1
                
                if can_reduce and i >= LMR_CUTOFF and depth >= LMR_REDUCTION + 1:
                    search_depth = depth - 1 - LMR_REDUCTION
                    reduced = True
                
                next_state = state.apply_move(move)
                current_value = value(next_state, alpha, beta, search_depth, can_reduce=True)
                
                if reduced and current_value < beta:
                    current_value = value(next_state, alpha, beta, depth - 1, can_reduce=False)
                
                best_value = min(best_value, current_value)
                beta = min(beta, best_value)
                
                if beta <= alpha:
                    break
            
            return best_value

        # 辅助函数：按优先级排序移动
        def order_moves(moves, state):
            # 实现排序逻辑（示例：优先置换表移动 → 吃子 → 杀手着法 → 历史启发式）
            ordered = []
            # 1. 提取置换表建议的最佳移动（若有）
            tt_move = state.transposition_table.get_move()
            if tt_move in moves:
                ordered.append(tt_move)
                moves.remove(tt_move)
            # 2. 吃子/将军移动按 MVV-LVA 排序
            ordered += sorted([m for m in moves if m.is_capture()], key=lambda m: -m.mvv_lva_score())
            # 3. 添加其他移动（杀手着法、历史启发式等）
            ordered += [m for m in moves if not m.is_capture()]
            return ordered
        ```
    3. 关键参数
        - LMR_CUTOFF：前 N 个移动不缩减（通常取 2-4）。
        - LMR_REDUCTION：深度缩减量（通常为 1-2 层，随剩余深度动态调整）。
        - Re-search 条件：若缩减后的搜索值超过当前 alpha，重新全深度搜索。
- 示例分析
    - 场景：当前节点剩余深度为 6（depth=6），生成 10 个移动。
    - 前 3 个移动（吃子、杀手着法）以深度 5 搜索。
    - 后 7 个移动缩减为深度 4 搜索。
    - 假设第 5 个移动（缩减深度后）返回 value=120，超过当前 alpha=100：
        - 重新以深度 5 搜索该移动，最终返回 value=150，更新 alpha。
    - 若后续移动无法超越 alpha=150，则触发剪枝。
- 优化与注意事项
    - 动态调整缩减量
        - 剩余深度越大，缩减量可增加（例如 depth >= 6 时缩减 2 层，depth=3 时缩减 1 层）。
        - 在 主变路径（PV Nodes） 禁用 LMR，避免漏算关键路径。
    - 特殊局面的处理
        - 将军局面：即使被标记为 Late Move，仍需全深度搜索，避免漏算将杀。
        - 残局：减少缩减强度（因微小优势可能决定胜负）。
    - 与历史启发式协同
        - 结合历史得分（History Heuristic）优化移动排序，确保高潜力移动优先，提升剪枝效率。
- 实际效果
    - 加速效果：LMR 可减少 30%-50% 的节点搜索量，对深层搜索尤为显著。
    - 准确性保障：通过 Re-search 机制，重要移动即使被误判为 Late Move，仍有机会全深度搜索。


## Opening book 开局库

- 预存的开局走法数据库，包含了大量经过人工或算法验证的高质量开局变例。

## End game tablebase 残局库

- 残局数据库（Endgame Tablebase），也叫 Tablebase，是一个包含所有可能的残局局面（通常是 3~7 个子）和这些局面的最优解的数据库。对每一个局面，Tablebase 告诉你：
    - 局面是 胜、和、负
    - 离胜利/失败还有多少步（例如：Mate in 5）
        - make sure that you maintain the distance in order to avoid cycling.
    - 最佳的走法（在某些格式中）
- e.g.
    - King Versus King
    - King Versus King and Pawn
        - who will win ? 
        - how many moves to win ?



## Iterative Deepening

- 迭代加深（Iterative Deepening）是一种搜索算法，结合了深度优先搜索和广度优先搜索的优点，适用于博弈树搜索中的 Alpha-Beta 剪枝。
- 其核心思想是：在每个搜索深度上进行深度优先搜索，逐步增加搜索深度，直到达到预设的最大深度或时间限制。
- 迭代加深的基本步骤
    1. 从深度 1 开始，进行深度优先搜索。
    2. 每次搜索完成后，增加搜索深度（例如：从 1 增加到 2、3、4...）。
    3. 在每个深度上，使用 Alpha-Beta 剪枝来优化搜索。
    4. 如果达到时间限制或最大深度，则停止搜索。
    5. 返回最佳走法和评估值。
- 迭代加深的优点
    - 1. 提供了一个渐进的搜索过程，可以在时间限制内找到最佳走法。
    - 2. 可以利用之前的搜索结果来优化后续的搜索（例如：使用置换表）。
    - 3. 在时间限制内，能够找到接近最佳解的走法。
- 迭代加深的缺点
    - 1. 可能会浪费时间在较低深度的搜索上，尤其是在时间限制较短时。
    - 2. 对于非常深的搜索树，可能需要较长的时间来完成搜索。


## Also applicable to MCTS

- Move Ordering（移动排序）
    - 应用方式：在 MCTS 的 选择（Selection） 阶段，优先访问历史胜率高或探索价值大的子节点。
    - 技术调整：
        - 使用 历史启发式（History Heuristic） 或 置换表建议的移动 对子节点排序。
        - 类似 UCT 公式的改进（如 RAVE 或 Progressive Bias），结合静态评估值引导移动选择。
- Transposition Table（置换表）
    - 应用方式：在不同路径到达相同局面时，共享节点的统计信息（访问次数、胜率）。
    - 技术调整：
        - 使用 Zobrist 哈希 识别相同局面。
        - 合并多个父节点对同一子节点的访问数据，加速收敛。
- Best-Move Table（最佳着法表）
    - 应用方式：在节点中记录历史模拟中的最佳移动，并在选择阶段优先探索。
    - 技术调整：
        - 维护每个节点的「最佳候选移动」，类似 MCTS 的 AMAF（All Moves As First） 或 RAVE 技术。
- Quiescence Search（静态搜索）
    - 应用方式：在 模拟（Simulation） 阶段，对不稳定局面（如吃子、将军）进行更深入的静态评估，而非随机走子。
    - 技术调整：
        - 在模拟中引入「有限深度搜索」或「动态终止条件」，避免评估函数误判。


