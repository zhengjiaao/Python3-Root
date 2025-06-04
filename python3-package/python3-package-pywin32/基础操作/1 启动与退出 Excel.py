import win32com.client
import os

if __name__ == '__main__':
    # 启动 Excel 实例
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True  # 显示 Excel 界面以便观察操作过程
    excel.DisplayAlerts = False  # 关闭警告提示（如覆盖文件时）

    try:
        # 创建一个新的工作簿
        wb = excel.Workbooks.Add()
        ws = wb.ActiveSheet
        ws.Name = "测试页"

        # 写入一些数据
        ws.Cells(1, 1).Value = "Hello Excel!"
        ws.Cells(2, 1).Value = "这是通过 Python 写入的数据"

        # 设置字体样式（可选）
        ws.Range("A1").Font.Bold = True
        ws.Range("A1").Font.Size = 14

        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "测试Excel.xlsx")

        # 保存工作簿
        wb.SaveAs(file_path)
        print(f"Excel 文件已保存至：{file_path}")

        # 关闭工作簿
        wb.Close(SaveChanges=True)

    finally:
        # 退出 Excel 应用程序
        excel.Quit()
        print("Excel 已退出。")
