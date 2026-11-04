---
layout: two-cols
layoutClass: gap-8
class: text-sm
---

# 变量与数据类型

<div class="mb-3 p-2 bg-blue-500/10 border-l-4 border-blue-500 rounded text-sm">
<b>变量</b>就是给数据起个名字，之后用名字就能反复使用它。
</div>

## 四种最常用的类型

```python
name = "张三"        # str  文本
age = 25             # int  整数
height = 1.75        # float 小数
is_student = True    # bool 真 / 假
```

## 类型注解（可选）

```python
age: int = 25
names: list[str] = ["a", "b"]
```

Python 会自动推断类型；注解是写给人和 IDE 看的，不写也能运行。

::right::

## 类型转换

```python
int("42")       # "42" → 42
float("3.14")   # "3.14" → 3.14
str(100)        # 100 → "100"
bool(0)         # 0 → False
```

## f-string 格式化

```python
name = "张三"
age = 25
print(f"我叫{name}，今年{age}岁")
# 输出：我叫张三，今年25岁
```

<div class="mt-4 p-3 bg-yellow-500/10 border-l-4 border-yellow-500 rounded text-sm">
<b>动态类型：</b>同一个变量可以先存数字，后面再存文本。<br/>
<b>常见坑：</b><code>"1" + 1</code> 会报错，要先转换类型：<code>int("1") + 1</code>。
</div>
