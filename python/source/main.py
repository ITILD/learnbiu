"""
Python 基础知识学习示例 - 主入口
按 PPT 页拆分为多个独立模块，本文件按顺序组织执行所有示例。

各模块对应 PPT 页：
  - basic_types.py      → 2-basic-types.md
  - basic_operators.py  → 2-basic-operators.md
  - control_flow.py     → 2-control-flow.md
  - data_structures.py  → 2-data-structures.md
  - functions.py        → 2-functions.md
  - classes.py          → 2-classes.md
  - exceptions.py       → 2-exceptions.md
  - async_example.py    → 2-async.md
  - logging_example.py  → 3-logging.md
  - pydantic_example.py → 3-pydantic.md
"""
import asyncio

import basic_operators
import basic_types
import async_example
import classes
import control_flow
import data_structures
import exceptions
import functions
import logging_example
import pydantic_example


def main():
    """主函数 - 组织所有示例的执行"""

    print("🎯 Python 基础知识学习示例")
    print("=" * 50)

    # 按顺序执行各个示例
    basic_types.main()
    basic_operators.main()
    control_flow.main()
    data_structures.main()
    functions.main()
    classes.main()
    exceptions.main()
    asyncio.run(async_example.async_example())

    # 进阶示例
    logging_example.main()
    pydantic_example.main()

    print("\n" + "=" * 50)
    print("✅ 所有示例执行完成！")
    print("💡 建议：修改代码并运行，观察不同的输出结果")


if __name__ == "__main__":
    main()
