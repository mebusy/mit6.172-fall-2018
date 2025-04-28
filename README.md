# mit6.172-fall-2018


[bit Hack](https://graphics.stanford.edu/~seander/bithacks.html) , or find in local archive "./bitHack/"

## Lectures

- [1 Introduction & Matrix Multiplication](course/static_resources/d0c73dd51c79b95196a2e6faa824e1b4_MIT6_172F18_lec1.pdf)
    - 通过调整多层循环的 顺序，尽可能的增加缓存命中，可以大幅增加运行速度
    - We can measure the effect of different access patterns using the Cachegrind cache simulator:
        ```bash
        $ valgrind --tool=cachegrind ./matrix_multiply
    - 并行化的矩阵乘法
        - Rule of Thumb: Parallelize the outer loops rather than the inner loops.
- [2 Bentley Rules for Optimizing Work](course/static_resources/1a57adbec9520270d4485b42a2e1a316_MIT6_172F18_lec2.pdf)
- [3 Bit Hacks](course/static_resources/cc6983c9ebd77c28e8ae85bc0e575360_MIT6_172F18_lec3.pdf)
- [17 Synchronization Without Locks](course/static_resources/cc6983c9ebd77c28e8ae85bc0e575360_MIT6_172F18_lec3.pdf)
    - non modern computer implement sequential consistency.
    - instruction reordering
        - store buffer ;  load take priority, bypassing/checking the store buff
        - A LOAD may be reordered with a prior STORE to a different location but not with a prior STORE to the same locationk
    - Lock Free Algorithm:  compare-and-swap,  for integer type only
        - Why we need CAS ?
        ```c++
        cilk_for (int i = 0; i ‹ n; ++i) {
            int temp = compute (myArray [i]);
            L. lock();
            result += temp;
            L. unlock();
        }
        ```
        - What happens if the operating system swaps out a loop iteration just after it acquires the mutex?
            - All other loop iterations must wait!!
        ```c++
        cilk_for (int i = 0; i ‹ n; ++i) {
            int temp = compute(myArray [i]);
            int old, new;
            do {
                old = result;
                new = old + temp;
            } while (!CAS(&result, old, new));
        }
        ```
        - Now no other loop iteration needs to wait. The algorithm is nonblocking.
    - CAS 有些情况下，比如 处理链表，会存在 ABA 问题
        - 解决方法是使用版本号: Pack a version number with each pointer in the same atomically updatable word
- [19 Leiserchess Codewalk](course/static_resources/809f3351da7a2e5a6afc7c22e2e68e4d_MIT6_172F18_lec19.pdf)
    - project 4



## Homework

- [Homework 1: Getting Started](course/static_resources/2724d8594cb413754669fc4e9c6ce7db_MIT6_172F18hw1.pdf)
- [Homework 2: Profiling Serial Merge Sort](course/static_resources/796439e646c02f44348d50b1836ff7f9_MIT6_172F18hw2.pdf)
    - **perf** 使用采样来收集有关重要软件、内核和硬件事件的数据，以便找出程序中的性能瓶颈。它会生成代码中时间消耗位置的详细记录。
        ```bash
        perf record <program_name> <program_arguments>
        perf report [-f]
        ```
        - if permission issue occurs
            - add 'kernel.perf_event_paranoid = -1'  to '/etc/sysctl.conf'
            ```bash
            sudo sysctl -p
            ```
    - **valgrind** valgrind 的 cachegrind 是一个缓存和分支预测分析器。优化缓存命中率是性能工程的关键部分。 cachegrind 模拟了 程序如何与机器的缓存层次结构和分支预测器交互，即使在没有可用的硬件性能计数器的情况下也可以使用。
        ```bash
        valgrind --tool=cachegrind --branch-sim=yes <program_name> <program_arguments>
        ```
        - e.g.
        ```bash
        $ valgrind --tool=cachegrind --branch-sim=yes ./sort 100000 10

        ==25465== 
        ==25465== I refs:        4,665,037,323
        ==25465== 
        ==25465== Branches:        451,076,778  (434,076,096 cond + 17,000,682 ind)
        ==25465== Mispredicts:      35,692,839  ( 35,692,555 cond +        284 ind)
        ==25465== Mispred rate:            7.9% (        8.2%     +        0.0%   )
        ```
        - 'I refs: 4,665,037,323'  
            - 这表示程序执行时，CPU 发出了 4,665,037,323 次指令引用。这是程序执行过程中加载指令的总次数。
        - 'Branches:        451,076,778  (434,076,096 cond + 17,000,682 ind)'
            - 这表示程序执行时共发生了 451,076,778 次分支操作。其中，cond（条件分支）为 434,076,096 次，而 ind（间接分支）为 17,000,682 次。
            - 条件分支是基于一些条件判断（如 if 语句），而间接分支通常是函数调用或跳转表相关的操作。
        - 'Mispredicts:      35,692,839  ( 35,692,555 cond +        284 ind)'
            - 这是程序在执行过程中，CPU 的分支预测失败的次数。总共 35,692,839 次预测失败，其中 35,692,555 次是条件分支预测失败，284 次是间接分支预测失败。
        - Mispred rate:            7.9% (        8.2%     +        0.0%   )
            - 这是分支预测失败的比率，表示分支预测失败次数占总分支数的比例。在这份报告中，分支预测失败率为 7.9%，其中条件分支的预测失败率为 8.2%，而间接分支几乎没有预测失败（0.0%）。
            - 理想情况下，CPU 的分支预测失败率应该尽可能低。
        - 如果需要分析 缓存命中， 加上 `--cache-sim=yes`
            ```bash
            ==34107== I refs:        4,665,036,965
            ==34107== I1  misses:            1,712    # L1 指令缓存（L1 I-cache）未命中的次数 非常低
            ==34107== LLi misses:            1,622    # 最后一级缓存（LLC，即 L2 或 L3）也未命中的次数
            ==34107== I1  miss rate:          0.00%
            ==34107== LLi miss rate:          0.00%   # 几乎没有需要从主存读取指令的情况
            ==34107== 
            ==34107== D refs:        3,056,874,774  (2,284,537,546 rd   + 772,337,228 wr)
            ==34107== D1  misses:        6,385,929  (    3,335,212 rd   +   3,050,717 wr)
            ==34107== LLd misses:           26,719  (        1,250 rd   +      25,469 wr)
            ==34107== D1  miss rate:           0.2% (          0.1%     +         0.4%  )
            ==34107== LLd miss rate:           0.0% (          0.0%     +         0.0%  )  
                        # 几乎所有数据访问都能在缓存中找到，很少访问主存。
            ==34107== 
            ==34107== LL refs:           6,387,641  (    3,336,924 rd   +   3,050,717 wr)
            ==34107== LL misses:            28,341  (        2,872 rd   +      25,469 wr)
            ==34107== LL miss rate:            0.0% (          0.0%     +         0.0%  )
                        # 几乎所有数据都能在缓存中找到，极少需要访问主存。
            ```
- [Homework 3: Vectorization](course/static_resources/072651a8229a63376d5720c9a500ae45_MIT6_172F18hw3.pdf)



# LLDB 

[lldb](lldb/lldb.md)
