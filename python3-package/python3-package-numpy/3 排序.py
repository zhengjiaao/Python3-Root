import numpy as np

def main():
    # 创建一个一维数组
    arr = np.array([3, 1, 2])

    # 升序排列
    sorted_arr = np.sort(arr)

    # 降序排列
    desc_sorted_arr = -np.sort(-arr)

    # 打印原始数组和排序后的数组
    print("原始数组:", arr) # [3, 1, 2]
    print("升序排列后的数组:", sorted_arr) # [1, 2, 3]
    print("降序排列后的数组:", desc_sorted_arr) # [3, 2, 1]

    # 创建一个多维数组
    multi_dim_arr = np.array([[4, 1, 3], [2, 5, 0]])

    # 对多维数组进行排序（默认按最后一个轴排序）
    sorted_multi_dim = np.sort(multi_dim_arr)

    print("\n多维数组排序结果:")
    print(sorted_multi_dim) # [[0, 3, 4], [0, 2, 5]]

if __name__ == "__main__":
    main()
