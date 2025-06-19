import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
import matplotlib.pyplot as plt
import seaborn as sns


def load_data():
    """
    加载加州房价数据集

    返回:
        X (np.ndarray): 特征数据
        y (np.ndarray): 目标值（房价中位数）
        feature_names (list): 特征名称列表
    """
    housing = fetch_california_housing()
    X, y = housing.data, housing.target
    feature_names = housing.feature_names
    return X, y, feature_names


def create_dataframe(X, y, feature_names):
    """
    将特征和目标值组合为 DataFrame 方便后续分析

    参数:
        X (np.ndarray): 特征数据
        y (np.ndarray): 标签数据
        feature_names (list): 特征名称列表

    返回:
        df (DataFrame): 合并后的数据集
    """
    df = pd.DataFrame(X, columns=feature_names)
    df["MedHouseVal"] = y
    return df


def split_data(X, y, test_size=0.2, random_state=42):
    """
    划分训练集和测试集

    参数:
        X (np.ndarray): 特征数据
        y (np.ndarray): 标签数据
        test_size (float): 测试集比例
        random_state (int): 随机种子

    返回:
        X_train, X_test, y_train, y_test: 划分后的四组数据
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def build_pipeline():
    """
    构建模型管道：标准化 + 随机森林回归器

    返回:
        pipeline (Pipeline): 模型流程管道
    """
    pipeline = make_pipeline(
        StandardScaler(),
        RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    )
    return pipeline


def define_param_grid():
    """
    定义网格搜索参数空间

    返回:
        param_grid (dict): 参数字典
    """
    param_grid = {
        'randomforestregressor__max_depth': [None, 10, 20],
        'randomforestregressor__min_samples_split': [2, 5, 10]
    }
    return param_grid


def perform_grid_search(pipeline, param_grid, X_train, y_train):
    """
    执行网格搜索寻找最优超参数

    参数:
        pipeline (Pipeline): 模型管道
        param_grid (dict): 参数网格
        X_train (np.ndarray): 训练特征
        y_train (np.ndarray): 训练标签

    返回:
        grid_search (GridSearchCV): 网格搜索结果对象
    """
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=5,
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)
    return grid_search


def evaluate_model(y_true, y_pred):
    """
    评估模型性能指标

    参数:
        y_true (np.ndarray): 真实值
        y_pred (np.ndarray): 预测值

    返回:
        metrics (dict): 包含 RMSE 和 R² 的字典
    """
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    return {'rmse': rmse, 'r2': r2}


def get_feature_importances(best_model, feature_names):
    """
    获取随机森林模型中的特征重要性排序

    参数:
        best_model (Pipeline): 最佳模型
        feature_names (list): 原始特征名称列表

    返回:
        importance_df (DataFrame): 排序后的特征重要性表
    """
    rf = best_model.named_steps['randomforestregressor']
    importances = rf.feature_importances_
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    }).sort_values('Importance', ascending=False).head(20)
    return importance_df


def plot_feature_importance(importance_df):
    """
    绘制特征重要性柱状图

    参数:
        importance_df (DataFrame): 特征重要性数据框
    """
    plt.figure(figsize=(12, 8))
    sns.barplot(x='Importance', y='Feature', data=importance_df, palette="viridis")
    plt.title("房价预测特征重要性 (Top 20)")
    plt.tight_layout()
    plt.savefig("housing_feature_importance.png", dpi=150)
    plt.close()


def plot_actual_vs_predicted(y_true, y_pred):
    """
    绘制实际值 vs 预测值对比图

    参数:
        y_true (np.ndarray): 真实值
        y_pred (np.ndarray): 预测值
    """
    plt.figure(figsize=(10, 8))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], 'r--')
    plt.xlabel("实际房价")
    plt.ylabel("预测房价")
    plt.title("实际值 vs 预测值")
    plt.grid(alpha=0.3)
    plt.savefig("housing_prediction_scatter.png", dpi=150)
    plt.close()


def main():
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 1. 加载数据
    X, y, feature_names = load_data()
    df = create_dataframe(X, y, feature_names)

    # 2. 数据划分
    X_train, X_test, y_train, y_test = split_data(X, y)

    # 3. 构建模型管道
    pipeline = build_pipeline()

    # 4. 定义参数网格
    param_grid = define_param_grid()

    # 5. 执行网格搜索
    grid_search = perform_grid_search(pipeline, param_grid, X_train, y_train)
    best_model = grid_search.best_estimator_

    # 6. 输出最佳参数和得分
    print(f"最佳参数: {grid_search.best_params_}")
    print(f"最佳得分 (Neg Mean Squared Error): {-grid_search.best_score_:.4f}")

    # 7. 预测与评估
    y_pred = best_model.predict(X_test)
    metrics = evaluate_model(y_test, y_pred)
    print(f"测试集 RMSE: {metrics['rmse']:.4f}")
    print(f"测试集 R²: {metrics['r2']:.4f}")

    # 8. 分析特征重要性
    importance_df = get_feature_importances(best_model, feature_names)
    plot_feature_importance(importance_df)

    # 9. 可视化实际值 vs 预测值
    plot_actual_vs_predicted(y_test, y_pred)


if __name__ == "__main__":
    main()
