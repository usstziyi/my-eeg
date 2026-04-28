`mne.datasets.sample` 的正常处理流程遵循 MNE-Python 的通用分析范式，通常包含**数据加载、事件提取、数据分段（Epoching）、时域/频域分析、可视化及溯源分析**等核心步骤。为了方便你理解和上手，我整理了一个标准流程表：

### 🔄 标准处理流程

| 步骤 | 核心任务 | 关键操作与函数 | 产出/目的 |
| :--- | :--- | :--- | :--- |
| **1. 数据准备** | 下载/加载示例数据，创建 Raw 对象 | `mne.datasets.sample.data_path()`<br>`mne.io.read_raw_fif()` | 获取数据路径，将原始数据加载为 `Raw` 对象，供后续处理 。 |
| **2. 事件提取** | 从刺激通道识别事件标记 | `mne.find_events()`<br>`mne.read_events()` | 获取事件的时间点和事件ID，这是进行数据分段的基础 。 |
| **3. 数据分段** | 根据事件将连续数据切分为时段 | `mne.Epochs()` | 创建 `Epochs` 对象，将所有试验（trials）对齐到事件发生时刻，为后续叠加平均或机器学习准备 。 |
| **4. 时域分析** | 计算并可视化事件相关电位/场 | `epochs.average()`<br>`evoked.plot()` | 通过叠加平均得到 `Evoked` 对象，观察特定事件（如听觉/视觉刺激）诱发的脑活动时空模式。 |
| **5. 频域分析** | 分析数据的频谱特性 | `raw.plot_psd()`<br>`epochs.plot_psd()` | 绘制功率谱密度（PSD），用于观察不同频段（如 Alpha， Beta）的能量分布。 |
| **6. 可视化** | 绘制信号、地形图等 | `raw.plot()`<br>`epochs.plot_image()`<br>`evoked.plot_topomap()` | 通过交互式绘图或地形图直观检查数据质量、识别伪迹、观察效应。 |
| **7. 高级分析** | 进行源定位或统计分析 | `mne.minimum_norm.apply_inverse()`<br>各种统计函数 | 将传感器空间的活动映射到大脑皮层（源空间），或进行组水平统计分析。 |

### 📝 基础代码示例

下面是一个串联了核心步骤的代码示例，你可以直接运行它来体验整个流程：

```python
import mne

# 1. 数据准备: 自动下载并加载示例数据集
# 首次运行会自动下载约2GB的数据，请耐心等待
sample_data_folder = mne.datasets.sample.data_path()
sample_data_raw_file = sample_data_folder / 'MEG' / 'sample' / 'sample_audvis_raw.fif'
raw = mne.io.read_raw_fif(sample_data_raw_file, preload=True) # preload=True 将数据载入内存，加快后续处理

print(raw.info) # 查看数据基本信息

# 2. 事件提取: 从 'STI 014' 刺激通道读取事件标记
events = mne.find_events(raw, stim_channel='STI 014')

# 定义事件ID，将数字标记映射为有意义的实验条件名称
event_dict = {
    'auditory/left': 1,
    'auditory/right': 2,
    'visual/left': 3,
    'visual/right': 4,
    'face': 5,
    'button': 32
}

# 3. 数据分段(Epoching): 基于事件将数据切分成2秒长的时段
epochs = mne.Epochs(raw, events, event_id=event_dict, tmin=-0.2, tmax=0.5,
                    baseline=(None, 0), preload=True, reject=dict(grad=4000e-13)) # 定义基线并应用简单拒绝标准

# 4. 时域分析: 对 'auditory/left' 条件的时段进行叠加平均
evoked_aud_left = epochs['auditory/left'].average()
evoked_aud_left.plot() # 绘制所有通道的波形图

# 绘制特定时刻（如0.1秒）的脑地形图
evoked_aud_left.plot_topomap(times=[0.1], ch_type='grad')
```

### 💡 关键点提示
- **数据版本**：示例数据集包含多个文件。教程中常用经过滤波和下采样的 `sample_audvis_filt-0-40_raw.fif`，而完整文件是 `sample_audvis_raw.fif`。前者数据量更小，处理更快 。
- **数据加载**：`read_raw_fif` 中的 `preload` 参数值得留意。设为 `True` 会将所有数据读入内存，后续处理（如滤波、绘图）会更快；设为 `False` 则仅在需要时从硬盘读取，可以节省内存，适用于内存有限或数据量极大的情况。

你是主要想基于这个数据集做**事件相关电位（ERP）分析**，还是想用它来**训练一个分类模型**？告诉我你的具体目标，我可以帮你梳理更有针对性的流程细节。