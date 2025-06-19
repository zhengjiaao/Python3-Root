import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import StandardScaler

def load_data():
    """
    加载鸢尾花数据集

    返回:
        X (np.array): 标准化前的特征矩阵
        y (np.array): 标签向量
        feature_names (list): 特征名称列表
        target_names (list): 目标类别名称
    """
    iris = datasets.load_iris()
    X, y = iris.data, iris.target
    feature_names = iris.feature_names
    target_names = iris.target_names
    return X, y, feature_names, target_names

def standardize_data(X):
    """
    对输入数据进行标准化处理（均值为0，方差为1）

    参数:
        X (np.array): 原始特征矩阵

    返回:
        X_scaled (np.array): 标准化后的特征矩阵
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled

def get_dim_reduction_models():
    """
    获取降维模型字典，包含 PCA、LDA 和 t-SNE

    返回:
        models (dict): 模型名 -> 实例 的映射
    """
    return {
        "PCA (2D)": PCA(n_components=2, random_state=42),
        "LDA (2D)": LDA(n_components=2),
        "t-SNE (2D)": TSNE(n_components=2, perplexity=30, random_state=42)
    }

def apply_dimensionality_reduction(model, X, y=None):
    """
    应用降维模型，支持是否需要标签（如 LDA）

    参数:
        model: 降维模型实例
        X (np.array): 输入数据
        y (np.array or None): 标签（仅用于 LDA）

    返回:
        X_reduced (np.array): 降维后的数据
    """
    if isinstance(model, LDA):
        return model.fit_transform(X, y)
    else:
        return model.fit_transform(X)

def plot_2d_results(X_reduced_dict, y, target_names):
    """
    可视化三种降维方法在二维空间的分布情况

    参数:
        X_reduced_dict (dict): 方法名 -> 降维后数据 的映射
        y (np.array): 标签向量
        target_names (list): 类别名称列表
    """
    plt.figure(figsize=(18, 5))
    for i, (name, X_reduced) in enumerate(X_reduced_dict.items()):
        plt.subplot(1, 3, i + 1)
        for target in np.unique(y):
            plt.scatter(
                X_reduced[y == target, 0],
                X_reduced[y == target, 1],
                label=target_names[target],
                alpha=0.8
            )
        plt.title(name)
        plt.xlabel("Component 1")
        plt.ylabel("Component 2")
        plt.grid(alpha=0.3)
        if i == 0:
            plt.legend()
    plt.tight_layout()
    plt.savefig("dimensionality_reduction.png", dpi=150)
    plt.close()

def plot_3d_pca(X, y, target_names):
    """
    使用三维 PCA 进行可视化展示

    参数:
        X (np.array): 输入数据
        y (np.array): 标签向量
        target_names (list): 类别名称列表
    """
    pca_3d = PCA(n_components=3)
    X_pca_3d = pca_3d.fit_transform(X)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    for target in np.unique(y):
        ax.scatter(
            X_pca_3d[y == target, 0],
            X_pca_3d[y == target, 1],
            X_pca_3d[y == target, 2],
            label=target_names[target],
            alpha=0.8,
            depthshade=True
        )

    ax.set_title("PCA 3D 可视化")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_zlabel("PC3")
    ax.legend()
    plt.savefig("pca_3d.png", dpi=150)
    plt.close()

def main():
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 1. 加载数据
    X, y, feature_names, target_names = load_data()

    # 2. 数据标准化
    X_scaled = standardize_data(X)

    # 3. 获取降维模型
    models = get_dim_reduction_models()

    # 4. 执行降维
    X_reduced_dict = {}
    for name, model in models.items():
        X_reduced = apply_dimensionality_reduction(model, X_scaled, y if name == "LDA (2D)" else None)
        X_reduced_dict[name] = X_reduced

    # 5. 可视化 2D 结果
    plot_2d_results(X_reduced_dict, y, target_names)

    # 6. 可视化 3D PCA
    plot_3d_pca(X_scaled, y, target_names)

if __name__ == "__main__":
    main()
