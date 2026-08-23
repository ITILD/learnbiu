"""
logging 日志模块示例
对应 PPT 页：3-logging.md
本文件参考基础语法示例，改用不同级别 log 输出，替代 print
"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """使用不同级别日志输出"""

    # 变量和数据类型
    name: str = "张三"  # 字符串类型
    age: int = 25       # 整数类型
    height: float = 1.75  # 浮点数类型
    is_student: bool = True  # 布尔类型

    # 不同级别日志输出
    logging.info(f"信息_姓名: {name}")
    logging.warning(f"警告_年龄: {age}")
    logging.error(f"错误_身高: {height}米")
    logging.critical(f"严重错误_是否学生: {is_student}")
    # 未能输出，因为 level 设置为 INFO，而 DEBUG 级别低于 INFO
    logging.debug(f"调试信息_姓名: {name}")


if __name__ == "__main__":
    main()
