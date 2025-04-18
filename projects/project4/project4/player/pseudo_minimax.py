import math
from collections import defaultdict

# ----------------------
# 常量与全局数据结构
# ----------------------
INF = math.inf
NULL_MOVE_R = 2  # 空着剪枝深度缩减量
LMR_CUTOFF = 3  # LMR 前 N 个移动不缩减
MAX_DEPTH = 4  # 最大搜索深度
FUTILITY_MARGIN = 150  # 无用剪枝安全边际（centipawns）


# 置换表项结构（简化版）
class TTEntry:
    def __init__(self, depth, value, flag, best_move):
        self.depth = depth  # 存储时的搜索深度
        self.value = value  # 评估值
        self.flag = flag  # 标志: 'EXACT', 'LOWER', 'UPPER'
        self.best_move = best_move  # 该节点的最佳移动


# 全局数据结构
transposition_table = dict()  # 置换表：{zobrist_key: TTEntry}
killer_moves = defaultdict(list)  # 杀手着法表：{depth: [move1, move2]}
history_heuristic = defaultdict(int)  # 历史启发式表：{(from_sq, to_sq): score}


# ----------------------
# 核心搜索函数
# ----------------------
def alpha_beta_search(state, depth):
    # 初始化搜索
    best_move = None
    alpha = -INF
    beta = INF
    value = -INF

    # 生成根节点移动并排序
    moves = order_moves(state.generate_moves(), state, depth, [])

    # 遍历所有移动
    for move in moves:
        next_state = state.apply_move(move)
        # 递归搜索
        current_value = value = min_value(
            next_state, alpha, beta, depth - 1, can_null_move=True
        )
        # 更新最佳移动
        if current_value > value:
            value = current_value
            best_move = move
        # Alpha 更新
        alpha = max(alpha, value)

    return best_move, value


def max_value(state, alpha, beta, depth, can_null_move):
    # ------------
    # 1. 置换表查询
    # ------------
    zobrist_key = state.zobrist_hash()
    tt_entry = transposition_table.get(zobrist_key)
    if tt_entry and tt_entry.depth >= depth:
        if tt_entry.flag == "EXACT":
            return tt_entry.value
        elif tt_entry.flag == "LOWER":
            alpha = max(alpha, tt_entry.value)
        elif tt_entry.flag == "UPPER":
            beta = min(beta, tt_entry.value)
        if alpha >= beta:
            return tt_entry.value

    # ------------
    # 2. 终止条件
    # ------------
    if state.is_terminal():
        return state.utility()

    # ------------
    # 3. 静态搜索 (Quiescence Search)
    # ------------
    if depth <= 0:
        return quiescence_search(state, alpha, beta)

    # ------------
    # 4. 空着剪枝 (Null-Move Pruning)
    # ------------
    if can_null_move and depth >= (NULL_MOVE_R + 1) and not state.in_check():
        # 尝试空着
        null_state = state.apply_null_move()
        null_value = min_value(
            null_state, beta - 1, beta, depth - NULL_MOVE_R - 1, can_null_move=False
        )
        if null_value >= beta:
            return beta  # 剪枝

    # ------------
    # 5. 无用剪枝 (Futility Pruning)
    # ------------
    if depth == 1:  # 浅层节点
        static_eval = evaluate(state)
        if static_eval - FUTILITY_MARGIN >= beta:
            return static_eval  # 直接剪枝

    # ------------
    # 6. 生成并排序移动
    # ------------
    moves = order_moves(state.generate_moves(), state, depth, killer_moves[depth])

    best_value = -INF
    best_move = None

    for i, move in enumerate(moves):
        # ------------
        # 7. Late-Move Reduction (LMR)
        # ------------
        reduction = 0
        if (
            i >= LMR_CUTOFF
            and depth >= 3
            and not move.is_capture()
            and not move.gives_check()
        ):
            reduction = 1  # 缩减 1 层

        # 递归搜索
        next_state = state.apply_move(move)
        current_value = min_value(
            next_state, alpha, beta, depth - 1 - reduction, can_null_move=True
        )

        # 如果缩减后结果有潜力，重新搜索
        if reduction > 0 and current_value > alpha:
            current_value = min_value(
                next_state, alpha, beta, depth - 1, can_null_move=True
            )

        # 更新最佳值
        if current_value > best_value:
            best_value = current_value
            best_move = move

        # Alpha-Beta 剪枝
        alpha = max(alpha, best_value)
        if alpha >= beta:
            # 记录杀手着法
            if not move.is_capture():
                update_killers(move, depth)
            # 更新历史启发式
            history_heuristic[(move.from_sq, move.to_sq)] += depth**2
            break

    # ------------
    # 8. 更新置换表
    # ------------
    flag = (
        "EXACT" if best_value <= alpha else ("LOWER" if best_value >= beta else "UACT")
    )
    transposition_table[zobrist_key] = TTEntry(depth, best_value, flag, best_move)

    return best_value


def min_value(state, alpha, beta, depth, can_null_move):
    # 与 max_value 对称实现，逻辑类似（省略重复部分）
    # ...
    return best_value


# ----------------------
# 辅助函数
# ----------------------
def quiescence_search(state, alpha, beta):
    # 静态搜索：只搜索吃子、将军等强制着法
    stand_pat = evaluate(state)
    if stand_pat >= beta:
        return beta
    alpha = max(alpha, stand_pat)

    # 生成所有吃子着法
    for move in state.generate_captures():
        next_state = state.apply_move(move)
        current_value = -quiescence_search(next_state, -beta, -alpha)
        if current_value >= beta:
            return beta
        alpha = max(alpha, current_value)

    return alpha


def order_moves(moves, state, depth, killers):
    # 综合排序：置换表最佳着 → 吃子 → 杀手着法 → 历史启发式
    ordered = []

    # 1. 提取置换表建议的最佳着
    tt_move = (
        transposition_table.get(state.zobrist_hash()).best_move
        if state.zobrist_hash() in transposition_table
        else None
    )
    if tt_move and tt_move in moves:
        ordered.append(tt_move)
        moves.remove(tt_move)

    # 2. 吃子着法按 MVV-LVA 排序
    ordered += sorted(
        [m for m in moves if m.is_capture()],
        key=lambda m: (m.captured_piece_value() - m.moved_piece_value()),
        reverse=True,
    )

    # 3. 添加杀手着法
    ordered += [m for m in moves if m in killers]

    # 4. 历史启发式排序剩余着法
    non_ordered = [m for m in moves if m not in ordered]
    non_ordered.sort(
        key=lambda m: history_heuristic.get((m.from_sq, m.to_sq), 0), reverse=True
    )

    return ordered + non_ordered


def update_killers(move, depth):
    # 维护杀手着法表（每个深度保留两个着法）
    if move not in killer_moves[depth]:
        killer_moves[depth] = [move] + killer_moves[depth][:1]


def evaluate(state):
    # 简化的局面评估函数（实现需具体化）
    return state.material_balance() + state.positional_score()
