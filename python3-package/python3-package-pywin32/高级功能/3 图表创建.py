import win32com.client

if __name__ == '__main__':
    # 启动 Excel 应用程序
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = True  # 显示 Excel 窗口以便查看图表

    # 创建新的工作簿
    wb = excel_app.Workbooks.Add()
    ws = wb.ActiveSheet
    ws.Name = "销售报表"

    # 写入标题行
    headers = ["季度", "销售额", "成本", "利润"]
    for col_num, data in enumerate(headers, 1):
        ws.Cells(1, col_num).Value = data

    # 写入示例数据
    data_rows = [
        ["第一季度", 15000, 9000, 6000],
        ["第二季度", 20000, 12000, 8000],
        ["第三季度", 18000, 10000, 8000],
        ["第四季度", 22000, 13000, 9000]
    ]

    for row_num, row_data in enumerate(data_rows, 2):  # 从第2行开始写入
        for col_num, value in enumerate(row_data, 1):
            ws.Cells(row_num, col_num).Value = value

    # 创建柱状图
    chart = ws.Shapes.AddChart2(201, 51).Chart  # 51 表示柱状图类型

    # 设置图表数据源范围
    chart.SetSourceData(Source=ws.Range("B1:D5"))  # 销售额、成本、利润数据区域

    # 设置图表标题
    chart.HasTitle = True
    chart.ChartTitle.Text = "季度销售与成本对比"

    # 设置图例
    chart.HasLegend = True
    chart.Legend.Position = -4107  # xlRight

    # 设置图表位置（放置在 H1 单元格附近）
    chart.Parent.Left = ws.Range("H1").Left
    chart.Parent.Top = ws.Range("H1").Top

    # 保存文件到当前目录
    output_path = "sales_chart.xlsx"
    wb.SaveAs(output_path)
    print(f"Excel 文件已保存至：{output_path}")

    # 提示用户操作完成，保持 Excel 打开状态
    print("图表已生成，请查看 Excel 界面。")
