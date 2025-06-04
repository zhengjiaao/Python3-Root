import win32com.client

if __name__ == '__main__':
    # 启动 Excel 应用程序
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = True  # 显示 Excel 界面便于观察操作
    excel_app.DisplayAlerts = False  # 防止弹窗干扰

    # 创建新的工作簿
    wb = excel_app.Workbooks.Add()

    # —— 获取工作表 ——————————————————————————————

    # 获取当前活动工作表
    ws = wb.ActiveSheet
    ws.Name = "主数据表"

    # 按名称获取工作表（若已存在）
    try:
        ws_sheet1 = wb.Worksheets("Sheet1")
        ws_sheet1.Name = "旧数据"
    except Exception as e:
        print("未找到 Sheet1")

    # —— 添加新工作表 ——————————————————————————————

    # 添加一个新工作表并设置名称
    new_ws = wb.Worksheets.Add()
    new_ws.Name = "季度数据"

    # 写入一些测试数据用于展示
    new_ws.Range("A1").Value = "季度"
    new_ws.Range("B1").Value = "销售额"
    new_ws.Range("A2:B3").Value = [["Q1", 15000], ["Q2", 20000]]

    # —— 删除工作表 ————————————————————————————————

    # 尝试删除名为 "Sheet2" 的工作表（如果存在）
    try:
        wb.Worksheets("Sheet2").Delete()
        print("Sheet2 已删除")
    except Exception as e:
        print("未找到 Sheet2，跳过删除")

    # —— 切换激活工作表 ——————————————————————————————

    # 激活“主数据表”
    wb.Worksheets("主数据表").Activate()

    # 在激活的工作表中写入数据
    active_ws = wb.ActiveSheet
    active_ws.Range("A1").Value = "这是主数据表"

    # —— 保存文件 ————————————————————————————————

    output_path = "worksheet_operations.xlsx"
    wb.SaveAs(output_path)
    print(f"Excel 文件已保存至：{output_path}")

    # 关闭工作簿并退出 Excel
    wb.Close(True)
    excel_app.Quit()
