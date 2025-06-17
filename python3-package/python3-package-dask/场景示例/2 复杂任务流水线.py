from dask import delayed
from typing import List, Optional
import logging
import time
import json
from dask.distributed import Client

# 动态任务依赖管理：复杂任务流水线（如 A→B→C依赖、[1, 2, 3] → [2, 4, 6]依赖）

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@delayed
def load_data(file_path: Optional[str] = None) -> List[int]:
    """
    延迟加载数据，支持从内存或文件加载。

    :param file_path: 文件路径（如果提供则从文件加载）
    :return: 数据列表
    """
    try:
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info(f"✅ 从 {file_path} 加载数据成功")
            return data
        else:
            data = [1, 2, 3]
            logger.info("✅ 使用默认数据加载成功")
            return data
    except Exception as e:
        logger.error(f"❌ 加载数据失败：{e}")
        raise


@delayed
def process_data(data: List[int], multiplier: int = 2) -> List[int]:
    """
    延迟处理数据（例如对每个元素乘以一个数）。

    :param data: 输入数据
    :param multiplier: 乘数因子
    :return: 处理后数据
    """
    try:
        result = [i * multiplier for i in data]
        logger.info(f"✅ 数据处理完成：{data} → {result}")
        return result
    except Exception as e:
        logger.error(f"❌ 数据处理失败：{e}")
        raise


@delayed
def save_results(results: List[int], output_file: Optional[str] = None) -> bool:
    """
    延迟保存结果到控制台或文件。

    :param results: 结果数据
    :param output_file: 输出文件路径（如果提供则写入文件）
    :return: 成功与否
    """
    try:
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(results, f)
            logger.info(f"💾 数据已保存至 {output_file}")
        else:
            logger.info(f"📤 输出结果：{results}")
        return True
    except Exception as e:
        logger.error(f"❌ 数据保存失败：{e}")
        return False


def run_pipeline(
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    use_distributed: bool = False
):
    """
    执行完整的任务流水线。

    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    :param use_distributed: 是否启用分布式调度器
    """
    client = None
    if use_distributed:
        try:
            client = Client(n_workers=4)
            logger.info("✅ 已启动分布式调度器")
        except Exception as e:
            logger.warning(f"⚠️ 启动分布式调度器失败，将使用本地模式运行：{e}")

    start_time = time.time()

    # 阶段1：加载数据
    data = load_data(input_file)

    # 阶段2：处理数据
    processed = process_data(data, multiplier=2)

    # 阶段3：保存结果
    result = save_results(processed, output_file)

    # 执行流水线
    success = result.compute()

    total_time = time.time() - start_time
    logger.info(f"⏱️ 总耗时：{total_time:.2f} 秒")
    logger.info(f"✅ 流水线执行 {'成功' if success else '失败'}")

    if client:
        client.close()


if __name__ == "__main__":
    # 示例文件路径（可自定义）
    input_file = "input_data.json"
    output_file = "output_result.json"

    # 示例输入数据
    example_input = [1, 2, 3]
    with open(input_file, 'w') as f:
        json.dump(example_input, f)

    # 运行流水线
    run_pipeline(input_file=input_file, output_file=output_file, use_distributed=False)
