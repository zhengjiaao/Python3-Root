import pandas as pd
import numpy as np
from sklearn.datasets import make_blobs
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

def generate_data(n_samples=1000, centers=4, noise_samples=50):
    """
    生成模拟客户数据并添加噪声

    参数:
        n_samples (int): 样本数量
        centers (int): 真实聚类中心数
        noise_samples (int): 噪声样本数

    返回:
        X (np.array): 特征矩阵
        true_labels (np.array): 真实标签（含 -1 表示异常值）
    """
    # 生成基础簇数据
    X, true_labels = make_blobs(
        n_samples=n_samples,
        centers=centers,
        cluster_std=1.2,
        random_state=42
    )

    # 添加噪声点
    noise = np.random.rand(noise_samples, 2) * 20 - 10
    X = np.vstack([X, noise])
    true_labels = np.concatenate([true_labels, np.full(noise_samples, -1)])

    return X, true_labels

def standardize_data(X):
    """
    对数据进行标准化处理

    参数:
        X (np.array): 特征矩阵

    返回:
        X_scaled (np.array): 标准化后的特征矩阵
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled

def find_optimal_clusters(X, k_range=range(2, 10)):
    """
    使用轮廓系数法确定最佳聚类数

    参数:
        X (np.array): 标准化后的特征矩阵
        k_range (range): 要尝试的聚类数范围

    返回:
        best_k (int): 最佳聚类数
        silhouette_scores (list): 各k值对应的轮廓系数
    """
    silhouette_scores = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X)
        score = silhouette_score(X, labels)
        silhouette_scores.append(score)

    best_k = k_range[np.argmax(silhouette_scores)]
    return best_k, silhouette_scores

def perform_clustering(X, best_k):
    """
    执行多种聚类算法

    参数:
        X (np.array): 标准化后的特征矩阵
        best_k (int): 推荐的聚类数

    返回:
        clustering_results (dict): 包含各类聚类结果的字典
    """
    # KMeans
    kmeans = KMeans(n_clusters=best_k, random_state=42)
    kmeans_labels = kmeans.fit_predict(X)

    # DBSCAN
    dbscan = DBSCAN(eps=0.5, min_samples=10)
    dbscan_labels = dbscan.fit_predict(X)

    # 高斯混合模型
    gmm = GaussianMixture(n_components=best_k, random_state=42)
    gmm_labels = gmm.fit_predict(X)

    return {
        'KMeans': kmeans_labels,
        'DBSCAN': dbscan_labels,
        'GMM': gmm_labels
    }

def reduce_dimensions(X):
    """
    使用PCA降维用于可视化

    参数:
        X (np.array): 标准化后的特征矩阵

    返回:
        X_pca (np.array): 降维后的二维表示
    """
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    return X_pca

def create_result_df(X_pca, true_labels, clustering_results):
    """
    创建包含聚类结果的 DataFrame 用于绘图

    参数:
        X_pca (np.array): 降维后的二维数据
        true_labels (np.array): 真实标签
        clustering_results (dict): 各模型聚类结果

    返回:
        results_df (DataFrame): 包含所有信息的结果表
    """
    data = {
        'PCA1': X_pca[:, 0],
        'PCA2': X_pca[:, 1],
        'True_Labels': true_labels
    }
    data.update(clustering_results)
    results_df = pd.DataFrame(data)
    return results_df

def plot_silhouette_scores(k_range, silhouette_scores):
    """
    绘制轮廓系数曲线以辅助选择聚类数

    参数:
        k_range (range): 聚类数范围
        silhouette_scores (list): 对应的轮廓系数
    """
    plt.figure(figsize=(10, 6))
    plt.plot(k_range, silhouette_scores, 'bo-')
    plt.xlabel('聚类数 (k)')
    plt.ylabel('轮廓系数')
    plt.title('轮廓系数法确定最佳聚类数')
    plt.grid(alpha=0.3)
    plt.savefig("silhouette_scores.png", dpi=150)
    plt.close()

def plot_clustering_results(results_df):
    """
    可视化各种聚类算法结果对比

    参数:
        results_df (DataFrame): 包含聚类结果的数据框
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 真实标签
    sns.scatterplot(
        x='PCA1', y='PCA2', hue='True_Labels',
        palette='viridis', data=results_df, ax=axes[0, 0]
    )
    axes[0, 0].set_title("真实标签分布")

    # KMeans结果
    sns.scatterplot(
        x='PCA1', y='PCA2', hue='KMeans',
        palette='tab10', data=results_df, ax=axes[0, 1]
    )
    axes[0, 1].set_title(f"KMeans聚类 (k={results_df['KMeans'].nunique()})")

    # DBSCAN结果
    sns.scatterplot(
        x='PCA1', y='PCA2', hue='DBSCAN',
        palette='Set2', data=results_df, ax=axes[1, 0]
    )
    axes[1, 0].set_title("DBSCAN聚类")

    # GMM结果
    sns.scatterplot(
        x='PCA1', y='PCA2', hue='GMM',
        palette='tab10', data=results_df, ax=axes[1, 1]
    )
    axes[1, 1].set_title("高斯混合模型聚类")

    plt.tight_layout()
    plt.savefig("clustering_results.png", dpi=150)
    plt.close()

def main():
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 1. 生成模拟数据
    X, true_labels = generate_data()

    # 2. 数据标准化
    X_scaled = standardize_data(X)

    # 3. 确定最佳聚类数
    best_k, silhouette_scores = find_optimal_clusters(X_scaled)
    print(f"推荐聚类数: {best_k}") # 输出：推荐聚类数 4

    # 4. 绘制轮廓系数曲线
    plot_silhouette_scores(range(2, 10), silhouette_scores)

    # 5. 执行聚类分析
    clustering_results = perform_clustering(X_scaled, best_k)

    # 6. 降维用于可视化
    X_pca = reduce_dimensions(X_scaled)

    # 7. 构建结果表格
    results_df = create_result_df(X_pca, true_labels, clustering_results)

    # 8. 可视化聚类结果
    plot_clustering_results(results_df)

if __name__ == "__main__":
    main()
