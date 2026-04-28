"""
MNE-Python 加载 EEG 数据集 Demo
================================
演示如何使用 mne.datasets 加载和预览各种内置 EEG 数据集
"""
# %%
import mne
mne.set_config("MNE_DATA","./datasets")

# %% 1. 加载 Sample 数据集（MEG + EEG）
print("=" * 60)
print("1. Sample 数据集")
print("=" * 60)
# 下载并加载数据集
sample_data_path = mne.datasets.sample.data_path(download=True)
raw_fname = sample_data_path / "MEG" / "sample" / "sample_audvis_raw.fif"
raw_sample = mne.io.read_raw_fif(raw_fname, preload=True)

# # 查看数据集信息
# print(raw_sample.info)
# 只看 EEG 通道
raw_sample.pick("eeg").plot(duration=5, n_channels=10, title="Sample EEG")

# %% 2. 加载 EEGBCI 运动想象数据集
print("=" * 60)
print("2. EEGBCI 运动想象数据集")
print("=" * 60)

# subject=1, runs: 6=左拳想象, 10=右拳想象, 14=双脚想象
raw_fnames = mne.datasets.eegbci.load_data(subject=1, runs=[6, 10, 14])
raws = [mne.io.read_raw_edf(f, preload=True) for f in raw_fnames]
raw_eegbci = mne.concatenate_raws(raws)

# 设置标准 10-20 电极位置
mne.datasets.eegbci.standardize(raw_eegbci)
montage = mne.channels.make_standard_montage("standard_1005")
raw_eegbci.set_montage(montage)

print(raw_eegbci.info)
raw_eegbci.plot(duration=5, n_channels=10, title="EEGBCI Motor Imagery")

# %% 3. 加载 ERP CORE 数据集
print("=" * 60)
print("3. ERP CORE 数据集")
print("=" * 60)

erp_core_path = mne.datasets.erp_core.data_path()
raw_fname = erp_core_path / "ERP-CORE_Subject-001_Task-Flankers_eeg.fif"
raw_erp = mne.io.read_raw_fif(raw_fname, preload=True)

print(raw_erp.info)
raw_erp.plot(duration=5, n_channels=10, title="ERP CORE - Flankers")

# %% 4. 加载 Sleep PhysioNet 睡眠数据集
print("=" * 60)
print("4. Sleep PhysioNet 睡眠数据集")
print("=" * 60)

sleep_files = mne.datasets.sleep_physionet.age.fetch_data(subjects=[0], recording=[1])
raw_sleep = mne.io.read_raw_edf(sleep_files[0][0], preload=True)
annot = mne.read_annotations(sleep_files[0][1])
raw_sleep.set_annotations(annot)

print(raw_sleep.info)
print(f"标注类型: {set(raw_sleep.annotations.description)}")
raw_sleep.plot(duration=30, n_channels=4, title="Sleep PhysioNet")

# %% 5. 综合示例：EEGBCI 从加载到分类的完整流程
print("=" * 60)
print("5. EEGBCI 完整处理流程")
print("=" * 60)

# 加载数据
raw_fnames = mne.datasets.eegbci.load_data(subject=1, runs=[6, 10, 14])
raw = mne.concatenate_raws([mne.io.read_raw_edf(f, preload=True) for f in raw_fnames])
mne.datasets.eegbci.standardize(raw)
raw.set_montage(mne.channels.make_standard_montage("standard_1005"))

# 滤波 (8-30 Hz, mu + beta 节律)
raw.filter(8.0, 30.0, fir_design="firwin")

# 提取事件和 Epochs
events, event_id = mne.events_from_annotations(raw)
print(f"事件类型: {event_id}")

epochs = mne.Epochs(
    raw,
    events,
    event_id,
    tmin=-0.5,
    tmax=2.0,
    baseline=None,
    preload=True,
)

print(f"Epochs 数量: {len(epochs)}")
print(f"Epochs 形状: {epochs.get_data().shape}")  # (n_epochs, n_channels, n_times)

# 可视化
epochs.plot(n_epochs=3, title="EEGBCI Epochs")
epochs.average().plot(title="EEGBCI 平均 ERP")

# PSD 功率谱
epochs.compute_psd(fmin=8, fmax=30).plot(title="EEGBCI PSD")

print("\nDemo 完成!")
