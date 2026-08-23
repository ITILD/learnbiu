"""
异常处理示例
对应 PPT 页：2-exceptions.md
本文件展示 Python 的 try/except/else/finally 异常处理结构
"""


def main():
    print("=== 异常处理 ===")

    # 尝试执行可能出错的代码
    try:
        number_str = input("请输入一个数字: ")
        number = int(number_str)
        result = 100 / number
        print(f"100除以{number}的结果是: {result}")

    except ValueError:
        print("错误：请输入有效的数字！")

    except ZeroDivisionError:
        print("错误：不能除以零！")

    except Exception as e:
        print(f"发生未知错误: {e}")

    else:
        print("计算成功完成！")

    finally:
        print("异常处理示例结束。")


if __name__ == "__main__":
    main()
