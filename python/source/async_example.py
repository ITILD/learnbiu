"""
异步编程示例
对应 PPT 页：2-async.md
本文件展示 Python 的 asyncio 异步编程，通过并发执行提升 IO 密集型任务性能
"""
import asyncio
import time


async def order_and_serve(dish_name: str, prepare_time: int):
    """点餐并上菜：模拟异步任务"""
    await asyncio.sleep(prepare_time)
    print(f"{dish_name} 已准备完成！")
    print(f"{dish_name} 已服务完成！")


async def async_example():
    """并发执行多个点餐任务"""
    start_time = time.time()
    print("\n=== 异步编程 ===")
    await asyncio.gather(
        order_and_serve("鱼香肉丝", 1),
        order_and_serve("红烧肉", 1),
        order_and_serve("青椒肉丝", 1),
    )
    print("异步任务完成,执行时时间: ", time.time() - start_time)


def main():
    # asyncio.run 运行顶层协程
    asyncio.run(async_example())


if __name__ == "__main__":
    main()
