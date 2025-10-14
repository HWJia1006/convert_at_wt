import pandas as pd
import os
from collections import OrderedDict

# --- 元素配置区域 ---
# 在这里添加或修改元素及其原子量，脚本会自动适应
# 数据来源：IUPAC (国际纯粹与应用化学联合会)
ATOMIC_MASSES = OrderedDict(
    [
        ("Al", 26.9815385),
        ("Li", 6.94),
        ("Cu", 63.546),
        ("Mg", 24.305),
        ("Zr", 91.224),
        ("Mn", 54.938044),
        # 您可以在这里继续添加，例如:
        # ('Si', 28.0855),
        # ('Fe', 55.845),
    ]
)

# --- 核心计算函数 ---


def wt_to_at(wt_percents: dict) -> dict:
    """
    将质量百分比 (wt%) 转换为原子百分比 (at%)
    :param wt_percents: 包含元素和其质量百分比的字典, e.g., {'Al': 90, 'Cu': 10}
    :return: 包含元素和其原子百分比的字典
    """
    at_percents = {}
    total_moles = 0

    # 检查输入中是否有未知元素
    for element in wt_percents.keys():
        if element not in ATOMIC_MASSES:
            raise ValueError(
                f"错误：元素 '{element}' 的原子量未知。请将其添加到脚本顶部的 ATOMIC_MASSES 字典中。"
            )

    # 1. 计算每个元素的摩尔数
    moles = {
        el: wt / ATOMIC_MASSES[el]
        for el, wt in wt_percents.items()
        if el in ATOMIC_MASSES and wt > 0
    }

    # 2. 计算总摩尔数
    total_moles = sum(moles.values())

    if total_moles == 0:
        return {el: 0 for el in wt_percents.keys()}

    # 3. 计算每个元素的原子百分比
    at_percents = {el: (mol / total_moles) * 100 for el, mol in moles.items()}

    return at_percents


def at_to_wt(at_percents: dict) -> dict:
    """
    将原子百分比 (at%) 转换为质量百分比 (wt%)
    :param at_percents: 包含元素和其原子百分比的字典, e.g., {'Al': 95, 'Cu': 5}
    :return: 包含元素和其质量百分比的字典
    """
    wt_percents = {}
    total_mass = 0

    # 检查输入中是否有未知元素
    for element in at_percents.keys():
        if element not in ATOMIC_MASSES:
            raise ValueError(
                f"错误：元素 '{element}' 的原子量未知。请将其添加到脚本顶部的 ATOMIC_MASSES 字典中。"
            )

    # 1. 计算每个元素的相对质量贡献
    mass_contributions = {
        el: at * ATOMIC_MASSES[el]
        for el, at in at_percents.items()
        if el in ATOMIC_MASSES and at > 0
    }

    # 2. 计算总质量
    total_mass = sum(mass_contributions.values())

    if total_mass == 0:
        return {el: 0 for el in at_percents.keys()}

    # 3. 计算每个元素的质量百分比
    wt_percents = {
        el: (mass / total_mass) * 100 for el, mass in mass_contributions.items()
    }

    return wt_percents


# --- 模式处理函数 ---


def handle_single_point_calculation(elements, conversion_func, from_unit, to_unit):
    """处理单点计算模式"""
    print(f"\n--- 单点计算：{from_unit}% -> {to_unit}% ---")
    print(f"请依次输入以下元素的含量 ({from_unit}%)，如果某个元素不存在，请输入 0。")

    input_percents = {}
    for element in elements:
        while True:
            try:
                value = float(input(f"请输入 {element} 的含量: "))
                if value >= 0:
                    input_percents[element] = value
                    break
                else:
                    print("含量不能为负数，请重新输入。")
            except ValueError:
                print("无效输入，请输入一个数字。")

    # 检查总和是否为100
    total_input = sum(input_percents.values())
    if not (99.9 < total_input < 100.1):
        print(
            f"\n警告：您输入的总含量为 {total_input:.2f}%，不接近100%。计算将继续，但结果可能不准确。"
        )

    # 执行计算
    result_percents = conversion_func(input_percents)

    # 格式化输出
    print("\n--- 计算结果 ---")
    header = ""
    values = ""
    # 保证输出顺序和元素列表一致
    for element in elements:
        header += f"{element}({to_unit}%)".ljust(15)
        value = result_percents.get(element, 0)  # 如果某元素含量为0，结果中可能不存在
        values += f"{value:<15.4f}"

    print(header)
    print("-" * len(header))
    print(values)


