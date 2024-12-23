```sh
bash build.sh release --init --make -j2 --silent
bash build.sh debug --init --make -j2 --silent
```

```sh
# 在 oceanbase 目录下运行
./tools/deploy/obd.sh prepare -p /tmp/obtest
./tools/deploy/obd.sh deploy -c obcluster.yaml
```

```sh
# 使用客户端连接observer
./deps/3rd/u01/obclient/bin/obclient -h127.0.0.1 -P2881 -uroot -Doceanbase -A
./deps/3rd/u01/obclient/bin/obclient -h127.0.0.1 -P2881 -uroot@perf -Dtest -A
create resource unit unit_1 max_cpu 6, memory_size "10G", log_disk_size "10G";
create resource pool pool_2 unit = 'unit_1', unit_num = 1, zone_list = ('zone1');
create tenant perf replica_num = 1,primary_zone='zone1', resource_pool_list=('pool_2') set ob_tcp_invited_nodes='%';

```

gdb attach $(pidof observer)

```sh
# 停止测试集群
./tools/deploy/obd.sh stop -n obcluster
#替换二进制文件
cp build_debug/src/observer/observer /tmp/obtest/bin/observer
cp build_debug/src/observer/observer /data/obcluster/bin/observer
cp build_release/src/observer/observer /data/obcluster/bin/observer
cp build_release/src/observer/observer /tmp/obtest/bin/observer
#启动测试集群
./tools/deploy/obd.sh start -n obcluster
# 重启集群
./tools/deploy/obd.sh restart obcluster
# 销毁集群
./tools/deploy/obd.sh destroy -n obcluster
```

运行前确保代码中的文件位置与运行环境的位置一致

```sh
python scirpt.py --pid [observer 线程id] [--skip-fit]
python scirpt.py --pid $(pidof observer) --skip-fit
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
python hybrid_ann.py
python -m ann_benchmarks.algorithms.oceanbase.hybrid_ann --skip_fit
python -m ann_benchmarks.algorithms.oceanbase.hybrid_ann --skip_fit
```


```
alter system set ob_vector_memory_limit_percentage=34;
DROP TABLE IF EXISTS items1;
CREATE TABLE items1 (id int,c1 int, embedding vector(5), primary key(id),key(c1));
insert into items1 values (1, 1, '[10, 10, 10, 10, 10]');
SELECT id FROM items1 ORDER BY l2_distance(embedding, '[10, 10, 10, 10, 10]') APPROXIMATE LIMIT 1;
set ob_log_level=trace;
select last_trace_id();

SET GLOBAL ob_query_timeout =1000000000000;
```