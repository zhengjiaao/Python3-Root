import numpy as np

def main():
    # 创建两个一维数组
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])

    # 元素级加法
    c_add = a + b  # [5, 7, 9]

    # 元素级减法
    c_sub = a - b  # [-3, -3, -3]

    # 元素级乘法（注意不是点积）
    c_mul = a * b  # [4, 10, 18]

    # 元素级除法
    c_div = a / b  # [0.25, 0.4, 0.5]

    # 点积运算（dot product）
    dot_product = np.dot(a, b)  # 1*4 + 2*5 + 3*6 = 32

    # 广播机制示例：标量加法
    broadcast_add = a + 10  # [11, 12, 13]

    # 打印结果
    print("数组 a:", a) #  [1, 2, 3]
    print("数组 b:", b) #  [4, 5, 6]
    print("加法结果:", c_add) # [5, 7, 9]
    print("减法结果:", c_sub) # [-3, -3, -3]
    print("乘法结果:", c_mul) # [4, 10, 18]
    print("除法结果:", c_div) # [0.25, 0.4, 0.5]
    print("点积结果:", dot_product) # 32
    print("广播加法结果:", broadcast_add) # [11, 12, 13]

if __name__ == "__main__":
    main()
