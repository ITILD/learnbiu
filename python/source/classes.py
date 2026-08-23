"""
类与对象示例
对应 PPT 页：2-classes.md
本文件展示 Python 的类定义、对象创建、方法调用与继承
"""


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


def main():
    print("=== 类和对象 ===")

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


if __name__ == "__main__":
    main()
