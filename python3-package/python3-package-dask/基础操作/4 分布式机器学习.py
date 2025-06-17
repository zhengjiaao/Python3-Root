from dask_ml.linear_model import LinearRegression
from dask_ml.metrics import mean_squared_error, r2_score
import dask.array as da
import time
from typing import Optional, Tuple

# 场景：并行训练模型（如线性回归）。
#
# 优势：与 Scikit-Learn API 兼容，支持分布式计算。

def generate_data(n_samples: int = 100000,
                  n_features: int = 10,
                  chunk_size: int = 1000) -> Tuple[da.Array, da.Array]:
    """
    生成分布式随机数据集用于线性回归。

    :param n_samples: 样本数
    :param n_features: 特征数
    :param chunk_size: 每个分块大小
    :return: 特征矩阵 X 和标签 y
    """
    X = da.random.random((n_samples, n_features), chunks=(chunk_size, n_features))
    coef = da.random.random((n_features, 1), chunks=(n_features, 1))
    y = X.dot(coef).compute()  # 转换为真实值
    return X, da.from_array(y, chunks=chunk_size)


def train_distributed_model(X: da.Array, y: da.Array) -> Optional[LinearRegression]:
    """
    使用 Dask-ML 训练线性回归模型。

    :param X: 特征数据
    :param y: 标签数据
    :return: 训练好的模型 或 None（失败时）
    """
    try:
        model = LinearRegression()
        model.fit(X, y)
        return model
    except Exception as e:
        print(f"模型训练失败：{e}")
        return None


def evaluate_model(model: LinearRegression, X: da.Array, y: da.Array) -> None:
    """
    对模型进行评估，输出 MSE 和 R²。

    :param model: 已训练的模型
    :param X: 特征数据
    :param y: 真实标签
    """
    try:
        y_pred = model.predict(X).compute()
        y_true = y.compute()

        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)

        print(f"📉 均方误差 (MSE): {mse:.4f}")
        print(f"📈 决定系数 (R²): {r2:.4f}")
    except Exception as e:
        print(f"模型评估失败：{e}")


def run_distributed_ml_pipeline(use_distributed: bool = False) -> None:
    """
    运行完整的分布式机器学习流程。

    :param use_distributed: 是否使用分布式 Client
    """
    client = None
    if use_distributed:
        from dask.distributed import Client
        client = Client(n_workers=4)
        print("✅ 已启动分布式调度器")

    start_time = time.time()

    # 数据生成
    X, y = generate_data()
    print(f"📊 数据形状：X={X.shape}, y={y.shape}")

    # 模型训练
    model = train_distributed_model(X, y)
    if model is None:
        return

    # 模型评估
    evaluate_model(model, X, y)

    end_time = time.time()
    print(f"⏱️ 总耗时：{end_time - start_time:.2f} 秒")

    if client:
        client.close()


if __name__ == "__main__":
    run_distributed_ml_pipeline(use_distributed=False)
