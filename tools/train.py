# Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

# add python path of PaddleDetection to sys.path
parent_path = os.path.abspath(os.path.join(__file__, *(['..'] * 2)))
sys.path.insert(0, parent_path)

# ignore warning log
import warnings

warnings.filterwarnings('ignore')

import paddle

from ppdet.core.workspace import load_config, merge_config

from ppdet.engine import Trainer, TrainerCot, init_parallel_env, set_random_seed, init_fleet_env
from ppdet.engine.trainer_ssod import Trainer_DenseTeacher, Trainer_ARSL, Trainer_Semi_RTDETR

from ppdet.slim import build_slim_model

from ppdet.utils.cli import ArgsParser, merge_args
import ppdet.utils.check as check
from ppdet.utils.logger import setup_logger

logger = setup_logger('train')


def parse_args():

    parser = ArgsParser()  # 提供基础命令行参数

    parser.add_argument(
        "--eval",
        action='store_true',
        default=False,
        help="Whether to perform evaluation in train"
    )
    parser.add_argument(
        "-r", "--resume", default=None, help="weights path for resume"
    )
    parser.add_argument(
        "--slim_config",
        default=None,
        type=str,
        help="Configuration file of slim method."
    )
    parser.add_argument(
        "--enable_ce",
        type=bool,
        default=False,
        help="If set True, enable continuous evaluation job."
        "This flag is only used for internal test."
    )
    parser.add_argument(
        "--amp",
        action='store_true',
        default=False,
        help="Enable auto mixed precision training."
    )
    parser.add_argument(
        "--fleet",
        action='store_true',
        default=False,
        help="Use fleet or not"
    )
    parser.add_argument(
        "--use_vdl",
        type=bool,
        default=False,
        help="whether to record the data to VisualDL."
    )
    parser.add_argument(
        '--vdl_log_dir',
        type=str,
        default="vdl_log_dir/scalar",
        help='VisualDL logging directory for scalar.'
    )
    parser.add_argument(
        "--use_wandb",
        type=bool,
        default=False,
        help="whether to record the data to wandb."
    )
    parser.add_argument(
        '--save_prediction_only',
        action='store_true',
        default=False,
        help='Whether to save the evaluation results only'
    )
    parser.add_argument(
        '--profiler_options',
        type=str,
        default=None,
        help="The option of profiler, which should be in "
        "format \"key1=value1;key2=value2;key3=value3\"."
        "please see ppdet/utils/profiler.py for detail."
    )
    parser.add_argument(
        '--save_proposals',
        action='store_true',
        default=False,
        help='Whether to save the train proposals'
    )
    parser.add_argument(
        '--proposals_path',
        type=str,
        default="sniper/proposals.json",
        help='Train proposals directory'
    )
    parser.add_argument(
        "--to_static",
        action='store_true',
        default=False,
        help="Enable dy2st to train."
    )

    args = parser.parse_args()

    return args


def run(FLAGS, cfg):

    if cfg.fleet:  # init fleet environment
        init_fleet_env(cfg.get('find_unused_parameters', False))
    else:  # init parallel environment if nranks > 1
        init_parallel_env()

    if FLAGS.enable_ce:

        set_random_seed(0)

    # build trainer
    ssod_method = cfg.get('ssod_method', None)

    if ssod_method is not None:

        if ssod_method == 'DenseTeacher':
            trainer = Trainer_DenseTeacher(cfg, mode='train')
        elif ssod_method == 'ARSL':
            trainer = Trainer_ARSL(cfg, mode='train')
        elif ssod_method == 'Semi_RTDETR':
            trainer = Trainer_Semi_RTDETR(cfg, mode='train')
        else:
            raise ValueError("Semi-Supervised Object Detection only no support this method.")

    elif cfg.get('use_cot', False):
        trainer = TrainerCot(cfg, mode='train')
    else:
        trainer = Trainer(cfg, mode='train')  # 关键步骤4

    # load weights
    if FLAGS.resume is not None:

        trainer.resume_weights(FLAGS.resume)

    elif 'pretrain_student_weights' in cfg and 'pretrain_teacher_weights' in cfg and cfg.pretrain_teacher_weights and cfg.pretrain_student_weights:

        trainer.load_semi_weights(cfg.pretrain_teacher_weights, cfg.pretrain_student_weights)

    elif 'pretrain_weights' in cfg and cfg.pretrain_weights:

        trainer.load_weights(cfg.pretrain_weights)  # 'https://paddledet.bj.bcebos.com/models/pretrained/LCNet_x1_0_pretrained.pdparams'

    # training
    trainer.train(FLAGS.eval)  # 关键步骤5


# 主函数定义
def main():

    FLAGS = parse_args()  # 关键步骤1：加载运行参数

    cfg = load_config(FLAGS.config)  # 关键步骤2：加载YAML配置

    merge_args(cfg, FLAGS)  # 排除一些命令行参数

    merge_config(FLAGS.opt)

    if 'use_npu' not in cfg:  # disable npu in config by default

        cfg.use_npu = False

    if 'use_xpu' not in cfg:  # disable xpu in config by default

        cfg.use_xpu = False

    if 'use_gpu' not in cfg:

        cfg.use_gpu = False

    if 'use_mlu' not in cfg:  # disable mlu in config by default

        cfg.use_mlu = False

    if cfg.use_gpu:
        place = paddle.set_device('gpu')
    elif cfg.use_npu:
        place = paddle.set_device('npu')
    elif cfg.use_xpu:
        place = paddle.set_device('xpu')
    elif cfg.use_mlu:
        place = paddle.set_device('mlu')
    else:
        place = paddle.set_device('cpu')

    if FLAGS.slim_config:

        cfg = build_slim_model(cfg, FLAGS.slim_config)

    # FIXME: Temporarily solve the priority problem of FLAGS.opt
    merge_config(FLAGS.opt)

    check.check_config(cfg)

    check.check_gpu(cfg.use_gpu)
    check.check_npu(cfg.use_npu)
    check.check_xpu(cfg.use_xpu)
    check.check_mlu(cfg.use_mlu)

    check.check_version()

    run(FLAGS, cfg) # 关键步骤3：


# 程序入口
if __name__ == "__main__":
    #
    main()  # 主函数入口
