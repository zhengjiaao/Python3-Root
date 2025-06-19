import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split, GridSearchCV, learning_curve, validation_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def load_data():
    """
    加载乳腺癌数据集

    返回:
        X (np.array): 特征矩阵
        y (np.array): 标签向量
    """
    cancer = load_breast_cancer()
    X, y = cancer.data, cancer.target
    return X, y

def split_data(X, y, test_size=0.2, random_state=42):
    """
    划分训练集和测试集（保留类别分布）

    参数:
        X (np.array): 特征矩阵
        y (np.array): 标签向量
        test_size (float): 测试集比例
        random_state (int): 随机种子

    返回:
        X_train, X_test, y_train, y_test: 划分后的四组数据
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )
    return X_train, X_test, y_train, y_test

def build_pipeline():
    """
    构建标准化 + 分类器的管道

    返回:
        pipeline (Pipeline): 管道对象
    """
    return Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', SVC(probability=True, random_state=42))
    ])

def define_param_grid():
    """
    定义参数搜索空间（包含SVM和RandomForest）

    返回:
        param_grid (list): 参数字典列表
    """
    return [
        {
            'classifier': [SVC(probability=True, random_state=42)],
            'classifier__C': [0.1, 1, 10, 100],
            'classifier__gamma': [0.001, 0.01, 0.1, 1],
            'classifier__kernel': ['rbf', 'poly']
        },
        {
            'classifier': [RandomForestClassifier(random_state=42)],
            'classifier__n_estimators': [50, 100, 200],
            'classifier__max_depth': [None, 5, 10, 20],
            'classifier__min_samples_split': [2, 5, 10]
        }
    ]

def perform_grid_search(pipeline, param_grid, X_train, y_train):
    """
    执行网格搜索以寻找最佳模型

    参数:
        pipeline (Pipeline): 模型管道
        param_grid (list): 参数网格
        X_train (np.array): 训练特征
        y_train (np.array): 训练标签

    返回:
        grid_search (GridSearchCV): 网格搜索结果对象
    """
    grid_search = GridSearchCV(
        pipeline,
        param_grid,
        cv=5,
        scoring='roc_auc',
        n_jobs=-1,
        verbose=1
    )
    grid_search.fit(X_train, y_train)
    return grid_search

def evaluate_model(best_model, X_test, y_test):
    """
    在测试集上评估模型性能

    参数:
        best_model (Pipeline): 最佳模型
        X_test (np.array): 测试特征
        y_test (np.array): 测试标签

    返回:
        metrics (dict): 包含准确率和AUC的字典
    """
    y_pred = best_model.predict(X_test)
    y_proba = best_model.predict_proba(X_test)[:, 1]

    test_accuracy = accuracy_score(y_test, y_pred)
    test_auc = roc_auc_score(y_test, y_proba)

    return {'accuracy': test_accuracy, 'auc': test_auc}

def plot_learning_curve(estimator, title, X, y, cv=5, train_sizes=np.linspace(0.1, 1.0, 10)):
    """
    绘制学习曲线

    参数:
        estimator (estimator): 模型
        title (str): 图表标题
        X (np.array): 数据特征
        y (np.array): 数据标签
        cv (int): 交叉验证折数
        train_sizes (array-like): 不同训练集大小

    返回:
        plt: matplotlib.pyplot 对象
    """
    plt.figure(figsize=(10, 6))
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, cv=cv, n_jobs=-1,
        train_sizes=train_sizes, scoring='accuracy'
    )

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.fill_between(
        train_sizes,
        train_scores_mean - train_scores_std,
        train_scores_mean + train_scores_std,
        alpha=0.1, color="r"
    )
    plt.fill_between(
        train_sizes,
        test_scores_mean - test_scores_std,
        test_scores_mean + test_scores_std,
        alpha=0.1, color="g"
    )
    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="训练分数")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="交叉验证分数")

    plt.title(title)
    plt.xlabel("训练样本数")
    plt.ylabel("准确率")
    plt.legend(loc="best")
    plt.grid(alpha=0.3)

    return plt

def plot_validation_curve(estimator, param_name, param_range, X, y, cv=5):
    """
    绘制验证曲线（显示不同超参数下的模型表现）

    参数:
        estimator (estimator): 模型
        param_name (str): 要调优的参数名
        param_range (array-like): 参数取值范围
        X (np.array): 数据特征
        y (np.array): 数据标签
        cv (int): 交叉验证折数

    返回:
        plt: matplotlib.pyplot 对象
    """
    train_scores, test_scores = validation_curve(
        estimator, X, y, param_name=param_name, param_range=param_range,
        cv=cv, scoring="accuracy", n_jobs=-1
    )

    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)

    plt.figure(figsize=(10, 6))
    plt.title(f"验证曲线 ({param_name})")
    plt.xlabel(param_name)
    plt.ylabel("准确率")
    plt.ylim(0.0, 1.1)

    plt.plot(param_range, train_scores_mean, 'o-', color="r", label="训练分数")
    plt.fill_between(
        param_range,
        train_scores_mean - train_scores_std,
        train_scores_mean + train_scores_std,
        alpha=0.1, color="r"
    )

    plt.plot(param_range, test_scores_mean, 'o-', color="g", label="交叉验证分数")
    plt.fill_between(
        param_range,
        test_scores_mean - test_scores_std,
        test_scores_mean + test_scores_std,
        alpha=0.1, color="g"
    )

    plt.legend(loc="best")
    plt.grid(alpha=0.3)
    plt.semilogx()

    return plt

def main():
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 1. 加载数据
    X, y = load_data()

    # 2. 划分训练集和测试集
    X_train, X_test, y_train, y_test = split_data(X, y)

    # 3. 构建模型管道
    pipeline = build_pipeline()

    # 4. 定义参数网格
    param_grid = define_param_grid()

    # 5. 执行网格搜索
    grid_search = perform_grid_search(pipeline, param_grid, X_train, y_train)
    best_model = grid_search.best_estimator_
    print(f"最佳模型: {best_model}")
    print(f"最佳参数: {grid_search.best_params_}")
    print(f"最佳AUC分数: {grid_search.best_score_:.4f}")

    # 6. 评估模型
    metrics = evaluate_model(best_model, X_test, y_test)
    print(f"测试集准确率: {metrics['accuracy']:.4f}")
    print(f"测试集AUC: {metrics['auc']:.4f}")

    # 7. 绘制学习曲线
    plot_learning_curve(
        best_model, "学习曲线", X_train, y_train
    ).savefig("learning_curve.png", dpi=150)
    plt.close()

    # 8. 绘制验证曲线
    if 'svc' in best_model.named_steps['classifier'].__class__.__name__.lower():
        param_name = "classifier__C"
        param_range = [0.001, 0.01, 0.1, 1, 10, 100]
    else:
        param_name = "classifier__n_estimators"
        param_range = [10, 50, 100, 200, 300]

    plot_validation_curve(
        best_model, param_name, param_range, X_train, y_train
    ).savefig("validation_curve.png", dpi=150)
    plt.close()

if __name__ == "__main__":
    main()
