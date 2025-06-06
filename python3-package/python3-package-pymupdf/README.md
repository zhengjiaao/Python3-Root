# PyMuPDF 操作pdf

## 介绍

## 安装Python依赖

确保你已经安装了Python 3.8或更高版本。你可以从[Python官方](https://www.python.org/downloads/)网站下载并安装。

```shell
# 安装PyMuPDF
pip install PyMuPDF

# 安装PyQt5
pip install PyQt5
pip install PyQt5-stubs

# or
pip install -r requirements.txt
```

验证：

```shell
pip show PyMuPDF
```

## 功能说明

这个PDF拆分工具提供以下功能：

1. **文件选择**：
   - 选择要拆分的PDF文件
   - 选择输出目录
2. **三种拆分方式**：
   - **按页数拆分**：指定每部分包含的页数
   - **按块数拆分**：指定要拆分成几个文件
   - **按文件大小拆分**：指定每个文件的最大大小（MB）
3. **处理日志**：
   - 显示操作过程中的详细日志
   - 包括错误信息和进度更新
4. **进度显示**：
   - 进度条显示当前处理进度
5. **操作控制**：
   - 开始拆分按钮
   - 取消操作按钮

## 技术特点

1. **PyQt5 GUI框架**：创建美观的用户界面
2. **多线程处理**：使用QThread实现后台处理，避免界面冻结
3. **PyMuPDF库**：高效处理PDF文件的拆分操作
4. **响应式设计**：界面元素自适应调整
5. **错误处理**：完善的输入验证和错误处理机制

## 使用说明

1. 点击"选择PDF文件"按钮上传PDF文件
2. 选择输出目录（默认为PDF文件所在目录）
3. 从下拉菜单中选择拆分方式
4. 输入拆分参数（页数、块数或文件大小）
5. 点击"开始拆分"按钮执行操作
6. 在日志区域查看处理过程和结果

## 运行要求

运行此脚本需要安装以下Python库：

```shell
pip install PyQt5 PyMuPDF
```

这个应用提供了一个直观、美观的界面来拆分PDF文件，满足不同的拆分需求，并实时显示处理日志和进度。

## 打包

```shell
# 安装
pip install pyinstaller

# 打包命令：单文件模式 + 隐藏控制台窗口 + 添加图标
pyinstaller --onefile --noconsole --icon=app.ico PDF拆分工具.py
```