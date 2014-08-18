DHTCrawler
==========

抓取DHT网络的磁力链接


文件
----

### collector.py dht网络爬虫脚本

    抓取dht网络的磁力链接，使用 libtorrent 库开发。

### collectord.py dht爬虫服务监控程序

    启动并监控dht爬虫进程，在爬虫进程退出后重启启动爬虫，使用 twisted 开发。
    


安装和使用方法
--------------

### 安装爬虫脚本

    1. 安装 libtorrent 的 python 绑定库
    2. 安装 twisted 网络库
    3. 下载 collector.py collectord.py 文件到安装目录

### 运行方法

    1. 脚本方式测试运行： python collector.py result.json collector.state
    2. 服务方式运行：twistd -y collectord.py

### 状态查看

    1. 服务状态查看：telnet 127.0.0.1 31000
    2. cat collector.state
  
### 运行结果

    result.json 是收集的磁力链接结果文件，json格式，key是资源的info hash，value是资源的热度
