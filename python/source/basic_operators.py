"""
运算符示例
对应 PPT 页：2-basic-operators.md
本文件展示 Python 的算术、比较、逻辑与赋值运算符
"""


def main():
    # 算术运算
    a: int = 10
    b: int = 3

    print("=== 算术运算 ===")
    print(f"{a} + {b} = {a + b}")  # 加法
    print(f"{a} - {b} = {a - b}")  # 减法
    print(f"{a} * {b} = {a * b}")  # 乘法
    print(f"{a} / {b} = {a / b:.2f}")  # 除法，保留两位小数
    print(f"{a} // {b} = {a // b}")  # 整除
    print(f"{a} % {b} = {a % b}")  # 取余
    print(f"{a} ** {b} = {a ** b}")  # 幂运算

    # 比较运算
    print("\n=== 比较运算 ===")
    print(f"{a} > {b}: {a > b}")
    print(f"{a} < {b}: {a < b}")
    print(f"{a} == {b}: {a == b}")
    print(f"{a} != {b}: {a != b}")

    # 逻辑运算
    x: bool = True
    y: bool = False

    print("\n=== 逻辑运算 ===")
    print(f"x and y: {x and y}")  # 与运算
    print(f"x or y: {x or y}")  # 或运算
    print(f"not x: {not x}")  # 非运算

    # 赋值运算
    print("\n=== 赋值运算 ===")
    val = 10
    print(f"初始值: {val}")
    val += 5
    print(f"val += 5 → {val}")
    val -= 3
    print(f"val -= 3 → {val}")
    val *= 2
    print(f"val *= 2 → {val}")
    val /= 4
    print(f"val /= 4 → {val}")


if __name__ == "__main__":
    main()
