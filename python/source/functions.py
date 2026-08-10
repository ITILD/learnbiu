"""
函数示例
对应 PPT 页：2-functions.md
本文件展示 Python 的函数定义、参数类型（默认参数、可变参数、关键字参数）与返回值
"""


# 简单函数
def greet(name: str) -> str:
    """向某人问好"""
    return f"你好, {name}!"


# 带默认参数的函数
def calculate_area(length: float, width: float = 1.0) -> float:
    """计算矩形面积，宽度默认为1.0"""
    return length * width


# 可变参数函数
def sum_numbers(*numbers: int) -> int:
    """计算任意数量数字的和"""
    return sum(numbers)


# 关键字参数函数
def show_info(**kwargs) -> None:
    """打印所有关键字参数"""
    for k, v in kwargs.items():
        print(f"  {k}: {v}")


# 单返回值
def add(a: int, b: int) -> int:
    return a + b


# 多返回值（元组）
def divide(a: int, b: int) -> tuple[int, int]:
    return a // b, a % b


def main():
    print("=== 函数定义和调用 ===")

    print(greet("王五"))
    print(f"矩形面积(长5宽3): {calculate_area(5, 3)}")
    print(f"矩形面积(长5默认宽): {calculate_area(5)}")

    print("\n=== 可变参数 ===")
    print(f"数字和: {sum_numbers(1, 2, 3, 4, 5)}")

    print("\n=== 关键字参数 ===")
    show_info(name="张三", age=25)

    print("\n=== 返回值 ===")
    print(f"单返回值 add(3, 4) = {add(3, 4)}")

    q, r = divide(10, 3)
    print(f"多返回值 divide(10, 3) → 商={q}, 余={r}")


if __name__ == "__main__":
    main()
