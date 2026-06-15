# pytest - Python 测试框架

pytest 是一个功能强大、易于使用的 Python 测试框架，支持简单的单元测试到复杂的功能测试。

## 核心特性

1. **简单语法**：使用 assert 语句进行断言，无需学习复杂的 API
2. **自动发现**：自动发现和运行测试用例
3. **丰富的插件生态**：支持代码覆盖率、并行测试、mock 等
4. **参数化测试**：轻松实现数据驱动测试
5. **fixture 机制**：强大的测试依赖管理和资源复用
6. **详细报告**：提供清晰的测试失败信息和堆栈跟踪

## 目录结构

```
python3-package-pytest/
├── 基础操作/              # 基础测试示例
│   ├── test_basic.py     # 基本断言和测试函数
│   ├── test_fixture.py   # fixture 使用示例
│   └── test_parametrize.py # 参数化测试
├── 高级功能/              # 高级测试技巧
│   ├── test_mock.py      # Mock 和补丁
│   ├── test_exception.py # 异常测试
│   ├── test_mark.py      # 标记和分组
│   └── conftest.py       # 共享 fixture
├── 场景示例/              # 实际应用场景
│   ├── test_api.py       # API 测试
│   ├── test_database.py  # 数据库测试
│   └── test_data_processing.py # 数据处理测试
├── README.md
└── requirements.txt
```

## 安装

```bash
pip install pytest pytest-cov pytest-mock
# 或
pip install -r requirements.txt
```

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest test_basic.py

# 运行特定测试函数
pytest test_basic.py::test_addition

# 显示详细输出
pytest -v

# 显示打印输出
pytest -s

# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行标记的测试
pytest -m smoke
```

## 基础示例

### 1. 简单测试

```python
def add(a, b):
    return a + b

def test_addition():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

### 2. 使用 Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    return [1, 2, 3, 4, 5]

def test_sum(sample_data):
    assert sum(sample_data) == 15
```

### 3. 参数化测试

```python
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

## 实际应用场景

### API 测试

测试 RESTful API 端点，验证响应状态码和数据格式。

### 数据库测试

测试数据库操作，包括 CRUD 操作和事务处理。

### 数据处理测试

验证数据清洗、转换和分析逻辑的正确性。

## 最佳实践

1. **测试命名**：测试函数以 `test_` 开头
2. **单一职责**：每个测试只验证一个功能点
3. **独立性**：测试之间互不依赖
4. **可读性**：使用描述性的测试名称和断言消息
5. **Fixture 复用**：将通用设置提取为 fixture
6. **标记分类**：使用 mark 对测试进行分类

## 常用插件

- **pytest-cov**：代码覆盖率
- **pytest-mock**：Mock 支持
- **pytest-xdist**：并行测试
- **pytest-html**：HTML 报告
- **pytest-django**：Django 集成
- **pytest-flask**：Flask 集成

## 参考资源

- [官方文档](https://docs.pytest.org/)
- [插件列表](https://docs.pytest.org/en/latest/reference/plugin_list.html)
