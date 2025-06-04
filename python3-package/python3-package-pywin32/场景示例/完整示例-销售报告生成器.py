import win32com.client
from win32api import RGB
import datetime
import os

def generate_sales_report():
    # 启动 Excel
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True
    excel.DisplayAlerts = False

    try:
        # 创建新工作簿
        wb = excel.Workbooks.Add()
        ws = wb.ActiveSheet
        ws.Name = "销售报告"

        # ===== 1. 准备数据 =====
        headers = ["产品", "Q1", "Q2", "Q3", "Q4", "年度总计"]
        products = [
            ["笔记本", 12000, 15000, 16500, 18000],
            ["显示器", 8000, 9500, 11000, 12500],
            ["服务器", 35000, 38000, 42000, 45000],
            ["配件", 5000, 6500, 7000, 7500]
        ]

        # ===== 2. 写入数据 =====
        # 标题行
        for col, header in enumerate(headers, 1):
            ws.Cells(1, col).Value = header
            ws.Cells(1, col).Font.Bold = True
            ws.Cells(1, col).Interior.Color = RGB(198, 224, 180)  # 浅绿色

        # 产品数据
        for row, product in enumerate(products, 2):
            for col, value in enumerate([product[0]] + product[1:], 1):
                ws.Cells(row, col).Value = value

        # 公式计算
        for row in range(2, len(products) + 2):
            ws.Cells(row, 6).Formula = f"=SUM(B{row}:E{row})"

        # 设置数字格式
        ws.Range("B2:F5").NumberFormat = "#,##0"

        # ===== 3. 创建图表 =====
        # 添加柱状图
        chart = ws.Shapes.AddChart2(201, 51).Chart  # 51=柱状图
        chart.SetSourceData(Source=ws.Range("A1:E5"))
        chart.HasTitle = True
        chart.ChartTitle.Text = "季度产品销售报告"

        # 定位图表
        chart.Parent.Left = ws.Range("H1").Left
        chart.Parent.Top = ws.Range("H1").Top

        # ===== 4. 添加总结 =====
        total_cell = ws.Range("F6")
        total_cell.Value = "=SUM(F2:F5)"
        total_cell.Font.Bold = True
        total_cell.Font.Size = 12
        total_cell.Interior.Color = RGB(255, 255, 0)  # 黄色

        # ===== 5. 格式美化 =====
        # 设置列宽
        ws.Columns("A:F").AutoFit()

        # 添加边框
        data_range = ws.Range("A1:F5")
        for border_id in [7, 8, 9, 10]:  # 左、右、上、下边框
            data_range.Borders(border_id).LineStyle = 1
            data_range.Borders(border_id).Weight = 2

        # ===== 6. 保存报告 =====
        report_date = datetime.datetime.now().strftime("%Y%m%d")
        save_path = os.path.join(os.getcwd(), f"销售报告_{report_date}.xlsx")
        wb.SaveAs(save_path)
        print(f"报告已保存至: {save_path}")

        return save_path

    except Exception as e:
        print(f"生成报告时出错: {str(e)}")
        return None

    finally:
        # 清理资源
        wb.Close(SaveChanges=False)
        excel.Quit()
        del excel


# 运行报告生成器
if __name__ == "__main__":
    report_path = generate_sales_report()
    if report_path:
        print(f"报告生成成功: {report_path}")