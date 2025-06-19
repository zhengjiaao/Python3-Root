import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler, OneHotEncoder, OrdinalEncoder,
    PolynomialFeatures
)
from sklearn.impute import KNNImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


def generate_data(n_samples=1000, n_features=10):
    """
    生成模拟分类数据集

    参数:
        n_samples (int): 样本数量
        n_features (int): 特征数量

    返回:
        df (DataFrame): 包含特征和标签的 DataFrame
    """
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=5,
        n_redundant=2,
        n_classes=2,
        random_state=42
    )

    # 转换为DataFrame
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(1, n_features + 1)])
    df['target'] = y

    # 添加缺失值
    for col in np.random.choice(df.columns[:-1], size=3, replace=False):
        mask = np.random.rand(len(df)) < 0.1
        df.loc[mask, col] = np.nan

    # 添加分类特征
    df['category'] = np.random.choice(['A', 'B', 'C', 'D'], size=len(df))
    df['ordinal'] = np.random.choice(['Low', 'Medium', 'High'], size=len(df))

    return df


def split_data(df, test_size=0.2, random_state=42):
    """
    划分训练集和测试集

    参数:
        df (DataFrame): 原始数据
        test_size (float): 测试集比例
        random_state (int): 随机种子

    返回:
        X_train, X_test, y_train, y_test: 四组划分结果
    """
    X = df.drop('target', axis=1)
    y = df['target']
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def define_feature_types():
    """
    定义各类特征名称列表

    返回:
        numerical_features (list): 数值型特征
        categorical_features (list): 分类型特征
        ordinal_features (list): 有序类别特征
    """
    numerical_features = [f"feature_{i}" for i in range(1, 11)]
    categorical_features = ['category']
    ordinal_features = ['ordinal']
    return numerical_features, categorical_features, ordinal_features


def create_preprocessor(numerical_features, categorical_features, ordinal_features):
    """
    创建预处理管道

    参数:
        numerical_features (list): 数值型特征列名
        categorical_features (list): 分类特征列名
        ordinal_features (list): 有序特征列名

    返回:
        preprocessor (ColumnTransformer): 预处理器对象
    """
    return ColumnTransformer(
        transformers=[
            ('num', Pipeline([
                ('imputer', KNNImputer(n_neighbors=5)),
                ('scaler', StandardScaler()),
                ('poly', PolynomialFeatures(degree=2, include_bias=False))
            ]), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('ord', OrdinalEncoder(categories=[['Low', 'Medium', 'High']]), ordinal_features)
        ],
        remainder='drop'
    )


def build_pipeline(preprocessor):
    """
    构建完整的机器学习管道

    参数:
        preprocessor (ColumnTransformer): 预处理器

    返回:
        pipeline (Pipeline): 完整的模型管道
    """
    return Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42, n_jobs=-1))
    ])


def train_model(pipeline, X_train, y_train):
    """
    训练模型

    参数:
        pipeline (Pipeline): 模型管道
        X_train (DataFrame): 训练特征
        y_train (Series): 训练标签

    返回:
        pipeline (Pipeline): 已训练好的模型
    """
    pipeline.fit(X_train, y_train)
    return pipeline


def evaluate_model(pipeline, X_test, y_test):
    """
    在测试集上评估模型性能

    参数:
        pipeline (Pipeline): 训练好的模型
        X_test (DataFrame): 测试特征
        y_test (Series): 测试标签

    返回:
        accuracy (float): 准确率
    """
    y_pred = pipeline.predict(X_test)
    return accuracy_score(y_test, y_pred)


def plot_missing_values_before(X_train):
    """
    可视化原始数据中的缺失值分布

    参数:
        X_train (DataFrame): 训练特征
    """
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.heatmap(X_train.isna(), cbar=False, cmap='viridis')
    plt.title("缺失值分布 (原始数据)")
    plt.tight_layout()


def plot_numerical_distributions(X_train, X_train_transformed, numerical_features):
    """
    绘制数值特征在标准化前后的分布对比

    参数:
        X_train (DataFrame): 原始训练数据
        X_train_transformed (np.array): 预处理后数据
        numerical_features (list): 数值特征列名
    """
    plt.figure(figsize=(15, 10))
    for i, feature in enumerate(numerical_features[:4]):
        plt.subplot(4, 2, 2 * i + 1)
        sns.histplot(X_train[feature], kde=True, color='blue')
        plt.title(f"{feature} (原始)")

        plt.subplot(4, 2, 2 * i + 2)
        feature_idx = numerical_features.index(feature)
        sns.histplot(X_train_transformed[:, feature_idx], kde=True, color='green')
        plt.title(f"{feature} (标准化后)")


def plot_categorical_encoding(X_train, X_train_transformed, categorical_features, cat_encoder):
    """
    绘制分类特征编码前后对比图

    参数:
        X_train (DataFrame): 原始训练数据
        X_train_transformed (np.array): 预处理后数据
        categorical_features (list): 分类特征列名
        cat_encoder (OneHotEncoder): 分类编码器
    """
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    sns.countplot(x='category', data=X_train)
    plt.title("原始分类特征分布")

    plt.subplot(1, 2, 2)
    cat_feature_names = cat_encoder.get_feature_names_out(categorical_features)
    start_idx = len([f"feature_{i}" for i in range(1, 11)])  # 数值特征数量
    end_idx = start_idx + len(cat_feature_names)

    cat_values = X_train_transformed[:, start_idx:end_idx]
    cat_df = pd.DataFrame(cat_values, columns=cat_feature_names)
    sns.countplot(data=cat_df.melt(), x='variable', hue='value')
    plt.title("One-Hot编码后分布")
    plt.xticks(rotation=45)


def main():
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 1. 生成数据
    df = generate_data()

    # 2. 数据划分
    X_train, X_test, y_train, y_test = split_data(df)

    # 3. 定义特征类型
    numerical_features, categorical_features, ordinal_features = define_feature_types()

    # 4. 创建预处理器
    preprocessor = create_preprocessor(numerical_features, categorical_features, ordinal_features)

    # 5. 构建完整管道
    pipeline = build_pipeline(preprocessor)

    # 6. 训练模型
    pipeline = train_model(pipeline, X_train, y_train)

    # 7. 评估模型
    accuracy = evaluate_model(pipeline, X_test, y_test)
    print(f"模型准确率: {accuracy:.4f}")

    # 8. 可视化预处理效果
    plot_missing_values_before(X_train)

    X_train_transformed = preprocessor.fit_transform(X_train)
    plot_numerical_distributions(X_train, X_train_transformed, numerical_features)
    plt.tight_layout()
    plt.savefig("feature_distribution_comparison.png", dpi=150)
    plt.close()

    cat_encoder = preprocessor.named_transformers_['cat']
    plot_categorical_encoding(X_train, X_train_transformed, categorical_features, cat_encoder)
    plt.tight_layout()
    plt.savefig("categorical_encoding.png", dpi=150)
    plt.close()


if __name__ == "__main__":
    main()
