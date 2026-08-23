"""
Pydantic 数据模型示例
对应 PPT 页：3-pydantic.md
本文件参考数据结构示例，使用 pydantic 替代字典定义数据模型
运行前请安装依赖：uv add pydantic
"""
import logging

from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Score(BaseModel):
    """成绩数据模型"""
    math: int
    english: int


class Student(BaseModel):
    """学生数据模型"""
    name: str
    age: int
    major: str
    average_score: Score = Score(math=0, english=0)  # 默认值为 0


def main():
    """使用 pydantic 定义数据模型，对比字典方式"""

    logging.info("=== 字典 (Dictionary) ===")

    # 字典 - 键值对集合
    student: dict[str, any] = {
        "姓名": "李四",
        "年龄": 20,
        "专业": "计算机科学",
        "成绩": {"数学": 90, "英语": 85}
    }

    logging.info(f"学生信息: {student}")
    logging.info(f"姓名: {student['姓名']}")
    logging.info(f"年龄: {student['年龄']}")

    # 字典操作
    student["班级"] = "一班"  # 添加新键值对
    logging.info(f"添加班级后: {student}")

    logging.info("=== pydantic 定义数据模型 (DataModel) ===")

    # 创建学生实例
    student1 = Student(
        name="李四",
        age=20,
        major="计算机科学",
        average_score=Score(math=90, english=85)
    )
    logging.info(f"学生信息: {student1}")
    logging.info(f"姓名: {student1.name}")
    logging.info(f"年龄: {student1.age}")
    logging.info(f"专业: {student1.major}")
    logging.info(f"数学成绩: {student1.average_score.math}")
    logging.info(f"英语成绩: {student1.average_score.english}")


if __name__ == "__main__":
    main()
