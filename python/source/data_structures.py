"""
数据结构示例
对应 PPT 页：2-data-structures.md
本文件展示 Python 的列表、元组、字典与集合
"""


def main():
    print("=== 列表 (List) ===")

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
    print(f"切片 [1:3]: {numbers[1:3]}")

    print("\n=== 元组 (Tuple) ===")

    # 元组 - 有序的不可变集合
    coordinates: tuple[float, float] = (10.5, 20.3)
    print(f"坐标: {coordinates}")
    print(f"X坐标: {coordinates[0]}")
    print(f"Y坐标: {coordinates[1]}")
    # 解包
    x, y = coordinates
    print(f"解包: x={x}, y={y}")

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
    print(f"安全访问性别: {student.get('性别', '未知')}")

    print("\n=== 集合 (Set) ===")

    # 集合 - 无序的不重复元素集合
    set1: set[int] = {1, 2, 3, 4, 5}
    set2: set[int] = {4, 5, 6, 7, 8}

    print(f"集合1: {set1}")
    print(f"集合2: {set2}")
    print(f"并集: {set1 | set2}")  # 或 set1.union(set2)
    print(f"交集: {set1 & set2}")  # 或 set1.intersection(set2)
    print(f"差集: {set1 - set2}")  # 或 set1.difference(set2)


if __name__ == "__main__":
    main()
