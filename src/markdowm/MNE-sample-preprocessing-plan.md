# MNE Sample Dataset 新手预处理教程 — 实现计划

## Context

用户希望为 `mne.datasets.sample` 数据集编写一份面向新手的预处理教程脚本。项目中已有 `mne_load_datasets_demo.py` 演示了数据加载，但缺少完整的预处理流程。Sample 数据集包含 MEG + EEG 混合数据（`sample_audvis_raw.fif`），本计划将编写一个循序渐进、注释详尽的预处理脚本。

## 目标文件

- **新建**: `D:\AI\claude-code\mne_sample_preprocessing.py` — 完整的预处理教程脚本

## 预处理步骤（共 10 步）

### Step 1: 环境配置与数据加载
- 导入 mne, numpy, matplotlib
- 设置 `MNE_DATA` 指向本地 `./datasets`
- 使用 `mne.datasets.sample.data_path()` 获取路径
- `mne.io.read_raw_fif()` 加载 `sample_audvis_raw.fif`
- 打印 `raw.info` 查看通道数、采样率、通道类型等基本信息

### Step 2: 数据初步检查
- `raw.plot()` 可视化原始数据（交互浏览）
- `raw.compute_psd().plot()` 查看功率谱密度（识别工频干扰等）
- `raw.plot_sensors()` 查看传感器布局

### Step 3: 选择感兴趣的通道
- 使用 `raw.pick_types(meg=True, eeg=True, eog=True, stim=False)` 选择通道
- 或 `raw.pick(['EEG 001', ...])` 精确选择
- 说明为何保留 EOG（后续 ICA 需要）

### Step 4: 滤波
- **带通滤波**: `raw.filter(l_freq=1.0, h_freq=40.0)` — 去除低频漂移和高频噪声
- **陷波滤波**（可选）: `raw.notch_filter(freqs=60.0)` — 去除工频干扰（美国 60Hz）
- 滤波前后 PSD 对比可视化，直观展示效果

### Step 5: 标记坏导
- `raw.info['bads']` 手动添加已知坏导（如 `['MEG 2443', 'EEG 053']`）
- `raw.plot()` 中可视化并标记
- 说明坏导对后续分析的影响

### Step 6: 重参考（仅 EEG）
- `raw.set_eeg_reference('average')` — 平均参考
- 说明常见参考方案（平均参考 vs 特定电极参考）及其适用场景

### Step 7: ICA 伪迹去除
- `mne.preprocessing.ICA(n_components=20, method='fastica')` 创建 ICA 对象
- `ica.fit(raw)` 拟合
- `ica.plot_components()` 查看成分地形图
- 自动识别眼动伪迹: `ica.find_bads_eog(raw)` 
- 自动识别心电伪迹: `ica.find_bads_ecg(raw)`（sample 数据无 ECG，使用 MEG 替代）
- `ica.plot_sources(raw)` 查看时域波形
- `ica.apply(raw)` 去除伪迹成分

### Step 8: 分段（Epoching）
- `mne.find_events(raw, stim_channel='STI 014')` 提取事件
- 定义事件字典: `event_id = {'auditory/left': 1, 'auditory/right': 2, 'visual/left': 3, 'visual/right': 4}`
- `mne.Epochs(raw, events, event_id, tmin=-0.2, tmax=0.5, baseline=(None, 0), preload=True)` 创建 epochs
- 说明 baseline correction 的原理

### Step 9: Epoch 质量控制与剔除
- `epochs.drop_bad(reject=dict(mag=4000e-13, grad=4000e-13, eeg=150e-6))` — 基于振幅阈值自动剔除
- `epochs.plot_drop_log()` 查看剔除统计
- `epochs.plot()` 浏览各个 epoch

### Step 10: 平均与结果可视化
- `evoked_aud = epochs['auditory/left'].average()` 计算 ERP/ERF
- `evoked_vis = epochs['visual/left'].average()` 
- `evoked_aud.plot()` — 波形图
- `evoked_aud.plot_topomap()` — 地形图（多时间点）
- `evoked_aud.plot_joint()` — 联合图（波形 + 地形图）
- `mne.viz.plot_compare_evokeds({'auditory': evoked_aud, 'visual': evoked_vis})` — 条件对比

## 代码风格约定

- 注释使用中文（与现有 `mne_load_datasets_demo.py` 保持一致）
- 每个步骤用分隔线和标题注释清晰标记
- 关键参数附带简要说明
- 每步末尾包含可视化，方便新手直观理解

## 验证方法

1. 运行脚本确认无报错: `python mne_sample_preprocessing.py`
2. 检查各步骤可视化输出是否正常生成
3. 确认 ICA 能正确识别眼动成分
4. 确认 epochs 剔除比例合理（通常 < 20%）
5. 确认 ERP 波形符合预期（如听觉 N100、视觉 P100）
