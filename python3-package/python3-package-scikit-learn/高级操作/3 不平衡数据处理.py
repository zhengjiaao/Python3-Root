from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import make_pipeline as make_imb_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(random_state=42):
    """
    生成模拟的不平衡二分类数据集

    返回:
        X (np.ndarray): 特征矩阵
        y (np.ndarray): 标签向量
    """
    # 设置类别比例为 9:1 的不平衡数据
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=2,
        n_classes=2,
        weights=[0.9, 0.1],
        random_state=random_state
    )
    return X, y


def split_data(X, y, test_size=0.2, random_state=42):
    """
    划分训练集和测试集

    参数:
        X (np.ndarray): 特征数据
        y (np.ndarray): 标签数据
        test_size (float): 测试集比例
        random_state (int): 随机种子

    返回:
        X_train, X_test, y_train, y_test: 四组划分结果
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def build_smote_pipeline():
    """
    构建仅使用 SMOTE 的管道

    返回:
        pipeline (Pipeline): 包含标准化、SMOTE 和分类器的管道
    """
    pipeline = make_imb_pipeline(
        StandardScaler(),
        SMOTE(sampling_strategy='minority', random_state=42),
        RandomForestClassifier(random_state=42)
    )
    return pipeline


def build_combined_pipeline():
    """
    构建组合采样方法的管道：SMOTE + 随机欠采样

    返回:
        pipeline (Pipeline): 包含标准化、SMOTE、随机欠采样和分类器的管道
    """
    pipeline = make_imb_pipeline(
        StandardScaler(),
        SMOTE(sampling_strategy=0.5, random_state=42),     # 将少数类上采样至 50%
        RandomUnderSampler(sampling_strategy=0.8, random_state=42),  # 多数类下采样至 80%
        RandomForestClassifier(random_state=42)
    )
    return pipeline


def evaluate_model(pipeline, X_train, y_train, X_test, y_test, name="模型"):
    """
    训练并评估模型，输出分类报告与混淆矩阵

    参数:
        pipeline (Pipeline): 模型管道
        X_train (np.ndarray): 训练特征
        y_train (np.ndarray): 训练标签
        X_test (np.ndarray): 测试特征
        y_test (np.ndarray): 测试标签
        name (str): 模型名称（用于打印）

    返回:
        report (str): 分类报告字符串
    """
    print(f"\n🚀 开始训练：{name}")

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    print("✅ 分类报告:")
    report = classification_report(y_test, y_pred, target_names=['类别 0', '类别 1'])
    print(report)

    # 绘制混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('预测值')
    plt.ylabel('真实值')
    plt.title(f"{name} 混淆矩阵")
    plt.savefig(f"confusion_matrix_{name}.png", dpi=150)
    plt.close()

    return report


def plot_class_distribution(y, title="类别分布"):
    """
    可视化数据集中各类别样本数量

    参数:
        y (np.ndarray): 标签数组
        title (str): 图表标题
    """
    class_counts = np.bincount(y)
    plt.figure(figsize=(6, 4))
    sns.barplot(x=np.arange(len(class_counts)), y=class_counts, palette="viridis")
    plt.xticks(np.arange(len(class_counts)), [f'类别 {i}' for i in range(len(class_counts))])
    plt.xlabel("类别")
    plt.ylabel("样本数")
    plt.title(title)
    plt.grid(axis='y', alpha=0.3)
    plt.savefig(f"class_distribution_{title}.png", dpi=150)
    plt.close()


def main():
    # 1. 加载数据
    X, y = load_data()
    print("📊 原始数据类别分布:", dict(zip(*np.unique(y, return_counts=True)))
    plot_class_distribution(y, "原始数据")

    # 2. 数据划分
    X_train, X_test, y_train, y_test = split_data(X, y)

    # 3. 构建并评估 SMOTE 管道
    smote_pipeline = build_smote_pipeline()
    evaluate_model(smote_pipeline, X_train, y_train, X_test, y_test, name="SMOTE")

    # 4. 构建并评估组合采样管道
    combined_pipeline = build_combined_pipeline()
    evaluate_model(combined_pipeline, X_train, y_train, X_test, y_test, name="SMOTE+欠采样")


if __name__ == "__main__":
    main()
