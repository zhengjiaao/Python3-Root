import asyncio
import aiohttp


async def fetch_url(session, url):
    """
    异步获取指定 URL 的内容，并打印响应长度
    :param session: aiohttp.ClientSession 实例
    :param url: 请求的目标 URL
    :return: 响应文本内容
    """
    try:
        async with session.get(url) as response:
            # 确保响应状态码为 200 OK
            response.raise_for_status()

            # 获取响应文本内容
            text = await response.text()

            # 打印简要信息（避免输出过长）
            print(f"URL: {url}, 内容长度: {len(text)}")
            return text
    except aiohttp.ClientError as e:
        print(f"请求失败: {url} - 错误: {str(e)}")
    except Exception as e:
        print(f"未知错误: {url} - 错误: {str(e)}")


async def main():
    """
    主函数：并发请求多个 URL 并等待所有完成
    """
    # 定义待请求的 URL 列表
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://github.com"
    ]

    # 设置超时限制（单位秒），防止请求卡住
    timeout = aiohttp.ClientTimeout(total=10)

    # 使用 ClientSession 发起异步 HTTP 请求
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # 创建任务列表
        tasks = [fetch_url(session, url) for url in urls]

        # 并发执行所有任务
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    # 启动事件循环并运行主函数
    asyncio.run(main())
