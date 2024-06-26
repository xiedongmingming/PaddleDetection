# 训练

入口文件：tools/train.py

关键参数：-c 模型训练配置文件

样例：configs\picodet\legacy_model\application\layout_analysis\picodet_lcnet_x1_0_layout_cdla.yml

配置文件中指定了：
- TrainDataset
- EvalDataset
- TestDataset















常见错误：

```
RuntimeError: (PreconditionNotMet) The third-party dynamic library (cudnn64_8.dll) that Paddle depends on is not configured correctly. (error code is 126)
  Suggestions:
  1. Check if the third-party dynamic library (e.g. CUDA, CUDNN) is installed correctly and its version is matched with paddlepaddle you installed.
  2. Configure third-party dynamic library environment variables as follows:
  - Linux: set LD_LIBRARY_PATH by `export LD_LIBRARY_PATH=...`
  - Windows: set PATH by `set PATH=XXX; (at ..\paddle\phi\backends\dynload\dynamic_loader.cc:312)
```