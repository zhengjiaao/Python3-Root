import win32com.client

if __name__ == '__main__':
    # 启动 Excel 应用程序
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = True  # 设置为 False 可在后台运行
    excel_app.DisplayAlerts = False  # 禁止弹窗提示

    # 创建新的工作簿
    wb = excel_app.Workbooks.Add()
    ws = wb.ActiveSheet
    ws.Name = "产品销售"

    # —— 写入数据 ——————————————————————————————

    # 使用 Cells(行, 列) 方式写入标题
    ws.Cells(1, 1).Value = "产品名称"  # A1
    ws.Cells(1, 2).Value = "销售额"    # B1

    # 使用 Range("单元格") 写入标题
    ws.Range("C1").Value = "Q1"
    ws.Range("D1").Value = "Q2"
    ws.Range("E1").Value = "Q3"

    # 使用 Range("范围") 批量写入一行数据
    ws.Range("A2:E2").Value = ["产品A", 15000, 4500, 6000, 4500]
    ws.Range("A3:E3").Value = ["产品B", 20000, 5000, 7000, 8000]

    # —— 读取数据 ——————————————————————————————

    # 读取单个单元格内容
    product_name = ws.Cells(2, 1).Value
    q1_sales = ws.Range("C2").Value

    print(f"第一行产品名称: {product_name}")
    print(f"Q1 销售额: {q1_sales}")

    # —— 自动调整列宽 ————————————————————————————

    ws.Columns("A:E").AutoFit()

    # —— 保存文件 ————————————————————————————————

    output_path = "cell_operations_output.xlsx"
    wb.SaveAs(output_path)
    print(f"Excel 文件已保存至：{output_path}")

    # 关闭工作簿并退出 Excel
    wb.Close(True)
    excel_app.Quit()
