import win32com.client
import os

if __name__ == '__main__':
    print("=== 批量处理 Excel 文件 - 添加【总销售额】列 ===")

    # 启动 Excel 应用程序
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = False  # 不显示界面
    excel.DisplayAlerts = False  # 禁止弹窗提示

    try:
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"正在扫描目录：{current_dir}")

        # 查找所有 .xls 和 .xlsx 文件（排除已有输出文件）
        files = [f for f in os.listdir(current_dir)
                 if f.lower().endswith(('.xls', '.xlsx')) and not f.startswith('输出_')]

        if not files:
            print("⚠️ 未找到任何可处理的 Excel 文件。")
            exit()

        print(f"共发现 {len(files)} 个文件需要处理。")

        for file in files:
            file_path = os.path.join(current_dir, file)
            print(f"\n📄 正在处理文件：{file}")

            try:
                # 打开工作簿
                wb = excel.Workbooks.Open(file_path)
                ws = wb.Sheets(1)  # 使用第一个工作表
                print(f"   已打开工作表：{ws.Name}")

                # 检测最后一列和行
                last_col = ws.UsedRange.Columns.Count
                last_row = ws.UsedRange.Rows.Count

                # 插入“总销售额”列标题
                ws.Cells(1, last_col + 1).Value = "总销售额"
                print(f"   新增列位置：第 {last_col + 1} 列")

                # 遍历数据行并插入公式计算总和（从第2行开始）
                for row in range(2, last_row + 1):
                    start_col = 2  # B列开始
                    end_col = last_col  # 动态结束列
                    formula = f"=SUM({ws.Cells(row, start_col).Address}:{ws.Cells(row, end_col).Address})"
                    ws.Cells(row, last_col + 1).Formula = formula

                # 构建输出文件名
                new_file = os.path.join(current_dir, f"输出_{file}")
                print(f"   正在保存为：{new_file}")

                # 另存为新文件
                wb.SaveAs(new_file)
                wb.Close(SaveChanges=True)
                print(f"✅ 文件处理完成：{file} -> 输出_{file}")

            except Exception as e:
                print(f"❌ 处理文件 {file} 时发生错误：{e}")
                continue  # 继续下一个文件

    except Exception as e:
        print(f"🚨 程序运行出错：{e}")

    finally:
        # 关闭 Excel
        try:
            excel.Quit()
        except:
            pass
        print("\n🔚 Excel 已退出。")
