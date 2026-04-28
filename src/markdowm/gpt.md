`mne.datasets.sample` 的“正常处理流程”，按 MNE 官方 sample 教程的标准主线，可以理解为一条 **从原始连续数据到诱发响应，再到源空间估计** 的流程。官方总览明确把这条主线概括为：**loading data → epoching → averaging → plotting → estimating cortical activity from sensor data**。([Mne Tools][1])

你可以按下面顺序理解：

1. **下载并定位 sample 数据集**
   先用 `mne.datasets.sample.data_path()` 获取数据目录。sample 数据集主要包含两部分：

   * `MEG/sample`：MEG/EEG 原始数据
   * `subjects/sample`：MRI 重建结果、BEM 等解剖建模文件
     官方也说明，这个数据集里的 **MRI 表面重建** 和 **BEM 表面** 已经预先做好了。([Mne Tools][2])

2. **读取原始数据 Raw**
   通常读取类似 `sample_audvis_raw.fif` 这样的文件，得到 `Raw` 对象，作为后续所有预处理的起点。官方把 `Raw`、`Epochs`、`Evoked`、`SourceEstimate` 作为这条分析链的核心数据结构。([Mne Tools][1])

3. **原始数据预处理**
   常见包括：

   * 选通道 / 设定 bad channels
   * 滤波（高通、低通、陷波）
   * SSP / ICA / 注释坏时间段
   * 参考设置（EEG 时常见）
     这些属于 MNE 的标准 preprocessing 范畴，通常发生在 epoch 之前。([Mne Tools][3])

4. **提取事件 events**
   从刺激通道或 annotations 中取出事件时间点，得到 `events` 和 `event_id`。这是从连续数据切成试次的前提。官方的 sample/intro 流程就是先有 Raw，再围绕 events 做后续分析。([Mne Tools][1])

5. **切分成 Epochs**
   用 `mne.Epochs(...)` 按事件把连续数据切成很多小段试次，一般会设置：

   * `tmin`, `tmax`
   * `baseline`
   * `reject` / `flat` 阈值
   * `picks`
     `Epochs` 官方文档也明确这是处理离散试次数据的标准对象。([Mne Tools][4])

6. **试次剔除与质量控制**
   在 `Epochs` 阶段做伪迹拒绝最常见，例如依据峰峰值阈值丢弃坏试次。MNE 官方对 `reject` 参数的说明就是：若某个通道在某个 epoch 中超阈值，则该 epoch 被丢弃。([Mne Tools][5])

7. **按条件平均得到 Evoked**
   例如把同一刺激条件下的 epochs 平均，得到 `Evoked`。这一步是 ERP/ERF 分析的核心。官方把 `Evoked` 定义为平均后的诱发数据对象。([Mne Tools][6])

8. **传感器层可视化与分析**
   对 `Evoked` 做：

   * 时序波形图
   * topomap
   * joint plot
   * 比较不同条件
     这是 sample 教程里非常标准的一步，用来先在传感器层确认效应。([Mne Tools][7])

9. **噪声协方差建模**
   为后续逆解准备 noise covariance。sample 数据集中也提供了相关模板/文件用于这类计算。([Mne Tools][2])

10. **前向模型（forward solution）**
    基于 sample 自带的 MRI、表面重建和 BEM，建立头模型与源空间，再把脑源投影到传感器空间。因为 sample 已经提供了解剖重建和 BEM，所以这一步通常是在现成结构上继续做。([Mne Tools][2])

11. **逆解 / 源定位**
    在有了 `Evoked + noise covariance + forward` 之后，计算 inverse operator，再得到源空间结果 `SourceEstimate`，例如 MNE/dSPM/sLORETA。官方 overview 直接把这一步描述为从传感器数据估计 cortical activity。([Mne Tools][1])

12. **源空间可视化与进一步分析**
    最后查看皮层激活分布、峰值时刻、ROI 时程，必要时做 group-level 或 morph 到其他被试空间。sample 数据集还包含 `morph` 相关资源，用来演示 morphing。([Mne Tools][2])

如果你想把它压缩成一句“流水线”，就是：

**sample.data_path → read raw → preprocess raw → find events → make epochs → reject bad epochs → average to evoked → sensor-level plots → compute covariance → forward model → inverse solution → source estimate visualization**。([Mne Tools][1])

补一句很关键的点：
`mne.datasets.sample` 不是“纯原始什么都没做”的数据；官方明确说其中 **MRI 重建和 BEM 已经预先完成**，所以它特别适合教学和演示完整的 MNE 分析链，而不是从 MRI 分割开始全流程重建。([Mne Tools][2])

你要的话，我可以下一条直接给你一份 **对应这 12 步的最小可运行 MNE 代码模板**。

[1]: https://mne.tools/stable/auto_tutorials/intro/10_overview.html?utm_source=chatgpt.com "Overview of MEG/EEG analysis with MNE-Python"
[2]: https://mne.tools/stable/documentation/datasets.html?utm_source=chatgpt.com "Datasets Overview — MNE 1.12.0 documentation"
[3]: https://mne.tools/stable/auto_tutorials/preprocessing/index.html?utm_source=chatgpt.com "Preprocessing — MNE 1.12.0 documentation"
[4]: https://mne.tools/stable/auto_tutorials/epochs/10_epochs_overview.html?utm_source=chatgpt.com "The Epochs data structure: discontinuous data - MNE-Python"
[5]: https://mne.tools/stable/generated/mne.Epochs.html?utm_source=chatgpt.com "mne.Epochs — MNE 1.12.0 documentation - MNE-Python"
[6]: https://mne.tools/stable/auto_tutorials/evoked/10_evoked_overview.html?utm_source=chatgpt.com "The Evoked data structure: evoked/averaged data - MNE-Python"
[7]: https://mne.tools/stable/generated/mne.Evoked.html?utm_source=chatgpt.com "mne.Evoked — MNE 1.12.0 documentation - MNE-Python"
