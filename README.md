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
#启动测试集群
./tools/deploy/obd.sh start -n obcluster
```

运行前确保代码中的文件位置与运行环境的位置一致

```sh
python scirpt.py --port [ob端口号] [--skip-fit]
```