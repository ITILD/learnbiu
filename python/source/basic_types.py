"""
变量与数据类型示例
对应 PPT 页：2-basic-types.md
本文件展示 Python 的基本数据类型、类型注解、类型转换与 f-string 格式化
"""


def main():
    # 变量和数据类型
    name: str = "张三"  # 字符串类型
    age: int = 25  # 整数类型
    height: float = 1.75  # 浮点数类型
    is_student: bool = True  # 布尔类型

    print("=== 基础数据类型 ===")
    print(f"姓名: {name}")
    print(f"年龄: {age}")
    print(f"身高: {height}米", f"是否学生: {is_student}")

    # 类型注解（新语法）
    print("\n=== 类型注解 ===")
    # 旧写法
    from typing import List, Dict
    names_old: List[str] = ["a", "b"]

    # 新写法（推荐）
    names_new: list[str] = ["a", "b"]
    scores: dict[str, int] = {"math": 90}
    print(f"旧写法: {names_old}")
    print(f"新写法: {names_new}")
    print(f"字典: {scores}")

    # 类型转换
    print("\n=== 类型转换 ===")
    print(f'int("42") = {int("42")}')      # "42" → 42
    print(f'float("3.14") = {float("3.14")}')  # "3.14" → 3.14
    print(f'str(100) = {str(100)!r}')        # 100 → "100"
    print(f'bool(1) = {bool(1)}')           # 1 → True
    print(f'bool(0) = {bool(0)}')           # 0 → False

    # f-string 格式化
    print("\n=== f-string 格式化 ===")
    name = "张三"
    age = 25
    print(f"我叫{name}，今年{age}岁")
    # 输出：我叫张三，今年25岁


if __name__ == "__main__":
    main()
