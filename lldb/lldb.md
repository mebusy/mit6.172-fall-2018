# LLDB

- [migrating_from_gdb_to_lldb](lldb/migrating_from_gdb_to_lldb.pdf)
- [lldb tutorial](https://lldb.llvm.org/use/tutorial.html)


## Basic Syntax

- Commands are in the form
    - object action [options] [arguments]
        ```bash
        breakpoint    set    --name     main
         (object)  (action)  (option)  (value)
        ```
        ```bash
        breakpoint  delete      5
         (object)  (action) (argument)
        ```
    - Options have **short** and long form, can appear anywhere in the command
        ```bash
        target create MyApp.app     -a     i386
                      (argument) (option) (value)
        ```
    - “--” ends options (useful **if arguments** start with “-”)
        ```bash
        process launch --working-dir /tmp   -- -run-arg-1 -run-arg-2
                        (option)    (value)    (argument) (argument)
        ```
    - Words are white-space separated
        - Use quotes to protect spaces, “\” to protect quotes.
    - Some commands are “unparsed” after the end of options("--"):
        - “expression” and “script”
        - expression 和 script 命令的参数不会被 lldb 解析，而是直接传递给底层（Clang 或 Python）
        - 这意味着你可以写更自由的表达式，而不会受到 lldb 本身的命令解析规则的限制。
            ```bash
            (lldb) expression -- (int)3 + 4
            ```
            - `--` 用于结束选项解析（不过 lldb 通常不需要这个）。
            - `(int)3 + 4` 是 expression 命令要执行的表达式，lldb 不会对其进一步解析，而是直接传递给 Clang 解释执行。
            ```bash
            (lldb) script
            >>> print("Hello from Python!")
            ```
            - 这里 script 命令后面的部分直接传递给 Python 解释器执行，lldb 不会解析 Python 语法。

- We favor option/value over arguments
    - Easier to document
    - Reduce dependency on “argument order”
    - More powerful auto-completion (e.g. scoped by other options):
        ```bash
        breakpoint set --shlibs MyApp --name ma<TAB>
        ```
        - Looks for completions only in MyApp of symbols by name
    - And of course we do shortest unique match, so you can also type:
        ```bash
        br s -s MyApp -n ma<TAB>
        ```

## Help

- “help” command for detailed explanation of command/subcommand
    ```bash
    (lldb) help breakpoint delete
    Delete the specified breakpoint(s).  If no breakpoints are specified, delete them all.
    Syntax: breakpoint delete <cmd-options> [<breakpt-id | breakpt-id-list>]
    ```
- Also give help on argument types:
    ```bash
    (lldb) help breakpt-id
      <breakpt-id> -- Breakpoints are identified using major and minor numbers; ...
    ```
- “apropos” does help search:
    ```bash
    (lldb) apropos delet
    The following commands may relate to 'delet':
      breakpoint clear          -- Delete or disable breakpoints matching the specified source file and line.
      breakpoint command delete ...
      ...
    ```
- Command completion works in help...


## LLDB Command Object

- Represented by top level commands
    ```bash
    target, thread, breakpoint...
    ```
- Sometimes two words
    ```bash
    target modules
    breakpoint command
    ```
- In some cases, many objects exist of the same sort
    - One process has many threads...
    - “**list**” will always list the instances available, e.g.
        ```bash
        thread list
        ```
    - “**select**” will focus on one instance
        ```bash
        thread select 1
        ```
    - Auto-selected when that makes sense
        - e.g., if you stop at a breakpoint, process, thread and frame are set
    - Some object are contained in others (frame in thread)
        - Selecting a thread sets the context for selecting a frame…
- The object/action form makes it easy to find commands
- For example, how do you do a backtrace?
    - For backtrace, threads have stack frames, so try “**thread**”
    - Then use the `<TAB>` completion to find the action:
        ```bash
        (lldb) thread <TAB>
            Available completions:
                backtrace      -- Show thread call stacks.  Defaults to the current thread, thread indexes can be specified as arguments.
                continue
                ...
        ```
    - Finally, “help” will give you the full syntax



For more details please check the pdf file.



