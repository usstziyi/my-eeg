# MNE-Python 内置 EEG 数据集

所有数据集都通过 `mne.datasets` 获取，首次调用会自动下载。

## 1. Sample Dataset (`mne.datasets.sample`)

- **内容**: 60通道 EEG + MEG 同时记录
- **来源**: MGH/HMS/MIT Martinos Center
- **用途**: MNE 教程中最常用的示例数据

```python
data_path = mne.datasets.sample.data_path()
```

## 2. EEGBCI Dataset (`mne.datasets.eegbci`)

- **内容**: 运动想象 (Motor Imagery) EEG 数据
- **被试**: 109 人
- **来源**: PhysioNet
- **用途**: BCI 分类、运动想象分析

```python
mne.datasets.eegbci.load_data(subject=1, runs=[6, 10, 14])
```

## 3. ERP CORE Dataset (`mne.datasets.erp_core`)

- **内容**: 6 种 EEG 实验，诱发 7 种经典 ERP 成分
- **用途**: ERP 分析教学（LRP、ERN 等）

```python
data_path = mne.datasets.erp_core.data_path()
```

## 4. Sleep PhysioNet (`mne.datasets.sleep_physionet`)

- **内容**: 197 例整夜多导睡眠图记录（EEG + EOG + EMG）
- **用途**: 睡眠分期分类

```python
mne.datasets.sleep_physionet.age.fetch_data(subjects=[0], recording=[1])
```

## 5. Frequency-Tagged Visual Stimulation

- **内容**: 频率标记视觉刺激 EEG
- **被试**: 2 人
- **用途**: 频域分析（SSVEP 相关）

## 6. Brainstorm Tutorials (`mne.datasets.brainstorm`)

- **内容**: CTF 275 系统记录的数据
- **用途**: 源定位教程

## 7. ECoG Dataset

- **内容**: 皮层电图（颞叶电极阵列，听觉任务）
- **用途**: ECoG 数据处理示例

## 8. Lexical Decision EEG Dataset

- **内容**: 75 名被试的英语词汇判断任务 EEG 平均数据（960 个单词）
- **用途**: 语言认知 ERP 研究

## 快速上手示例

```python
import mne

# 下载 sample 数据集
data_path = mne.datasets.sample.data_path()
raw_fname = data_path / 'MEG' / 'sample' / 'sample_audvis_raw.fif'
raw = mne.io.read_raw_fif(raw_fname, preload=True)

# 下载 EEGBCI 运动想象数据
raw_fnames = mne.datasets.eegbci.load_data(subject=1, runs=[6, 10, 14])
raw = mne.io.concatenate_raws([mne.io.read_raw_edf(f) for f in raw_fnames])
```

## 推荐用途

| 用途 | 推荐数据集 |
|------|-----------|
| 入门学习 | Sample Dataset |
| BCI/运动想象 | EEGBCI |
| ERP 分析 | ERP CORE |
| 睡眠分期 | Sleep PhysioNet |
| 频域分析 | Frequency-Tagged |

## 参考链接

- [Datasets Overview — MNE Documentation](https://mne.tools/stable/documentation/datasets.html)
- [Overview of MEG/EEG analysis with MNE-Python](https://mne.tools/stable/auto_tutorials/intro/10_overview.html)
- [EEGBCI source code (mne-python GitHub)](https://github.com/mne-tools/mne-python/blob/main/mne/datasets/eegbci/eegbci.py)
