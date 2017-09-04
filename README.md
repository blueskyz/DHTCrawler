DHTCrawler
==========

python 编写的DHT Crawler 网络爬虫，抓取DHT网络的磁力链接。


文件
----

### collector.py dht网络爬虫脚本

    抓取dht网络的磁力链接，使用 libtorrent 的python绑定库开发

### collectord.py dht爬虫服务监控程序

    启动并监控dht爬虫进程，在爬虫进程退出后重启启动爬虫，使用 twisted 开发


安装和使用方法
--------------

### 运行环境

*__运行的机器要能被外网访问，用来接收dht网络节点的信息，使用vps即可__*

  1. linux 服务器
  2. python 2.7.3
  3. 安装 libtorrent 的 python 绑定库
  4. 安装 twisted 网络库
  5. 开放防火墙的对应端口段，目前默认的是 32900--32920 (20是工作的p2p客户端数量)

### 运行方法

  1. 下载 collector.py collectord.py 文件到安装目录
  2. 脚本方式测试运行： python collector.py result.json collector.state
  3. 服务方式运行：twistd -y collectord.py

### 状态查看

  1. 通过 twistd 服务启动时，服务状态查看：telnet 127.0.0.1 31000
  2. 命令行或服务启动是，爬虫状态查看：cat collector.state
  
### 运行结果

    result.json 是收集的磁力链接结果文件，json格式，key是资源的info hash，value是资源的热度

<br>

### 初学者入门群

  * 一群工程师组建的面向初学者的学习群
  * 有问题可以加群问，这样效率更高
  * 非商业性质，拒绝广告，只接收真正想学这方面技术的朋友，交流学习
  * 申请请说明来自 github

### 群列表

  * python Linux 初学者入门群（ qq 群号：278529278 ）
  * php Linux 初学者入门群（ qq 群号：476648701 ）
