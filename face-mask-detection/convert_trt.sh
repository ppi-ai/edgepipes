#!/bin/bash
./tlt-converter /home/jetson/edgepipes/face-mask-detection/experiment_dir_final/resnet18_detector.etlt \
               -k tlt_encode \
               -o output_cov/Sigmoid,output_bbox/BiasAdd \
               -d 3,544,960 \
               -i nchw \
               -m 8 \
               -t fp16 \
               -e /home/jetson/edgepipes/face-mask-detection/experiment_dir_final/resnet18_detector.trt \
               -b 4
