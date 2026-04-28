"""
MNE Sample Dataset 新手预处理教程
==================================
基于 mne.datasets.sample 数据集，演示 EEG/MEG 数据从原始信号到 ERP 的完整预处理流程。

预处理步骤:
  1. 环境配置与数据加载
  2. 数据初步检查
  3. 选择感兴趣的通道
  4. 滤波
  5. 标记坏导
  6. 重参考（仅 EEG）
  7. ICA 伪迹去除
  8. 分段（Epoching）
  9. Epoch 质量控制与剔除
  10. 平均与结果可视化
"""

# %%
# =============================================================================
# Step 1: 环境配置与数据加载
# =============================================================================
import mne
from mne.preprocessing import ICA
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")  # 确保交互式后端，如不需要可注释掉
import matplotlib.pyplot as plt

# 设置 MNE 数据目录为本地路径（避免重复下载）
mne.set_config("MNE_DATA", "./datasets")

# 加载 Sample 数据集
sample_data_path = mne.datasets.sample.data_path()
raw_fname = sample_data_path / "MEG" / "sample" / "sample_audvis_raw.fif"

# preload=True 将数据全部读入内存，方便后续就地修改
raw = mne.io.read_raw_fif(raw_fname, preload=True)

# 查看基本信息：通道数、采样率、时长、通道类型等
print(raw.info)
print(f"采样率: {raw.info['sfreq']} Hz")
print(f"通道数: {raw.info['nchan']}")
print(f"数据时长: {raw.times[-1]:.1f} 秒")
print(f"初始坏导列表: {raw.info['bads']}")

# %%
# =============================================================================
# Step 2: 数据初步检查
# =============================================================================
# 可视化原始数据（交互式窗口，可滚动浏览）
raw.plot(duration=10, n_channels=20, title="Raw data browsing")

# 查看功率谱密度（PSD），帮助识别工频干扰（50/60Hz）和其他噪声
raw.compute_psd(fmax=80).plot(picks="data", exclude="bads")
plt.suptitle("PSD before filtering")
plt.show()

# 查看传感器布局（MEG 和 EEG 的空间分布）
raw.plot_sensors(show_names=True)

# %%
# =============================================================================
# Step 3: 选择感兴趣的通道
# =============================================================================
# 保留 MEG（磁力计 mag + 梯度计 grad）、EEG、EOG 通道
# 丢弃 stim（刺激触发通道）和其他无关通道
# 注意：保留 EOG 是因为后续 ICA 需要它来自动识别眼动伪迹
raw.pick_types(meg=True, eeg=True, eog=True, stim=False)
print(f"选择后通道数: {raw.info['nchan']}")

# %%
# =============================================================================
# Step 4: 滤波
# =============================================================================
# 保存滤波前 PSD 用于对比
psd_before = raw.compute_psd(fmax=80)

# 带通滤波 1-40 Hz:
#   - 高通 1 Hz: 去除低频漂移（慢电位漂移、呼吸伪迹等）
#   - 低通 40 Hz: 去除高频肌电噪声，保留 ERP 相关频段
raw.filter(l_freq=1.0, h_freq=40.0)

# 陷波滤波（可选）：去除工频干扰
# Sample 数据采集于美国，电网频率为 60 Hz
# 由于上面已经低通 40 Hz，60 Hz 已被滤除，此步通常可跳过
# 如果低通截止频率 > 60 Hz，则需要取消下行注释：
# raw.notch_filter(freqs=60.0)

# 滤波前后 PSD 对比
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
psd_before.plot(picks="eeg", exclude="bads", axes=axes[0], show=False)
axes[0].set_title("滤波前 (EEG)")
raw.compute_psd(fmax=80).plot(picks="eeg", exclude="bads", axes=axes[1], show=False)
axes[1].set_title("滤波后 1-40 Hz (EEG)")
plt.tight_layout()
plt.show()

