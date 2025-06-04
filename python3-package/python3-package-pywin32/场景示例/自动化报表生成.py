import win32com.client
import os

# 该脚本会自动创建一个包含数据和图表的 Excel 报表。
if __name__ == '__main__':
    # 启动 Excel
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True
    excel.DisplayAlerts = False

    try:
        # 创建新工作簿
        wb = excel.Workbooks.Add()
        ws = wb.ActiveSheet
        ws.Name = "销售报表"

        # 写入标题行
        headers = ["产品", "Q1 销售额", "Q2 销售额", "Q3 销售额"]
        for col_num, data in enumerate(headers, 1):
            ws.Cells(1, col_num).Value = data

        # 写入示例数据
        data_rows = [
            ["产品A", 15000, 16000, 17000],
            ["产品B", 20000, 21000, 22000],
            ["产品C", 18000, 19000, 20000]
        ]

        for row_num, row_data in enumerate(data_rows, 2):
            for col_num, value in enumerate(row_data, 1):
                ws.Cells(row_num, col_num).Value = value

        # 添加总计列
        ws.Cells(1, 5).Value = "总计"
        for row in range(2, len(data_rows) + 2):
            ws.Cells(row, 5).Formula = f"=SUM(B{row}:D{row})"

        # 自动调整列宽
        ws.Columns("A:E").AutoFit()

        # 创建柱状图
        chart = ws.Shapes.AddChart2(201, 51).Chart  # 51 = 柱状图
        chart.SetSourceData(ws.Range("A1:D4"))
        chart.HasTitle = True
        chart.ChartTitle.Text = "季度销售额对比"

        # 保存文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "自动生成报表.xlsx")
        wb.SaveAs(file_path)
        print(f"报表已保存至：{file_path}")

        # 关闭工作簿
        wb.Close(True)

    finally:
        excel.Quit()
        print("Excel 已退出。")