def handle_batch_calculation(elements, conversion_func, from_unit, to_unit):
    """处理批量计算模式"""
    print(f"\n--- 批量计算：{from_unit}% -> {to_unit}% ---")

    # 1. 获取CSV文件路径
    while True:
        csv_path = input("请输入CSV文件的路径 (例如: alloys.csv): ")
        try:
            df = pd.read_csv(csv_path)
            print(f"成功读取文件 '{csv_path}'。")
            print("文件前5行预览:")
            print(df.head())
            break
        except FileNotFoundError:
            print(f"错误：找不到文件 '{csv_path}'。请检查文件名和路径是否正确。")
        except Exception as e:
            print(f"读取文件时发生错误: {e}")
            return

    # 2. 获取成分所在的列
    while True:
        try:
            print("\n文件中的列:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}: {col}")
            start_col_idx = int(input(f"请输入成分所在的起始列号 (从1开始): ")) - 1
            end_col_idx = int(input(f"请输入成分所在的结束列号 (从1开始): ")) - 1

            if 0 <= start_col_idx <= end_col_idx < len(df.columns):
                element_cols = df.columns[start_col_idx : end_col_idx + 1].tolist()
                break
            else:
                print("错误：列号范围无效，请重新输入。")
        except ValueError:
            print("错误：请输入有效的整数。")

    # 3. 校验元素是否存在于已知元素列表中
    unknown_elements = [el for el in element_cols if el not in elements]
    if unknown_elements:
        print("\n" + "=" * 50)
        print("!! 警告：CSV文件中的以下列名不在预设的元素列表中 !!")
        for el in unknown_elements:
            print(f"  - {el}")
        print("请在脚本顶部的 ATOMIC_MASSES 字典中添加这些元素的数据后重试。")
        print("=" * 50)
        return

    print(f"\n将对以下成分列进行计算: {', '.join(element_cols)}")

    # 4. 定义行计算函数并应用
    def calculate_row(row):
        input_percents = row[element_cols].to_dict()
        result_percents = conversion_func(input_percents)
        return pd.Series(result_percents)

    result_df = df.apply(calculate_row, axis=1)

    # 5. 重命名结果列并合并
    result_df = result_df.rename(
        columns={el: f"{el}({to_unit}%)" for el in result_df.columns}
    )
    final_df = pd.concat([df, result_df], axis=1)

    # 6. 保存到新文件
    base_name, ext = os.path.splitext(csv_path)
    output_path = f"{base_name}-{to_unit}.csv"

    final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print("\n--- 计算完成 ---")
    print(f"结果已保存到新文件: {output_path}")
    print("新文件预览:")
    print(final_df.head())


# --- 主程序入口 ---
def main():
    print("=" * 50)
    print("        质量百分比 (wt%) 与 原子百分比 (at%) 转换工具")
    print("=" * 50)
    print("支持的元素:", ", ".join(ATOMIC_MASSES.keys()))

    # 选择转换方向
    while True:
        print("\n请选择转换方向:")
        print("  1. 质量百分比 (wt%) -> 原子百分比 (at%)")
        print("  2. 原子百分比 (at%) -> 质量百分比 (wt%)")
        choice = input("请输入选项 (1或2): ")
        if choice == "1":
            conversion_func = wt_to_at
            from_unit, to_unit = "wt", "at"
            break
        elif choice == "2":
            conversion_func = at_to_wt
            from_unit, to_unit = "at", "wt"
            break
        else:
            print("无效输入，请输入 1 或 2。")

    # 选择计算模式
    while True:
        print("\n请选择计算模式:")
        print("  1. 单点计算 (手动输入单个合金成分)")
        print("  2. 批量计算 (从CSV文件读取)")
        mode = input("请输入选项 (1或2): ")
        if mode in ["1", "2"]:
            break
        else:
            print("无效输入，请输入 1 或 2。")

    # 执行相应的功能
    element_list = list(ATOMIC_MASSES.keys())
    if mode == "1":
        handle_single_point_calculation(
            element_list, conversion_func, from_unit, to_unit
        )
    elif mode == "2":
        handle_batch_calculation(element_list, conversion_func, from_unit, to_unit)


if __name__ == "__main__":
    main()
