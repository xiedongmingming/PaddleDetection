# PADDLEDETECTION预测部署

PADDLEDETECTION提供了PADDLE INFERENCE、PADDLE SERVING、PADDLE-LITE多种部署形式，支持服务端、移动端、嵌入式等多种平台，提供了完善的PYTHON和C++部署方案。

## PADDLEDETECTION支持的部署形式说明
|形式|语言|教程|设备/平台|
|-|-|-|-|
|Paddle Inference|Python|已完善|Linux(ARM\X86)、Windows
|Paddle Inference|C++|已完善|Linux(ARM\X86)、Windows|
|Paddle Serving|Python|已完善|Linux(ARM\X86)、Windows|
|Paddle-Lite|C++|已完善|Android、IOS、FPGA、RK...


## 1. PADDLEINFERENCE部署

### 1.1 导出模型

使用`TOOLS/EXPORT_MODEL.PY`脚本导出模型以及部署时使用的配置文件，配置文件名字为`INFER_CFG.YML`。模型导出脚本如下：
```bash
# 导出YOLOV3模型
python tools/export_model.py 
	-c configs/yolov3/yolov3_mobilenet_v1_roadsign.yml 
	-o weights=output/yolov3_mobilenet_v1_roadsign/best_model.pdparams
```
预测模型会导出到`OUTPUT_INFERENCE/YOLOV3_MOBILENET_V1_ROADSI`目录下，分别为

- infer_cfg.yml

- model.pdiparams

- model.pdiparams.info

- model.pdmodel

  模型导出具体请参考文档[PADDLEDETECTION模型导出教程](EXPORT_MODEL.md)。

### 1.2 使用PADDLEINFERENCE进行预测
* PYTHON部署支持`CPU`、`GPU`和`XPU`环境，支持WINDOWS、LINUX系统，支持NV JETSON嵌入式设备上部署。参考文档[PYTHON部署](python/README.md)
* C++部署支持`CPU`、`GPU`和`XPU`环境，支持WINDOWS、LINUX系统，支持NV JETSON嵌入式设备上部署。参考文档[C++部署](cpp/README.md)
* PADDLEDETECTION支持TENSORRT加速，相关文档请参考[TENSORRT预测部署教程](TENSOR_RT.md)

**注意：**PADDLE预测库版本需要>=2.1，BATCH_SIZE>1仅支持YOLOV3和PP-YOLO。

##  2. PADDLESERVING部署
### 2.1 导出模型

如果需要导出`PADDLESERVING`格式的模型，需要设置`EXPORT_SERVIING_MODEL=TRUE`：
```buildoutcfg
python tools/export_model.py 
	-c configs/yolov3/yolov3_mobilenet_v1_roadsign.yml 
	-o weights=output/yolov3_mobilenet_v1_roadsign/best_model.pdparams 
	--export_serving_model=True
```
预测模型会导出到`OUTPUT_INFERENCE/YOLOV3_DARKNET53_270E_COCO`目录下，分别为

- infer_cfg.yml
- model.pdiparams
- model.pdiparams.info
- model.pdmodel
- serving_client/文件夹
- serving_server/文件夹

模型导出具体请参考文档[PADDLEDETECTION模型导出教程](EXPORT_MODEL.md)。

### 2.2 使用PADDLESERVING进行预测
* [安装PADDLESERVING](https://github.com/PaddlePaddle/Serving/blob/develop/README.md#installation)
* [使用PADDLESERVING](./serving/README.md)


## 3. PADDLELITE部署
- [使用PADDLELITE部署PADDLEDETECTION模型](./lite/README.md)
- 详细案例请参考[PADDLE-LITE-DEMO](https://github.com/PaddlePaddle/Paddle-Lite-Demo)部署。更多内容，请参考[PADDLE-LITE](https://github.com/PaddlePaddle/Paddle-Lite)


## 4. 第三方部署（MNN、NCNN、OPENVINO）
- 第三方部署提供PICODET、TINYPOSE案例，其他模型请参考修改
- TINYPOSE部署推荐工具：INTEL CPU端推荐使用OPENVINO，GPU端推荐使用PADDLEINFERENCE，ARM/ANDROID端推荐使用PADDLELIT或者MNN

| Third_Engine | MNN  | NCNN  | OPENVINO   |
| ------------ | ---- | ----- | ---------- |
| PicoDet      | [PicoDet_MNN](./third_engine/demo_mnn/README.md)       | [PicoDet_NCNN](./third_engine/demo_ncnn/README.md) | [PicoDet_OPENVINO](./third_engine/demo_openvino/README.md)   |
| TinyPose     | [TinyPose_MNN](./third_engine/demo_mnn_kpts/README.md) | -                                                  | [TinyPose_OPENVINO](./third_engine/demo_openvino_kpts/README.md) |



## 5. BENCHMARK测试
- 使用导出的模型，运行BENCHMARK批量测试脚本：
```shell
sh deploy/benchmark/benchmark.sh {model_dir} {model_name}
```
**注意**如果是量化模型，请使用`DEPLOY/BENCHMARK/BENCHMARK_QUANT.SH`脚本。

- 将测试结果LOG导出至EXCEL中：
```
python deploy/benchmark/log_parser_excel.py --log_path=./output_pipeline --output_name=benchmark_excel.xlsx
```

## 6. 常见问题QA
- 1、`PADDLE1.8.4`训练的模型，可以用`PADDLE2.0`部署吗？
  PADDLE2.0是兼容PADDLE1.8.4的，因此是可以的。但是部分模型（如SOLOV2）使用到了PADDLE2.0中新增OP，这类模型不可以。

- 2、WINDOWS编译时，预测库是VS2015编译的，选择VS2017或VS2019会有问题吗？
  关于VS兼容性问题请参考：[C++ VISUAL STUDIO 2015、2017和2019之间的二进制兼容性](https://docs.microsoft.com/zh-cn/cpp/porting/binary-compat-2015-2017?view=msvc-160)

- 3、CUDNN8.0.4连续预测会发生内存泄漏吗？
  经QA测试，发现CUDNN8系列连续预测时都有内存泄漏问题，且CUDNN8性能差于CUDNN7，推荐使用CUDA+CUDNN7.6.4的方式进行部署。