# %%
# =============================================================================
# Step 5: 标记坏导
# =============================================================================
# 坏导 = 信号质量差的通道（断线、持续噪声等）
# 坏导不会参与后续分析（ICA、平均等），避免污染结果
# Sample 数据集中已知的坏导：
raw.info["bads"] = ["MEG 2443", "EEG 053"]
print(f"标记的坏导: {raw.info['bads']}")

# 可视化坏导（坏导会以灰色显示）
raw.plot(duration=10, n_channels=20, title="坏导标记后（灰色为坏导）")

# %%
# =============================================================================
# Step 6: 重参考（仅 EEG）
# =============================================================================
# EEG 信号是相对于参考电极的电位差，参考的选择会影响信号形态
# 常见参考方案：
#   - 平均参考（average）: 以所有 EEG 通道均值为参考，最常用
#   - 单电极参考: 如 Cz、鼻尖、耳垂等
# 这里使用平均参考
# projection=True 表示先添加为投影，在后续运算中自动应用
raw.set_eeg_reference("average", projection=True)
print("已设置 EEG 平均参考（投影方式）")

# %%
# =============================================================================
# Step 7: ICA 伪迹去除
# =============================================================================
# ICA（独立成分分析）将混合信号分解为统计独立的成分
# 眼动、心跳等伪迹通常集中在少数成分中，识别并去除即可

# 创建 ICA 对象
# n_components=20: 提取 20 个独立成分（通常 15-25 个足够）
# method='fastica': 快速 ICA 算法，适合新手
# random_state=42: 固定随机种子，保证结果可复现
ica = ICA(n_components=20, method="fastica", random_state=42)

# 拟合 ICA（在滤波后的连续数据上）
ica.fit(raw)
print(f"ICA 拟合完成，共 {ica.n_components_} 个成分")

# 查看所有 ICA 成分的地形图（脑电空间分布）
# 眼动成分通常集中在前额区域，心跳成分呈现特征性分布
ica.plot_components(picks=range(20), inst=raw)

# --- 自动识别眼动伪迹 (EOG) ---
# find_bads_eog 通过 EOG 通道与 ICA 成分的相关性来识别眼动成分
eog_indices, eog_scores = ica.find_bads_eog(raw)
print(f"自动识别的 EOG 伪迹成分: {eog_indices}")
ica.plot_scores(eog_scores, title="EOG 相关性得分")

# --- 自动识别心电伪迹 (ECG) ---
# Sample 数据没有 ECG 通道，MNE 会自动用 MEG 信号构造虚拟 ECG
ecg_indices, ecg_scores = ica.find_bads_ecg(raw)
print(f"自动识别的 ECG 伪迹成分: {ecg_indices}")
ica.plot_scores(ecg_scores, title="ECG 相关性得分")

# 汇总要排除的成分
ica.exclude = list(set(eog_indices + ecg_indices))
print(f"将要排除的 ICA 成分: {ica.exclude}")

# 查看要排除成分的时域波形（确认是否合理）
ica.plot_sources(raw, picks=ica.exclude)

# 应用 ICA，从原始数据中去除伪迹成分
# 注意：这会就地修改 raw 对象
ica.apply(raw)
print("ICA 伪迹去除完成")

# %%
# =============================================================================
# Step 8: 分段（Epoching）
# =============================================================================
# 从 stim 通道提取事件标记
# 注意：虽然之前 pick_types 时丢弃了 stim 通道，
# 但事件信息仍可从 raw 的 annotations 或重新加载中获取
# 这里我们重新读取事件（从原始文件的 stim 通道）
raw_for_events = mne.io.read_raw_fif(raw_fname, preload=False)
events = mne.find_events(raw_for_events, stim_channel="STI 014")

# 定义感兴趣的事件类型
# Sample 数据集包含听觉和视觉刺激，分左右耳/视野呈现
event_id = {
    "auditory/left": 1,   # 左耳听觉刺激
    "auditory/right": 2,  # 右耳听觉刺激
    "visual/left": 3,     # 左视野视觉刺激
    "visual/right": 4,    # 右视野视觉刺激
}

