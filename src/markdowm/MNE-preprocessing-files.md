# MNE 预处理所需文件清单

## 核心文件（必需）

| 文件 | 用途 |
|------|------|
| `MEG/sample/sample_audvis_raw.fif` | 原始数据，所有预处理的起点 |
| `MEG/sample/sample_audvis_raw-eve.fif` | 事件标记，用于分段（epoching） |
| `MEG/sample/sample_bads.bad` | 坏导列表，标记需要剔除/插值的通道 |

## 伪迹去除相关

| 文件 | 用途 |
|------|------|
| `MEG/sample/sample_audvis_ecg-eve.fif` | 心电伪迹事件（用于定位心跳） |
| `MEG/sample/sample_audvis_eog-eve.fif` | 眼电伪迹事件（用于定位眨眼） |
| `MEG/sample/sample_audvis_ecg-proj.fif` | 心电 SSP 投影向量（去心电伪迹） |
| `MEG/sample/sample_audvis_eog-proj.fif` | 眼电 SSP 投影向量（去眼电伪迹） |

## Maxwell 滤波（tSSS/SSS）

| 文件 | 用途 |
|------|------|
| `SSS/ct_sparse_mgh.fif` | 串扰校正矩阵 |
| `SSS/sss_cal_mgh.dat` | 精细校准数据 |

## 噪声估计

| 文件 | 用途 |
|------|------|
| `MEG/sample/ernoise_raw.fif` | 空房间噪声记录，用于估计噪声协方差 |

## 典型预处理流程对应关系

```
1. 加载原始数据        → sample_audvis_raw.fif
2. 标记坏导            → sample_bads.bad
3. Maxwell 滤波        → ct_sparse_mgh.fif + sss_cal_mgh.dat
4. 带通/陷波滤波       → 直接对 raw 操作，不需要额外文件
5. 去除伪迹 (SSP/ICA) → ecg-eve/eog-eve + ecg-proj/eog-proj
6. 分段 (Epoching)     → sample_audvis_raw-eve.fif
7. 基线校正/剔除坏段   → 直接对 epochs 操作
```

总共大约 **10 个文件**，其中前 3 个是最基础的，其余按需使用。
