# 快速开始

Pydantic 2.x 是 Python 数据验证和设置管理的重大升级版本，带来了显著的性能提升和强大的新功能。

## 介绍

Pydantic 2.x 核心特性:

性能提升:

* 验证速度提高 5-50 倍
* 序列化速度提高 4-10 倍
* 内存占用减少 50%
* 基于 Rust 实现的验证核心

新功能亮点:

1. 模型字段别名系统重构
2. 自定义验证器 API 改进
3. 更强大的 JSON 模式生成
4. 标准库 TypedDict 支持
5. 改进的 @validate_call 装饰器
6. 更友好的错误消息

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装依赖
pip install pydantic
pip install pydantic_settings

# or
pip install -r requirements.txt
```

验证：

```shell
pip show pydantic
```

## 示例