# 查看事件分布
mne.viz.plot_events(events, sfreq=raw.info["sfreq"], event_id=event_id)

# 创建 Epochs（分段）
# tmin=-0.2: 刺激前 200ms（用作基线）
# tmax=0.5: 刺激后 500ms（ERP 主要成分出现区间）
# baseline=(None, 0): 基线校正，用 tmin 到 0 的均值做基线
#   基线校正原理：将每个 epoch 的信号减去基线期均值，
#   消除不同 trial 间的直流偏移差异
epochs = mne.Epochs(
    raw,
    events,
    event_id,
    tmin=-0.2,
    tmax=0.5,
    baseline=(None, 0),
    preload=True,
)
print(f"创建的 Epochs 数量: {len(epochs)}")
print(f"各条件 Epoch 数:")
for cond in event_id:
    print(f"  {cond}: {len(epochs[cond])}")

# %%
# =============================================================================
# Step 9: Epoch 质量控制与剔除
# =============================================================================
# 基于峰峰值振幅阈值自动剔除异常 epoch
# 如果某个 epoch 中任意通道的振幅超过阈值，则整个 epoch 被丢弃
reject = dict(
    mag=4000e-13,    # 磁力计: 4000 fT
    grad=4000e-13,   # 梯度计: 4000 fT/cm
    eeg=150e-6,      # EEG: 150 μV
    eog=250e-6,      # EOG: 250 μV
)
epochs.drop_bad(reject=reject)
print(f"剔除后剩余 Epochs: {len(epochs)}")

# 查看剔除统计：哪些通道导致了最多的 epoch 被丢弃
epochs.plot_drop_log()

# 浏览各个 epoch（可手动标记需要额外剔除的 epoch）
epochs.plot(n_epochs=5, title="Epoch 浏览")

# %%
# =============================================================================
# Step 10: 平均与结果可视化
# =============================================================================
# 对各条件分别求平均，得到 ERP/ERF（事件相关电位/磁场）
evoked_aud_l = epochs["auditory/left"].average()
evoked_aud_r = epochs["auditory/right"].average()
evoked_vis_l = epochs["visual/left"].average()
evoked_vis_r = epochs["visual/right"].average()

# --- 波形图 ---
# 显示所有通道的时间波形
evoked_aud_l.plot(titles="听觉左 - ERP/ERF 波形")

# --- 地形图 ---
# 在多个时间点显示头皮电位/磁场分布
# 可以看到 N100、P200 等成分的空间分布
evoked_aud_l.plot_topomap(
    times=[0.05, 0.1, 0.15, 0.2],
    title="听觉左 - 地形图"
)

# --- 联合图（波形 + 地形图）---
# 最直观的展示方式：上方是波形，标记处显示对应时刻的地形图
evoked_aud_l.plot_joint(title="听觉左 - 联合图")
evoked_vis_l.plot_joint(title="视觉左 - 联合图")

# --- 条件对比 ---
# 比较不同实验条件的 ERP 差异
evokeds_compare = {
    "auditory/left": evoked_aud_l,
    "auditory/right": evoked_aud_r,
    "visual/left": evoked_vis_l,
    "visual/right": evoked_vis_r,
}
mne.viz.plot_compare_evokeds(
    evokeds_compare,
    picks="eeg",
    title="四种条件 ERP 对比 (EEG)",
)

# --- 听觉 vs 视觉 对比 ---
mne.viz.plot_compare_evokeds(
    {"auditory": evoked_aud_l, "visual": evoked_vis_l},
    picks="eeg",
    title="听觉 vs 视觉 ERP 对比 (EEG)",
)

print("\n预处理教程完成!")
print("关键成果:")
print(f"  - 原始数据: {raw_fname}")
print(f"  - 最终 Epochs 数量: {len(epochs)}")
print(f"  - ICA 排除成分: {ica.exclude}")
print(f"  - 生成 4 个条件的 ERP/ERF")
