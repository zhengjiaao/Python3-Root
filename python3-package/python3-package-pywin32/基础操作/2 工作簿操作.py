import win32com.client
import os

if __name__ == '__main__':
    # 启动 Excel 应用程序
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True  # 显示 Excel 窗口以便查看操作效果
    excel.DisplayAlerts = False  # 防止弹窗干扰

    # —— 新建工作簿 ——————————————————————————————

    print("创建新工作簿...")
    new_wb = excel.Workbooks.Add()
    new_ws = new_wb.ActiveSheet
    new_ws.Name = "数据表"
    new_ws.Cells(1, 1).Value = "这是新建的工作簿"

    # 保存新工作簿到当前目录
    new_file_path = os.path.join(os.getcwd(), "新建工作簿.xlsx")
    new_wb.SaveAs(new_file_path)
    print(f"新工作簿已保存至：{new_file_path}")

    # —— 打开现有工作簿 ——————————————————————————————

    # 示例路径，请替换为你本地实际存在的文件路径
    existing_file = os.path.join(os.getcwd(), "示例工作簿.xlsx")

    # 如果不存在测试文件，则先创建一个用于演示
    if not os.path.exists(existing_file):
        temp_wb = excel.Workbooks.Add()
        temp_ws = temp_wb.ActiveSheet
        temp_ws.Cells(1, 1).Value = "这是一个示例工作簿"
        temp_wb.SaveAs(existing_file)
        temp_wb.Close()
        print(f"已创建测试工作簿：{existing_file}")

    print(f"正在打开工作簿：{existing_file}")
    opened_wb = excel.Workbooks.Open(existing_file)

    # 修改内容
    ws = opened_wb.ActiveSheet
    ws.Cells(2, 1).Value = "这是从 Python 添加的内容"

    # —— 保存工作簿 ————————————————————————————————

    print("正在保存修改...")
    opened_wb.Save()

    # 另存为新文件
    backup_file = os.path.join(os.getcwd(), "备份_示例工作簿.xlsx")
    opened_wb.SaveAs(backup_file)
    print(f"文件已另存为：{backup_file}")

    # —— 关闭工作簿 ————————————————————————————————

    print("关闭工作簿...")
    opened_wb.Close(SaveChanges=True)

    # 关闭新建的工作簿
    new_wb.Close(SaveChanges=True)

    # 退出 Excel 应用程序
    excel.Quit()
    print("Excel 已关闭。")
