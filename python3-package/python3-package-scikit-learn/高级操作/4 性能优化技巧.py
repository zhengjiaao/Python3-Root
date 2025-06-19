from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.feature_selection import SelectPercentile, chi2, f_classif
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.datasets import fetch_openml
from sklearn.metrics import classification_report
import numpy as np


def load_data():
    """
    加载 MNIST 数据集（手写数字识别），用于演示性能优化技巧

    返回:
        X_train, X_test, y_train, y_test: 划分好的训练集和测试集
    """
    # 使用较小的数据集加快训练速度
    mnist = fetch_openml('mnist_784', version=1, parser='auto')
    X, y = mnist["data"], mnist["target"]

    # 仅使用部分数据加速演示
    idx = np.random.choice(len(X), size=10000, replace=False)
    X = X.iloc[idx]  # ✅ 使用 .iloc 按位置选取
    y = y.iloc[idx]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test


def build_pipeline(feature_selector=None):
    """
    构建机器学习管道，可选特征选择器

    参数:
        feature_selector (TransformerMixin or None): 特征选择方法

    返回:
        pipeline (Pipeline): 包含标准化、特征选择（可选）和分类器的完整管道
    """
    steps = [
        ('scaler', StandardScaler())
    ]
    if feature_selector is not None:
        steps.append(('feature_selector', feature_selector))

    steps.append(('model', HistGradientBoostingClassifier(max_iter=100, random_state=42)))

    return Pipeline(steps)


def perform_grid_search(pipeline, X_train, y_train):
    """
    执行网格搜索并返回最佳模型

    参数:
        pipeline (Pipeline): 原始模型管道
        X_train (np.ndarray): 训练特征
        y_train (np.ndarray): 训练标签

    返回:
        best_model (Pipeline): 网格搜索找到的最佳模型
    """
    param_grid = {
        'model__learning_rate': [0.01, 0.1],
        'model__max_depth': [3, 5]
    }

    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(X_train, y_train)
    print(f"🔍 最佳参数: {grid_search.best_params_}")
    return grid_search.best_estimator_


def train_incremental_model(X_train, y_train):
    """
    使用增量学习处理大数据，适合内存受限场景

    参数:
        X_train (np.ndarray): 训练特征
        y_train (np.ndarray): 训练标签

    返回:
        model (SGDClassifier): 训练完成的增量学习模型
    """
    model = SGDClassifier(loss='log_loss', max_iter=1000, tol=1e-3, random_state=42)
    model.partial_fit(X_train, y_train, classes=np.unique(y_train))
    return model


def evaluate_model(model, X_test, y_test, model_name="模型"):
    """
    评估模型性能并输出报告

    参数:
        model: 分类模型
        X_test (np.ndarray): 测试特征
        y_test (np.ndarray): 测试标签
        model_name (str): 模型名称（用于打印）

    返回:
        accuracy (float): 准确率
    """
    y_pred = model.predict(X_test)
    accuracy = np.mean(y_pred == y_test)
    print(f"\n📊 【{model_name}】测试准确率: {accuracy:.4f}")
    print(classification_report(y_test, y_pred, digits=4))
    return accuracy


def main():
    # 1. 加载数据
    print("📥 正在加载数据...")
    X_train, X_test, y_train, y_test = load_data()

    # 2. 构建包含特征选择的管道
    print("\n⚙️ 构建带特征选择的管道...")
    selector = SelectPercentile(f_classif, percentile=50)  # 支持负值
    pipeline = build_pipeline(selector)

    # 3. 使用所有CPU核心进行网格搜索
    print("\n🚀 开始网格搜索（并行加速）...")
    best_model = perform_grid_search(pipeline, X_train, y_train)

    # 4. 评估优化后模型
    evaluate_model(best_model, X_test, y_test, "HistGradientBoosting + 特征选择")

    # 5. 使用增量学习应对大数据
    print("\n🧠 使用增量学习（适用于内存受限场景）...")
    incremental_model = train_incremental_model(X_train, y_train)
    evaluate_model(incremental_model, X_test, y_test, "SGDClassifier 增量学习")


if __name__ == "__main__":
    main()
