

# webra_hot_api
热门网站的热榜API
免部署，直接使用。

# github发版的版本参考如下方法

- 😆 发版使用pyinstaller 进行打包，不太了解这些东西，以后再研究研究怎么把包的大小搞下去

```shell
# 将下载下来的webra_top.zip 进行解压缩
unzip webra_top.zip
cd webra_top
# 赋予执行权限，init是用shell语句写的
chmod +x init

./init
Usage: ./init.sh {start|stop|restart|status}
# 启动
./init start
# 关闭
./init stop
# 重启
./init restart
# 查看状态
./init status

# 查看端口监听是否存在
ss -tanpl
State                 Recv-Q                Send-Q                               Local Address:Port                               Peer Address:Port               Process                                         
LISTEN                0                     128                                      127.0.0.1:5000                                    0.0.0.0:*                   users:(("top",pid=106379,fd=3))                

```


# 代码使用方法参考
https://www.webra.top/1371.html

![image](https://github.com/wiuid/webra_hot/assets/61615298/560b52ea-94f6-4e92-829e-124791e39042)


