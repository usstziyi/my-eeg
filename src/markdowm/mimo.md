# MNE-Python Sample 数据集标准处理流程

`mne.datasets.sample` 是 MNE-Python 自带的示例数据集（MEG/EEG 数据），以下是典型的标准处理流程：

---

## 1. 加载数据

```python
import mne
from mne.datasets import sample

# 获取数据路径
data_path = sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'

# 读取 Raw 对象
raw = mne.io.read_raw_fif(raw_fname, preload=True)
```

---

## 2. 数据检查与预览

```python
# 查看基本信息
raw.info
raw.plot()              # 可视化原始信号
raw.plot_psd()          # 功率谱密度
```

---

## 3. 设置电极参考（Re-referencing）

```python
raw.set_eeg_reference('average', projection=True)
```

---

## 4. 滤波（Filtering）

```python
raw.filter(l_freq=1.0, h_freq=40.0)  # 带通滤波
# raw.notch_filter(freqs=60)          # 陷波滤除工频干扰（如需要）
```

---

## 5. ICA 去伪迹（Artifact Removal）

```python
from mne.preprocessing import ICA

ica = ICA(n_components=20, random_state=97, max_iter=800)
ica.fit(raw)

# 自动检测眼电/心电伪迹
eog_indices, eog_scores = ica.find_bads_eog(raw)
ecg_indices, ecg_scores = ica.find_bads_ecg(raw)

ica.exclude = eog_indices + ecg_indices
ica.apply(raw)  # 将 ICA 应用到原始数据
```

---

## 6. 提取事件（Events）

```python
events = mne.find_events(raw, stim_channel='STI 014')
print(f"共发现 {len(events)} 个事件")

# 定义事件 ID
event_id = {
    'auditory/left':  1,
    'auditory/right': 2,
    'visual/left':    3,
    'visual/right':   4,
}
```

---

## 7. 创建 Epochs（分段）

```python
tmin, tmax = -0.2, 0.5  # 锁时窗口：事件前200ms ~ 后500ms
baseline = (None, 0)     # 基线校正：-200ms ~ 0ms

epochs = mne.Epochs(
    raw, events, event_id,
    tmin=tmin, tmax=tmax,
    baseline=baseline,
    preload=True,
    reject=dict(eeg=150e-6, mag=4e-12, grad=4000e-13)  # 幅值阈值拒绝
)

epochs.drop_bad()  # 自动剔除超阈值的 epoch
print(f"剩余 {len(epochs)} 个 epoch")
```

---

## 8. Epochs 质量检查

```python
epochs.plot()                    # 逐 trial 可视化
epochs.plot_drop_log()           # 查看被剔除的 trial
epochs.plot_image()              # epoch 图像
```

---

## 9. 计算 ERP（Evoked Response）

```python
evoked_auditory_left = epochs['auditory/left'].average()
evoked_auditory_right = epochs['auditory/right'].average()
evoked_visual_left = epochs['visual/left'].average()
evoked_visual_right = epochs['visual/right'].average()

# 可视化
evoked_auditory_left.plot()
evoked_auditory_left.plot_topomap(times=[0.1, 0.2, 0.3])
evoked_auditory_left.plot_joint()  # 联合图
```

---

## 10. 时频分析（Time-Frequency Analysis）

```python
from mne.time_frequency import tfr_morlet

freqs = np.arange(6, 30, 1)
n_cycles = freqs / 2.0

power = tfr_morlet(
    epochs['auditory/left'],
    freqs=freqs, n_cycles=n_cycles,
    return_itc=False, average=True
)
power.plot(baseline=(-0.2, 0), mode='logratio')
```

---

## 11. 源定位（Source Localization，可选）

```python
# 设置 BEM 模型和源空间
bem = mne.read_bem_solution(data_path + '/bem/sample-5120-5120-5120-bem-sol.fif')
src = mne.setup_source_space('sample', spacing='oct6', subjects_dir=data_path + '/subjects')

# 计算正演模型
fwd = mne.make_forward_solution(raw_fname, trans, src, bem)

# 计算逆解
noise_cov = mne.compute_covariance(epochs, tmax=0)
inverse_operator = mne.minimum_norm.make_inverse_operator(raw.info, fwd, noise_cov)
stc = mne.minimum_norm.apply_inverse(evoked_auditory_left, inverse_operator, lambda2=1./9.)
stc.plot()
```

---

## 12. 统计分析

```python
from mne.stats import permutation_cluster_test

# 条件间对比
X = [epochs['auditory/left'].get_data(), epochs['auditory/right'].get_data()]
T_obs, clusters, cluster_p_values, H0 = permutation_cluster_test(
    X, n_permutations=1000, tail=0
)
```

---

## 流程总结图

```
Raw 数据
  │
  ▼
信息检查 & 可视化
  │
  ▼
参考设置 → 滤波 → ICA 去伪迹
  │
  ▼
提取事件（Events）
  │
  ▼
分段（Epochs）→ 基线校正 → 幅值拒绝
  │
  ├──→ ERP 分析（Evoked）
  ├──→ 时频分析（TFR）
  ├──→ 源定位（Source Localization）
  └──→ 统计检验（Statistics）
```

以上是 MNE sample 数据集从原始数据到分析结果的**标准处理流水线**，具体步骤可根据研究目的进行增减。