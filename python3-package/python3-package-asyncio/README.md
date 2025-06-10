# 快速开始

## 介绍

asyncio 是 Python 用于编写并发代码 的核心库，基于 async/await 语法实现异步 I/O 操作。它允许开发者通过事件循环（Event Loop）驱动协程（Coroutine），以单线程的方式高效处理大量并发任务，尤其适用于 I/O 密集型场景（如网络请求、Web 服务）

## 核心概念

1. **事件循环（Event Loop）**
   `asyncio` 的核心是事件循环，负责管理协程的调度与执行。通过事件循环，协程可以在 I/O 等待时主动让出控制权，从而实现非阻塞操作。

   - 示例：

     ```python
     asyncio.run(main())
     ```

      启动事件循环并运行主协程 。

2. **协程（Coroutine）**
   使用 `async def` 定义的函数称为协程，需通过 `await` 关键字调用。协程是轻量级的，比线程更节省资源 。

   - 示例：

     ```python
     async def fetch_data():
         await asyncio.sleep(1)
         return "Data"
     ```

3. **任务（Task）**
   将协程封装为 `Task` 对象后，可由事件循环并发调度。例如：

   ```python
   task = asyncio.create_task(fetch_data())
   ```

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
pip install asyncio   # Python标准库，提供异步I/O、事件循环、协程和任务的基础设施。
pip install aiohttp   # 用于异步HTTP客户端/服务器。

# or
pip install -r requirements.txt
```

验证：

```shell
pip show asyncio
```

## 示例


