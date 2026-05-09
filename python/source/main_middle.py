
"""
Python 基础语法学习示例
本文件展示了 Python 的基础语法、数据结构、类和对象等核心概念
"""

# =============================================================================
# 1. 基础语法示例_扩展logger
# =============================================================================
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def basic_syntax_examples():
    """参考基础语法示例函数，修改成使用不同级别log输出，颜色不同"""
    
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
    # 未能输出，因为level设置为INFO，而DEBUG级别低于INFO
    logging.debug(f"调试信息_姓名: {name}")
    
    
    

# =============================================================================
# 3. 数据结构示例
# =============================================================================

def data_structure_examples():
    """参考数据结构示例函数，使用pydantic替代字典定义数据模型"""
    
    logging.info("\n=== 字典 (Dictionary) ===")
    
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
    
    logging.info("\n=== pydantic 定义数据模型 (DataModel) ===")
    
    # 定义数据模型 uv add pydantic
    from pydantic import BaseModel
    class Score(BaseModel):
        """成绩数据模型"""
        math: int
        english: int
    
    class Student(BaseModel):
        """学生数据模型"""
        name: str
        age: int
        major: str
        average_score: Score = Score(math=0, english=0)  # 默认值为0.0
    
    # 创建学生实例
    student1 = Student(name="李四", age=20, major="计算机科学", average_score=Score(math=90, english=85))
    logging.info(f"学生信息: {student1}")
    logging.info(f"姓名: {student1.name}")
    logging.info(f"年龄: {student1.age}")
    logging.info(f"专业: {student1.major}")
    logging.info(f"数学成绩: {student1.average_score.math}")
    logging.info(f"英语成绩: {student1.average_score.english}")
    
   
# =============================================================================
# 主函数
# =============================================================================

def main():
    """主函数 - 组织所有示例的执行"""

    # 按顺序执行各个示例
    basic_syntax_examples()
    data_structure_examples()

    logging.info("✅ 所有示例执行完成！")
    logging.info("💡 建议：修改代码并运行，观察不同的输出结果")

if __name__ == "__main__":
    main()
