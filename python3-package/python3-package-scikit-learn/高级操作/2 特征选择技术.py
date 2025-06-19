from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import classification_report
import numpy as np


def load_data():
    """
    加载乳腺癌数据集（二分类任务）

    返回:
        X (np.ndarray): 特征矩阵
        y (np.ndarray): 标签向量
    """
    data = load_breast_cancer()
    X, y = data.data, data.target
    return X, y


def build_pipeline(selector_name='SelectKBest'):
    """
    构建包含预处理、特征选择和分类器的完整管道

    参数:
        selector_name (str): 特征选择方法名称 ('SelectKBest' 或 'RFE')

    返回:
        pipeline (Pipeline): 完整的机器学习管道
    """
    if selector_name == 'SelectKBest':
        selector = SelectKBest(score_func=f_classif, k=5)
    elif selector_name == 'RFE':
        selector = RFE(
            estimator=RandomForestClassifier(n_estimators=100, random_state=42),
            n_features_to_select=5,
            step=1
        )
    else:
        raise ValueError("不支持的特征选择方法")

    pipeline = Pipeline([
        ('scaler', StandardScaler()),           # 预处理：标准化
        ('feature_selector', selector),         # 特征选择
        ('classifier', RandomForestClassifier(random_state=42))  # 分类模型
    ])

    return pipeline


def run_feature_selection(X_train, X_test, y_train, y_test, method='SelectKBest'):
    """
    执行特征选择 + 模型训练与评估

    参数:
        X_train (np.ndarray): 训练特征
        X_test (np.ndarray): 测试特征
        y_train (np.ndarray): 训练标签
        y_test (np.ndarray): 测试标签
        method (str): 使用的特征选择方法名

    返回:
        report (str): 分类报告字符串
    """
    # 构建管道
    pipeline = build_pipeline(method)

    # 训练模型
    pipeline.fit(X_train, y_train)

    # 预测并评估
    y_pred = pipeline.predict(X_test)

    # 获取选中的特征索引
    selector = pipeline.named_steps['feature_selector']
    if hasattr(selector, 'get_support'):
        selected_features = selector.get_support(indices=True)
        print(f"\n【{method}】选中特征索引:", selected_features)

    # 输出报告
    report = classification_report(y_test, y_pred, target_names=['良性', '恶性'])
    return report


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


def main():
    # 1. 加载数据
    X, y = load_data()

    # 2. 数据划分
    X_train, X_test, y_train, y_test = split_data(X, y)

    # 3. 使用 SelectKBest 进行特征选择
    print("✅ 使用 SelectKBest 进行特征选择:")
    report_kbest = run_feature_selection(X_train, X_test, y_train, y_test, method='SelectKBest')
    print(report_kbest)

    # 4. 使用 RFE 进行特征选择
    print("✅ 使用 RFE 进行特征选择:")
    report_rfe = run_feature_selection(X_train, X_test, y_train, y_test, method='RFE')
    print(report_rfe)


if __name__ == "__main__":
    main()
