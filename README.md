# Python3 基础学习

- [python3 官网](https://www.python.org/)
- [python3 菜鸟教程](https://www.runoob.com/python3/python3-tutorial.html)
- [python3 廖雪峰教程](https://www.liaoxuefeng.com/wiki/1016959663602400)

**Python3 基础学习进展是根据[python3 菜鸟教程](https://www.runoob.com/python3/python3-tutorial.html)步骤进行的。**

## 基础环境

### 安装Python和虚拟环境

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

1.创建虚拟环境

```shell
cd Python3-Root

python -m venv .venv
```

2.激活虚拟环境

```shell
  # Windows:
  .venv\Scripts\activate
  # macOS/Linux:
  source .venv/bin/activate
```

3.安装Python依赖

```shell
cd example
pip install -r requirements.txt
# or 
pip install package-name
```

4.简单示例

创建文件：`main.py`

```python
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
```