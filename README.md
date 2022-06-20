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

## Go 开发的电商平台

技术：golang、vue开发、小程序开发

  * 一群工程师开发的B2B、B2C电商平台
  * 目前客户百万级别月GMV
  * 可以提供整套服务合作、或者整套源代码出售
  * 电商平台简介
  > 1. 海外版跨境电商h5、web平台
  > 2. 经销商车销平台（业务员下单，司机带货管理)
  > 3. 天阶高性能 B2B、B2C 电商平台，商城与管理后台完全分离，支持多公司多仓库加盟模式
  >    支持高并发，集群水平扩展，微信小程序商城

### golang 电商开发技术交流群

  * 欢迎大家交流电商开发的技术，经验
  * QQ群：226220067 加群请说明来自 github

![image](https://user-images.githubusercontent.com/1860564/174646268-8cfe046d-1937-46c1-9e26-a4424501f158.png){:width="400px"}

