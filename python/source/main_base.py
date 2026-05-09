"""
Python 基础语法学习示例
本文件展示了 Python 的基础语法、数据结构、类和对象等核心概念
"""

# =============================================================================
# 1. 基础语法示例
# =============================================================================


def basic_syntax_examples():
    """基础语法示例函数"""

    # 变量和数据类型
    name: str = "张三"  # 字符串类型
    age: int = 25  # 整数类型
    height: float = 1.75  # 浮点数类型
    is_student: bool = True  # 布尔类型

    print("=== 基础数据类型 ===")
    print(f"姓名: {name}")
    print(f"年龄: {age}")
    print(f"身高: {height}米", f"是否学生: {is_student}")

    # 算术运算
    a: int = 10
    b: int = 3

    print("\n=== 算术运算 ===")
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


# =============================================================================
# 2. 控制流示例
# =============================================================================


def control_flow_examples():
    """控制流示例函数"""

    print("\n=== if/else 条件判断 ===")

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


# =============================================================================
# 3. 数据结构示例
# =============================================================================


def data_structure_examples():
    """数据结构示例函数"""

    print("\n=== 列表 (List) ===")

    # 列表 - 有序的可变集合
    numbers: list[int] = [1, 2, 3, 4, 5]
    print(f"原始列表: {numbers}")

    # 列表操作
    numbers.append(6)  # 添加元素
    numbers.insert(0, 0)  # 在指定位置插入
    numbers.remove(3)  # 删除元素

    print(f"修改后列表: {numbers}")
    print(f"列表长度: {len(numbers)}")
    print(f"第一个元素: {numbers[0]}")
    print(f"最后一个元素: {numbers[-1]}")

    print("\n=== 元组 (Tuple) ===")

    # 元组 - 有序的不可变集合
    coordinates: tuple[float, float] = (10.5, 20.3)
    print(f"坐标: {coordinates}")
    print(f"X坐标: {coordinates[0]}")
    print(f"Y坐标: {coordinates[1]}")

    print("\n=== 字典 (Dictionary) ===")

    # 字典 - 键值对集合
    student: dict[str, any] = {
        "姓名": "李四",
        "年龄": 20,
        "专业": "计算机科学",
        "成绩": {"数学": 90, "英语": 85},
    }

    print(f"学生信息: {student}")
    print(f"姓名: {student['姓名']}")
    print(f"年龄: {student['年龄']}")

    # 字典操作
    student["班级"] = "一班"  # 添加新键值对
    print(f"添加班级后: {student}")

    print("\n=== 集合 (Set) ===")

    # 集合 - 无序的不重复元素集合
    set1: set[int] = {1, 2, 3, 4, 5}
    set2: set[int] = {4, 5, 6, 7, 8}

    print(f"集合1: {set1}")
    print(f"集合2: {set2}")
    print(f"并集: {set1 | set2}")  # 或 set1.union(set2)
    print(f"交集: {set1 & set2}")  # 或 set1.intersection(set2)
    print(f"差集: {set1 - set2}")  # 或 set1.difference(set2)


# =============================================================================
# 4. 函数示例
# =============================================================================


def function_examples():
    """函数示例函数"""

    print("\n=== 函数定义和调用 ===")
    # 作用域示例
    name: str = "张三"

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

    # 调用函数
    print(greet("王五"))
    print(f"矩形面积(长5宽3): {calculate_area(5, 3)}")
    print(f"矩形面积(长5默认宽): {calculate_area(5)}")
    print(f"数字和: {sum_numbers(1, 2, 3, 4, 5)}")


# =============================================================================
# 5. 类和对象示例
# =============================================================================


class Person:
    """人类 - 演示类的定义和使用"""

    def __init__(self, name: str, age: int):
        """构造函数，初始化对象属性"""
        self.name = name
        self.age = age

    def introduce(self) -> str:
        """自我介绍方法"""
        return f"我叫{self.name}，今年{self.age}岁。"

    def have_birthday(self) -> None:
        """过生日，年龄加1"""
        self.age += 1
        print(f"{self.name}过生日啦！现在{self.age}岁。")


class Student(Person):
    """学生类 - 继承自Person类"""

    def __init__(self, name: str, age: int, student_id: str):
        """学生类构造函数"""
        super().__init__(name, age)  # 调用父类构造函数
        self.student_id = student_id
        self.courses: list[str] = []

    def enroll_course(self, course_name: str) -> None:
        """选课方法"""
        self.courses.append(course_name)
        print(f"{self.student_id}选了课程: {course_name}")

    def show_courses(self) -> None:
        """显示所选课程"""
        if self.courses:
            print(f"{self.student_id}的课程: {', '.join(self.courses)}")
        else:
            print(f"{self.student_id}还没有选课")


def class_object_examples():
    """类和对象示例函数"""

    print("\n=== 类和对象 ===")

    # 创建Person对象
    person1 = Person("张三", 25)
    print(person1.introduce())

    # 创建Student对象
    student1 = Student("李四", 20, "S001")
    print(student1.introduce())

    # 调用对象方法
    student1.enroll_course("Python编程")
    student1.enroll_course("数据结构")
    student1.show_courses()

    # 过生日
    student1.have_birthday()


# =============================================================================
# 6. 异常处理示例
# =============================================================================


def exception_handling_examples():
    """异常处理示例函数"""

    print("\n=== 异常处理 ===")

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


# =============================================================================
# 7. 异步编程示例
# =============================================================================
import asyncio, time


async def async_example():
    """简单异步示例"""

    async def order_and_serve(dish_name: str, prepare_time: int):
        await asyncio.sleep(prepare_time)
        print(f"{dish_name} 已准备完成！")
        print(f"{dish_name} 已服务完成！")

    start_time = time.time()
    print("\n=== 异步编程 ===")
    await asyncio.gather(
        order_and_serve("鱼香肉丝", 1),
        order_and_serve("红烧肉", 1),
        order_and_serve("青椒肉丝", 1),
    )
    print("异步任务完成,执行时时间: ", time.time() - start_time)


# =============================================================================
# 主函数
# =============================================================================


def main():
    """主函数 - 组织所有示例的执行"""

    print("🎯 Python 基础语法学习示例")
    print("=" * 50)

    # 按顺序执行以上7个示例
    basic_syntax_examples()
    control_flow_examples()
    data_structure_examples()
    asyncio.run(async_example())
    function_examples()
    class_object_examples()
    exception_handling_examples()

    print("\n" + "=" * 50)
    print("✅ 所有示例执行完成！")
    print("💡 建议：修改代码并运行，观察不同的输出结果")


if __name__ == "__main__":
    main()
