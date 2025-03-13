# mit6.172-fall-2018


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


## Homework

- [Homework 1: Getting Started](course/static_resources/2724d8594cb413754669fc4e9c6ce7db_MIT6_172F18hw1.pdf)
- [Homework 2: Profiling Serial Merge Sort](course/static_resources/796439e646c02f44348d50b1836ff7f9_MIT6_172F18hw2.pdf)

