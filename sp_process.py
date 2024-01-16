import skrf as rf
import numpy as np

def custom_sort(s, prefix_order_dict, suffix_order_dict):
    #检查字符串前缀和后缀是否在排序顺序中，并返回按照规则排序后的序列
    prefix = next((key for key in prefix_order_dict if s.startswith(key)), None)
    suffix = next((key for key in suffix_order_dict if s.endswith(key)), None)

    if prefix is not None and suffix is not None:
        return (prefix_order_dict[prefix], suffix_order_dict[suffix])
    else:
        return False

def rearrange_port_to_diff(N):
    lst = list(range(4 * N))
    new_lst = [None] * (4 * N)

    for i in range(N):
        new_lst[4 * i] = lst[2 * i]
        new_lst[4 * i + 1] = lst[2 * i + 1]
        new_lst[4 * i + 2] = lst[2 * i + 2 * N]
        new_lst[4 * i + 3] = lst[2 * i + 2 * N + 1]

    return new_lst

def process_network_data(file_path,lane):
    Data = rf.Network(file_path)
    Data.renormalize(45)
    port_name = Data.port_names
    port_num = np.size(port_name)

    prefix_order = ['DIE', 'BGA']
    suffix_order = []
    for trx in ['TX', 'RX']:
        for i in range(lane):
            for j in ['P', 'N']:
                suffix_order.append(trx + j + str(i + 1))

    prefix_order_dict = {key: i for i, key in enumerate(prefix_order)}
    suffix_order_dict = {key: i for i, key in enumerate(suffix_order)}

    port_indexed_lst = list(enumerate(port_name))
    sorted_indexed_port = sorted(port_indexed_lst, key=lambda x: custom_sort(x[1], prefix_order_dict, suffix_order_dict))

    #提取排序后的列表和原始索引，用于s参数的reorder
    sorted_port = [item[1] for item in sorted_indexed_port]
    orgin_indices = [item[0] for item in sorted_indexed_port]
    new_indices = rearrange_port_to_diff(int(port_num / 4))
    Data.renumber([i for i in range(port_num)], orgin_indices)
    Data.renumber([i for i in range(port_num)], new_indices)
    Data.se2gmm(int(port_num / 2))

    rf.write('./example/Host_diff_ntwk', Data)

# Call the function to process the network data
process_network_data("./example/Sweep1_DV757.s64p",8)