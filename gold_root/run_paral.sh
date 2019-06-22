#!/bin/bash

rm -rf ./train_leveldb ./val_leveldb mean.binaryproto 
../caffe-parallel-master/build/tools/convert_imageset -backend leveldb --shuffle ./ ./images/train.txt ./train_leveldb
../caffe-parallel-master/build/tools/convert_imageset -backend leveldb --shuffle ./ ./images/val.txt ./val_leveldb

../caffe-parallel-master/build/tools/compute_image_mean train_leveldb/ mean.binaryproto leveldb
echo "now call: "
echo "mpiexec -n 10 ../caffe-parallel-master/build/tools/caffe train --solver=model/solver.prototxt --snapshot=snapshot_iter_run.solverstate"

# $Id: $


