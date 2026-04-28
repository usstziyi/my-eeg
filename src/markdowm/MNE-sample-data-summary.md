# MNE-sample-data 数据集总览

这是 **MNE-Python** 的官方示例数据集，包含一个被试（sample）的**听觉-视觉刺激实验**（audvis）的完整 MEG/EEG 数据及 FreeSurfer 脑结构重建结果。共 **624 个文件**，分为三大部分：

---

## 1. `MEG/sample/` — MEG/EEG 采集与分析数据（76 个文件）

| 类别 | 文件 | 说明 |
|------|------|------|
| **原始数据** | `sample_audvis_raw.fif` (123MB) | 主实验原始 MEG/EEG 数据 |
| | `sample_audvis_filt-0-40_raw.fif` (63MB) | 0-40Hz 带通滤波后的原始数据 |
| | `ernoise_raw.fif` (40MB) | 空房间噪声记录（用于噪声协方差估计） |
| **事件文件** | `*_raw-eve.fif` | 标记刺激事件的时间点（听觉左/右、视觉左/右） |
| | `*_ecg-eve.fif` / `*_eog-eve.fif` | 心电/眼电伪迹事件 |
| **平均诱发** | `sample_audvis-ave.fif` (5.3MB) | 条件平均后的诱发响应（ERP/ERF） |
| **协方差** | `sample_audvis-cov.fif` / `-shrunk-cov.fif` | 噪声协方差矩阵（用于源定位） |
| **正向模型** | `*-fwd.fif` (20-179MB) | 正向解（MEG/EEG/联合，表面/体积源空间） |
| **逆算子** | `*-inv.fif` (26-344MB) | 逆算子（不同深度加权、固定/自由方向） |
| **源估计** | `*.stc` | 源时间课程（source time course），分左右半球 |
| **敏感度图** | `*-sensmap-*.w` | 前向模型的传感器敏感度映射 |
| **伪迹投影** | `*_ecg-proj.fif` / `*_eog-proj.fif` | SSP 投影向量（去除心电/眼电伪迹） |
| **坐标变换** | `*-trans.fif` | 头部到 MRI 的坐标变换矩阵 |
| **标签** | `labels/Aud-*.label` / `Vis-*.label` | 听觉/视觉皮层 ROI 标签 |
| **其他** | `*.bad` / `*.log` / `*.dip` / `*.ave` / `*.cov` | 坏导记录、处理日志、偶极拟合、旧格式文件 |

---

## 2. `SSS/` — 信号空间分离校准数据（2 个文件）

| 文件 | 说明 |
|------|------|
| `ct_sparse_mgh.fif` | 串扰（crosstalk）校正矩阵 |
| `sss_cal_mgh.dat` | 精细校准（fine calibration）数据 |

用于 Maxwell 滤波（tSSS/SSS）的设备校准。

---

## 3. `subjects/` — FreeSurfer 脑结构重建数据（545 个文件）

包含三个被试目录：

### 3.1 `subjects/sample/` — 实际被试的脑结构

| 子目录 | 说明 |
|--------|------|
| **`mri/`** | T1 MRI 体积（`T1.mgz`）、脑分割（`aseg.mgz`、`aparc+aseg.mgz`）、脑掩模、配准变换等 |
| **`surf/`** | 皮层表面网格：白质面（`white`）、软脑膜面（`pial`）、膨胀面（`inflated`）、球面（`sphere`）、曲率/厚度/面积等形态学指标 |
| **`label/`** | 皮层分区标签：Brodmann 区（BA1-BA45）、Desikan-Killiany 分区（`aparc`）、Destrieux 分区（`a2009s`）、V1/V2/MT 等功能区 |
| **`bem/`** | 边界元模型：内颅/外颅/外皮表面、BEM 解、源空间定义（表面 oct-6 / 体积 7mm） |
| **`stats/`** | FreeSurfer 统计输出 |

### 3.2 `subjects/fsaverage/` — FreeSurfer 标准模板脑

包含与 sample 类似的 `surf/`、`label/`、`mri/`、`bem/` 等，用作**群组分析的标准空间**和**个体到模板的配准目标**。

### 3.3 `subjects/fsaverage_sym/` — 左右对称模板脑

用于**跨半球对比分析**的对称化模板。

### 3.4 `subjects/morph-maps/` — 变形映射

`sample-fsaverage-morph.fif` 等 6 个文件，用于在不同被试的皮层表面之间进行**空间变形**（morphing）。

---

## 总结

这个数据集是一个完整的 **MEG/EEG 源成像分析 pipeline** 的全套示例数据，涵盖了从原始采集 → 预处理 → 平均 → 正向建模 → 逆问题求解 → 源估计的所有环节，配合 FreeSurfer 的解剖重建结果，可以用来学习和演示 MNE-Python 的几乎所有功能。
