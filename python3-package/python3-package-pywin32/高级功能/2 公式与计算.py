import win32com.client

if __name__ == '__main__':
    # 启动 Excel 应用程序
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = False  # 不显示 Excel 窗口

    # 创建新的工作簿
    wb = excel_app.Workbooks.Add()
    ws = wb.ActiveSheet
    ws.Name = "公式计算"

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

    # 添加“总计”列标题
    ws.Cells(1, 6).Value = "总计"

    # 设置行总计公式（每行 B:E 求和）
    for row in range(2, len(data_rows) + 2):
        ws.Cells(row, 6).Formula = f"=SUM(B{row}:E{row})"

    # 设置列总计公式（B 列总和）
    ws.Cells(7, 2).Formula = "=SUM(B2:B" + str(len(data_rows)+1) + ")"

    # 手动触发 Excel 全局计算
    excel_app.Calculate()

    # 读取某个单元格的公式计算结果
    total_value = ws.Range("F2").Value
    print(f"第一行总计 F2 的值为：{total_value}")

    # 保存文件到当前目录
    output_path = "formula_output.xlsx"
    wb.SaveAs(output_path)
    print(f"Excel 文件已保存至：{output_path}")

    # 关闭工作簿并退出 Excel
    wb.Close(True)
    excel_app.Quit()
