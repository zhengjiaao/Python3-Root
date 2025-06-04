import win32com.client
import time

if __name__ == '__main__':
    # 启动 Excel 应用程序（可见以便查看宏执行效果）
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = True
    excel_app.DisplayAlerts = False  # 禁止弹窗提示

    try:
        # —— 第一部分：运行已有的宏 ——————————————————————

        # 打开包含宏的工作簿（或 Personal.xlsb）
        # 假设 Personal.xlsb 已在 Excel 中加载，并包含名为 FormatReport 的宏
        print("正在运行 Personal.xlsb!FormatReport 宏...")
        excel_app.Run("Personal.xlsb!FormatReport")

        # —— 第二部分：动态注入并运行 VBA 代码 ————————————————

        # 创建一个新的工作簿用于测试 VBA 脚本
        wb = excel_app.Workbooks.Add()
        ws = wb.ActiveSheet
        ws.Name = "VBA 测试"
        ws.Cells(1, 1).Value = "Hello from Python!"

        # 插入一段简单的 VBA 子程序
        vba_code = """
Sub HelloPyWin32()
    MsgBox "Hello from Python!", vbInformation, "PyWin32 消息"
End Sub
        """

        # 将 VBA 添加到当前工作簿模块
        vba_module = wb.VBProject.VBComponents.Add(1)  # 1 = vbext_ct_StdModule
        vba_module.CodeModule.AddFromString(vba_code)

        # 运行刚刚插入的 VBA 宏
        print("正在运行 HelloPyWin32 宏...")
        excel_app.Run("HelloPyWin32")

        # 移除模块以避免重复添加
        wb.VBProject.VBComponents.Remove(vba_module)

        # —— 第三部分：保存文件 ——————————————————————————————

        output_path = "macro_automation_output.xlsx"
        wb.SaveAs(output_path)
        print(f"Excel 文件已保存至：{output_path}")

    except Exception as e:
        print(f"发生错误：{e}")

    finally:
        # 关闭工作簿并退出 Excel
        if 'wb' in locals():
            wb.Close(SaveChanges=False)
        excel_app.Quit()
        print("Excel 已关闭。")
