import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        # 限制响应内容长度以避免输出过长
        text = await response.text()
        print(f"URL: {url}, Length: {len(text)}")
        return text

async def main():
    urls = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://github.com"
    ]
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        await asyncio.gather(*tasks)  # 并发执行所有任务

if __name__ == '__main__':
    # 运行事件循环
    asyncio.run(main())