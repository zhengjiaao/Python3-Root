from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_california_housing


class LogTransformer(BaseEstimator, TransformerMixin):
    """
    自定义日志变换器，支持对指定列或全部特征应用 log(x + constant)

    参数:
        add_constant (float): 加到原始值上的常数，防止 log(0)
        features (list or None): 要变换的列名列表。若为 None，则对所有列进行变换
    """

    def __init__(self, add_constant=1.0, features=None):
        self.add_constant = add_constant
        self.features = features
        self._input_is_df = False  # 是否输入的是 DataFrame

    def fit(self, X, y=None):
        """
        检查输入数据格式并记录是否是 DataFrame

        参数:
            X (np.ndarray or pd.DataFrame): 输入特征矩阵
            y: 忽略（兼容 scikit-learn 接口）

        返回:
            self
        """
        if isinstance(X, pd.DataFrame):
            self._input_is_df = True
            if self.features is not None:
                missing_features = set(self.features) - set(X.columns)
                if missing_features:
                    raise ValueError(f"以下列不存在于 DataFrame 中：{missing_features}")
        elif isinstance(X, np.ndarray):
            self._input_is_df = False
            if self.features is not None:
                raise ValueError("当输入为 NumPy 数组时，不能指定 features 列名")
        else:
            raise TypeError("输入必须为 pandas DataFrame 或 NumPy 数组")

        return self

    def transform(self, X):
        """
        对数据执行 log(x + add_constant) 变换

        参数:
            X (np.ndarray or pd.DataFrame): 输入特征矩阵

        返回:
            X_transformed (np.ndarray or pd.DataFrame): 变换后的数据
        """
        X = X.copy()

        if self._input_is_df:
            for feature in self.features:
                X[feature] = np.log(X[feature] + self.add_constant)
        else:
            X = np.log(X + self.add_constant)

        return X


def load_data():
    """
    加载加州房价数据集

    返回:
        X (pd.DataFrame): 特征数据（DataFrame 格式）
        y (np.array): 标签数据
    """
    housing = fetch_california_housing()
    X = pd.DataFrame(housing.data, columns=housing.feature_names)
    y = housing.target
    return X, y


def build_pipeline():
    """
    构建包含自定义 LogTransformer 和 StandardScaler 的管道

    返回:
        pipeline (Pipeline): 构建好的模型管道
    """
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    pipeline = Pipeline([
        ('log_transform', LogTransformer(add_constant=1.0, features=['MedInc', 'HouseAge'])),
        ('scaler', StandardScaler())
    ])
    return pipeline


def apply_transformation(X, pipeline):
    """
    应用预处理管道进行数据变换

    参数:
        X (pd.DataFrame): 原始特征数据
        pipeline (Pipeline): 已构建的管道

    返回:
        X_transformed (np.array): 转换后的特征数组
    """
    X_transformed = pipeline.fit_transform(X)
    return X_transformed


def main():
    # 1. 加载数据
    X, y = load_data()

    # 2. 构建预处理管道
    pipeline = build_pipeline()

    # 3. 应用变换
    X_transformed = apply_transformation(X, pipeline)

    # 4. 输出部分结果查看效果
    print("原始数据前5行:")
    print(X.head())

    print("\n转换后数据前5行:")
    print(pd.DataFrame(X_transformed, columns=X.columns).head())


if __name__ == "__main__":
    main()
