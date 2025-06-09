import numpy as np


def main() -> None:
    """
    NumPy 数组创建示例：
    包括从列表创建、零数组、全1数组、等差数列、等分数组、随机数组等。
    """

    # 1. 从 Python 列表创建数组
    arr = np.array([1, 2, 3])
    print("从列表创建数组:", arr)

    # 2. 创建全零数组 (2行3列)
    zeros = np.zeros((2, 3))  # 默认浮点型 float64
    print("\n全零数组:\n", zeros)

    # 3. 创建全为1的数组 (3行2列)
    ones = np.ones((3, 2))
    print("\n全为1的数组:\n", ones)

    # 4. 创建等差数列数组，从0到10步长2
    seq_arange = np.arange(0, 10, 2)
    print("\n等差数列（arange）:", seq_arange)

    # 5. 创建等分数列，在0到1之间分成5个数（包含端点）
    seq_linspace = np.linspace(0, 1, 5)
    print("\n等分数列（linspace）:", seq_linspace)

    # 6. 创建随机数组（0~1之间的随机数，3个元素）
    rand_arr = np.random.rand(3)
    print("\n随机数组（rand）:", rand_arr)

    # 7. 创建指定形状的随机整数数组（例如：2x4，数值范围0~10）
    rand_int_arr = np.random.randint(0, 10, size=(2, 4))
    print("\n随机整数数组（randint）:\n", rand_int_arr)


if __name__ == "__main__":
    main()
