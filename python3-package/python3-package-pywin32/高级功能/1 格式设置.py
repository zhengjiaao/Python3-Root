import win32com.client
from win32api import RGB  # 用于颜色设置
import os

if __name__ == '__main__':
    # 启动 Excel 应用程序
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = False  # 不显示 Excel 窗口

    # 创建新的工作簿
    wb = excel_app.Workbooks.Add()
    ws = wb.ActiveSheet
    ws.Name = "数据表"

    # 写入标题行
    headers = ["ID", "销售额", "成本", "利润", "增长率"]
    for col_num, data in enumerate(headers, 1):
        ws.Cells(1, col_num).Value = data

    # 写入示例数据
    data_rows = [
        [1, 15000.5, 9000.3, 6000.2, 12.5],
        [2, 20000.7, 12000.4, 8000.3, 15.3],
        [3, 18000.0, 10000.0, 8000.0, 10.0],
        [4, 22000.2, 13000.1, 9000.1, 18.7],
        [5, 25000.9, 14000.8, 11000.1, 20.2]
    ]

    for row_num, row_data in enumerate(data_rows, 2):  # 从第2行开始写入
        for col_num, value in enumerate(row_data, 1):
            ws.Cells(row_num, col_num).Value = value

    # 设置字体样式 - 标题行加粗、字号、蓝色字体
    ws.Range("A1:E1").Font.Bold = True
    ws.Range("A1:E1").Font.Size = 12
    ws.Range("A1:E1").Font.Color = RGB(0, 0, 255)  # 蓝色

    # 设置背景色 - 浅蓝色
    ws.Range("A1:E1").Interior.Color = RGB(220, 230, 241)

    # 设置边框 - 实线边框
    borders = ws.Range("A1:E{}".format(len(data_rows)+1)).Borders
    borders.LineStyle = 1  # 实线
    borders.Weight = 2     # 中等粗细

    # 设置数字格式 - 千位分隔符 + 两位小数
    ws.Range("B2:E{}".format(len(data_rows)+1)).NumberFormat = "#,##0.00"

    # 获取当前目录并保存文件
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, "formatted_output.xlsx")

    # 保存并关闭
    wb.SaveAs(file_path)
    print(f"Excel 文件已保存至：{file_path}")
    wb.Close(True)
    excel_app.Quit()
