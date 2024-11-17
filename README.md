```sh
bash build.sh release --init --make -j2 --silent
```

```sh
# 在 oceanbase 目录下运行
./tools/deploy/obd.sh prepare -p /tmp/obtest
./tools/deploy/obd.sh deploy -c obcluster.yaml
```

```sh
# 使用客户端连接observer
./deps/3rd/u01/obclient/bin/obclient -h127.0.0.1 -P2881 -uroot -Doceanbase -A
```

```sh
# 停止测试集群
./tools/deploy/obd.sh stop -n obcluster
#替换二进制文件
cp build_debug/src/observer/observer /tmp/obtest/bin/observer
cp build_release/src/observer/observer /tmp/obtest/bin/observer
#启动测试集群
./tools/deploy/obd.sh start -n obcluster
# 重启集群
./tools/deploy/obd.sh cluster restart obcluster
```

运行前确保代码中的文件位置与运行环境的位置一致

```sh
python scirpt.py --port [ob端口号] [--skip-fit]
```

```sh
# 测试时导入数据并构建索引
python run.py --algorithm oceanbase --local --force --dataset sift-128-euclidean --runs 1
# 测试时跳过导入数据及构建索引
python run.py --algorithm oceanbase --local --force --dataset sift-128-euclidean --runs 1 --skip_fit
# 计算召回率及 QPS
python plot.py --dataset sift-128-euclidean --recompute
```

```sh
# 示例命令
python plot.py --dataset sift-128-euclidean --recompute
# 示例输出如下，其中每行结果倒数第一个值为该算法对应的QPS，每行结果倒数第二个值为该算法对应的召回率。
Computing knn metrics
  0:                               OBVector(m=16, ef_construction=200, ef_search=400)        0.999      416.990
Computing knn metrics
  1:                                                                 BruteForceBLAS()        1.000      355.359
```

```sh
python python hybrid_ann.py
``