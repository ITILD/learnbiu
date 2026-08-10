"""
控制流示例
对应 PPT 页：2-control-flow.md
本文件展示 Python 的条件判断、for 循环、while 循环与循环控制
"""


def main():
    print("=== if/else 条件判断 ===")

    score: int = 85

    if score >= 90:
        print("成绩优秀！")
    elif score >= 80:
        print("成绩良好！")
    elif score >= 60:
        print("成绩及格！")
    else:
        print("成绩不及格！")

    print("\n=== for 循环 ===")

    # 遍历数字范围
    print("数字 1-5:")
    for i in range(1, 6):
        print(f"  {i}")

    # 遍历列表
    fruits: list[str] = ["苹果", "香蕉", "橙子"]
    print("水果列表:")
    for fruit in fruits:
        print(f"  {fruit}")

    print("\n=== while 循环 ===")

    count: int = 3
    while count > 0:
        print(f"倒计时: {count}")
        count -= 1
    print("开始！")

    print("\n=== 循环控制 ===")

    # break - 跳出整个循环
    print("break 示例:")
    for i in range(10):
        if i == 5:
            break
        print(f"  {i}", end="")
    print()

    # continue - 跳过本次迭代
    print("continue 示例（只打印奇数）:")
    for i in range(10):
        if i % 2 == 0:
            continue
        print(f"  {i}", end="")
    print()


if __name__ == "__main__":
    main()
