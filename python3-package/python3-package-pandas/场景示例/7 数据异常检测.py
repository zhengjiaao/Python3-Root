import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 场景：使用统计方法检测交易数据中的异常值
if __name__ == '__main__':
    # 创建模拟交易数据
    np.random.seed(123)
    normal_trans = np.round(np.random.normal(loc=150, scale=30, size=95), 2)
    outliers = [5.0, 600.0, 2.5, 800.0, 1.0]
    all_trans = np.concatenate([normal_trans, outliers])

    transaction_df = pd.DataFrame({
        '交易ID': range(1, 101),
        '金额': all_trans
    })

    # Z-Score 异常检测
    mean = transaction_df['金额'].mean()
    std = transaction_df['金额'].std()
    transaction_df['Z异常'] = abs((transaction_df['金额'] - mean) / std) > 3

    # IQR 异常检测
    Q1 = transaction_df['金额'].quantile(0.25)
    Q3 = transaction_df['金额'].quantile(0.75)
    IQR = Q3 - Q1
    transaction_df['IQR异常'] = (transaction_df['金额'] < (Q1 - 1.5 * IQR)) | \
                                (transaction_df['金额'] > (Q3 + 1.5 * IQR))

    # 综合标记异常
    transaction_df['异常'] = transaction_df['Z异常'] | transaction_df['IQR异常']

    # 打印结果
    print("\n🔴 检测到的异常交易记录:")
    print(transaction_df[transaction_df['异常']][['交易ID', '金额', 'Z异常', 'IQR异常']])

    # 数据分布直方图
    plt.figure(figsize=(8, 4))
    plt.hist(transaction_df['金额'], bins=30, color='skyblue', edgecolor='black')
    plt.title("交易金额分布")
    plt.xlabel("金额")
    plt.ylabel("频数")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("amount_distribution.png")
    plt.close()

    # 异常点可视化
    colors = np.where(transaction_df['异常'], 'red', 'blue')

    plt.figure(figsize=(10, 6))
    plt.scatter(
        transaction_df['交易ID'],
        transaction_df['金额'],
        c=colors,
        alpha=0.7
    )
    plt.axhline(y=Q1 - 1.5 * IQR, color='r', linestyle='--', label='IQR下限')
    plt.axhline(y=Q3 + 1.5 * IQR, color='r', linestyle='--', label='IQR上限')
    plt.title('交易金额异常检测')
    plt.xlabel('交易ID')
    plt.ylabel('金额')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('anomaly_detection.png')
    plt.close()

    # 输出保存信息
    print(f"\n📊 分布图已保存至：{os.path.abspath('amount_distribution.png')}")
    print(f"📉 异常检测图表已保存至：{os.path.abspath('anomaly_detection.png')}")
