# 导入所需的库
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
import seaborn as sns

# 全局启用中文支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """
    加载手写数字数据集
    
    返回:
        X (array): 特征数据
        y (array): 标签数据
    """
    digits = datasets.load_digits()
    X, y = digits.data, digits.target
    return X, y

def split_data(X, y, test_size=0.2, random_state=42):
    """
    划分训练集和测试集
    
    参数:
        X (array): 特征数据
        y (array): 标签数据
        test_size (float): 测试集比例
        random_state (int): 随机种子
    
    返回:
        X_train (array): 训练特征数据
        X_test (array): 测试特征数据
        y_train (array): 训练标签数据
        y_test (array): 测试标签数据
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test

def create_pipeline():
    """
    创建标准化和SVM分类器的管道
    
    返回:
        pipeline (Pipeline): 标准化 + SVM分类器的管道
    """
    pipeline = make_pipeline(
        StandardScaler(),
        SVC(kernel='rbf', gamma=0.001, C=10, random_state=42)
    )
    return pipeline

def train_model(pipeline, X_train, y_train):
    """
    训练模型
    
    参数:
        pipeline (Pipeline): 标准化 + SVM分类器的管道
        X_train (array): 训练特征数据
        y_train (array): 训练标签数据
    
    返回:
        pipeline (Pipeline): 训练好的模型
    """
    pipeline.fit(X_train, y_train)
    return pipeline

def evaluate_model(y_test, y_pred):
    """
    评估模型性能
    
    参数:
        y_test (array): 测试标签数据
        y_pred (array): 预测标签数据
    
    返回:
        cm (array): 混淆矩阵
    """
    print("分类报告:")
    print(classification_report(y_test, y_pred))
    
    cm = confusion_matrix(y_test, y_pred)
    return cm

def plot_confusion_matrix(cm, digits):
    """
    绘制混淆矩阵
    
    参数:
        cm (array): 混淆矩阵
        digits (Bunch): 手写数字数据集
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=digits.target_names,
                yticklabels=digits.target_names)
    plt.title("手写数字识别混淆矩阵")
    plt.xlabel("预测标签")
    plt.ylabel("真实标签")
    plt.savefig("digits_confusion_matrix.png", dpi=150)
    plt.show()

def visualize_predictions(X_test, y_test, y_pred):
    """
    可视化部分预测结果
    
    参数:
        X_test (array): 测试特征数据
        y_test (array): 测试标签数据
        y_pred (array): 预测标签数据
    """
    fig, axes = plt.subplots(4, 4, figsize=(10, 10))
    for i, ax in enumerate(axes.flat):
        ax.imshow(X_test[i].reshape(8, 8), cmap="binary")
        ax.set_title(f"预测: {y_pred[i]}\n真实: {y_test[i]}")
        ax.axis("off")
    plt.tight_layout()
    plt.savefig("digits_predictions.png", dpi=150)

def main():
    # 加载数据集
    digits = datasets.load_digits()  # 直接加载数据集以获取 digits 对象
    X, y = load_data()
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # 创建管道
    pipeline = create_pipeline()
    
    # 训练模型
    pipeline = train_model(pipeline, X_train, y_train)
    
    # 预测测试集
    y_pred = pipeline.predict(X_test)
    
    # 评估模型
    cm = evaluate_model(y_test, y_pred)
    
    # 绘制混淆矩阵
    plot_confusion_matrix(cm, digits)
    
    # 可视化部分预测结果
    visualize_predictions(X_test, y_test, y_pred)

if __name__ == "__main__":
    main()
