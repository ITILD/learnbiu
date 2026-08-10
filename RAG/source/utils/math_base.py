# 基础的加减乘除


def add(a: float, b: float) -> float:
    """加法运算"""
    return a + b


def subtract(a: float, b: float) -> float:
    """减法运算"""
    return a - b


def multiply(a: float, b: float) -> float:
    """乘法运算"""
    return a * b


def divide(a: float, b: float) -> float:
    """除法运算"""
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


if __name__ == "__main__":
    print("=== 基础加减乘除测试 ===")

    a = 10.0
    b = 3.0

    print(f"{a} + {b} = {add(a, b)}")
    print(f"{a} - {b} = {subtract(a, b)}")
    print(f"{a} * {b} = {multiply(a, b)}")
    print(f"{a} / {b} = {divide(a, b)}")

    # 测试除零异常
    try:
        print(f"{a} / 0 = {divide(a, 0)}")
    except ValueError as e:
        print(f"错误: {e}")
