import win32com.client
import os

# 该脚本会在 Excel 中动态插入一段 VBA 宏，并调用它来格式化报表。
if __name__ == '__main__':
    # 启动 Excel
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True
    excel.DisplayAlerts = False

    try:
        # 创建新工作簿
        wb = excel.Workbooks.Add()
        ws = wb.ActiveSheet
        ws.Name = "VBA 测试"

        # 写入示例数据
        ws.Range("A1").Value = "产品"
        ws.Range("B1").Value = "销售额"
        ws.Range("A2:B3").Value = [["产品A", 15000], ["产品B", 20000]]

        # 插入 VBA 宏代码
        vba_code = """
Sub 格式化报表()
    Dim ws As Worksheet
    Set ws = ThisWorkbook.Sheets("VBA 测试")
    
    ' 设置标题加粗
    ws.Range("A1:B1").Font.Bold = True
    
    ' 设置背景色
    ws.Range("A1:B1").Interior.Color = RGB(173, 216, 230) ' 浅蓝色
    
    ' 设置边框
    With ws.Range("A1:B2").Borders
        .LineStyle = xlContinuous
        .Weight = xlThin
    End With
End Sub
"""
        # 添加 VBA 模块并注入代码
        module = wb.VBProject.VBComponents.Add(1)  # 1 = vbext_ct_StdModule
        module.CodeModule.AddFromString(vba_code)

        # 运行宏
        excel.Run("格式化报表")

        # 移除模块（避免重复加载）
        wb.VBProject.VBComponents.Remove(module)

        # 保存文件
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "VBA_报表.xlsx")
        wb.SaveAs(file_path)
        print(f"报表已保存至：{file_path}")

        wb.Close(True)

    finally:
        excel.Quit()
        print("Excel 已退出。")
