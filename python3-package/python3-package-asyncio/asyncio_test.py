import asyncio
import aiohttp
import time
import os


# =================== 基础协程示例 ===================

async def say_after(delay, message):
    """
    协程函数：延迟打印消息
    :param delay: 延迟时间（秒）
    :param message: 要打印的消息
    """
    await asyncio.sleep(delay)
    print(message)


async def main():
    """
    主函数：演示顺序执行与并发执行的区别
    """
    print(f"开始时间: {time.strftime('%X')}")

    # 顺序执行两个协程
    await say_after(1, '你好')
    await say_after(2, '异步')

    # 并发执行两个协程
    task1 = asyncio.create_task(say_after(1, '并发'))
    task2 = asyncio.create_task(say_after(1, '世界'))

    await task1
    await task2

    print(f"结束时间: {time.strftime('%X')}")


# =================== 异步 HTTP 客户端 ===================

async def fetch_url(session, url):
    """
    异步获取网页内容并返回长度信息
    :param session: aiohttp.ClientSession 实例
    :param url: 请求的 URL 地址
    :return: 结果字符串
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.text()
                return f"{url}: {len(data)} 字节"
            return f"{url}: 错误 {response.status}"
    except Exception as e:
        return f"{url}: 异常 {str(e)}"


async def bulk_fetch(urls):
    """
    批量异步请求多个 URL
    :param urls: URL 列表
    """
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                print(f"请求失败: {result}")
            else:
                print(result)


# =================== 异步文件操作 ===================

async def async_file_io():
    """
    异步写入和读取文件（使用线程池避免阻塞事件循环）
    """
    file_path = 'async_demo.txt'
    content = "异步文件操作示例\n" * 100

    # 写入文件
    await asyncio.to_thread(lambda: open(file_path, 'w', encoding='utf-8').write(content))

    # 读取文件
    data = await asyncio.to_thread(lambda: open(file_path, 'r', encoding='utf-8').read())
    print(f"读取 {len(data)} 字节数据")


# =================== 生产者-消费者模型 ===================

async def producer(queue):
    """
    生产者：生成任务并放入队列
    :param queue: asyncio.Queue 队列实例
    """
    for i in range(1, 6):
        await asyncio.sleep(0.5)
        await queue.put(f"产品 {i}")
        print(f"生产: 产品 {i}")


async def consumer(queue):
    """
    消费者：从队列中取出任务并处理
    :param queue: asyncio.Queue 队列实例
    """
    while True:
        item = await queue.get()
        if item is None:  # 终止信号
            break
        await asyncio.sleep(1)
        print(f"消费: {item}")
        queue.task_done()


async def run_producer_consumer():
    """
    启动生产者-消费者模型
    """
    queue = asyncio.Queue(maxsize=3)

    # 启动生产者和消费者
    producer_task = asyncio.create_task(producer(queue))
    consumer_task = asyncio.create_task(consumer(queue))

    # 等待生产者完成
    await producer_task
    print("生产者完成")

    # 等待队列清空
    await queue.join()

    # 发送终止信号给消费者
    await queue.put(None)
    await consumer_task
    print("消费者完成")


# =================== 主程序入口 ===================

if __name__ == "__main__":
    print("基础协程示例:")
    asyncio.run(main())

    print("\n异步HTTP请求:")
    urls = [
        'https://www.python.org',
        'https://www.google.com',
        'https://www.github.com',
        'https://www.example.com'
    ]
    asyncio.run(bulk_fetch(urls))

    print("\n异步文件操作:")
    asyncio.run(async_file_io())

    print("\n生产者-消费者模型:")
    asyncio.run(run_producer_consumer())

    # 可选：清理测试文件
    file_path = 'async_demo.txt'
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"已删除临时文件: {file_path}")
