import win32com.client
import os

if __name__ == '__main__':
    # 启动 Excel
    excel_app = win32com.client.Dispatch('Excel.Application')
    excel_app.Visible = False  # 不显示 Excel 程序

    # 新建工作簿
    wb = excel_app.Workbooks.Add()
    ws = wb.ActiveSheet

    # 写入数据
    ws.Range('A1').Value = 'Hello pywin32!'

    # 获取当前脚本所在目录并保存文件
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'test.xlsx')

    # 保存文件
    wb.SaveAs(file_path)
    print(f'Excel 文件已保存至：{file_path}')

    # 关闭工作簿和 Excel 应用程序
    wb.Close(True)
    excel_app.Quit()
