---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">🌐 更换阿里源</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">为什么换源？</h3>

默认 Ubuntu 源位于国外，国内访问速度慢：

- 软件下载慢
- 更新时间长
- 容易超时失败

阿里源是国内最稳定的镜像源之一。

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">🔧 备份原配置</h3>

```bash
# 备份 ubuntu.sources（Ubuntu 24.04）
sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak
```

</div>

<div class="mt-10">
<h3 class="text-xl font-semibold mb-4">📝 替换为阿里源</h3>

```bash
# 使用 sed 替换（适用于 Ubuntu 24.04 DEB822 格式）
sudo sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources
sudo sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list.d/ubuntu.sources
```

</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">🔍 手动编辑方式</h3>

```bash
# 打开配置文件
sudo nano /etc/apt/sources.list.d/ubuntu.sources

# 在 File: 行中替换地址
# 原：http://archive.ubuntu.com/ubuntu/
# 改：http://mirrors.aliyun.com/ubuntu/
```

<h3 class="text-xl font-semibold mb-4 mt-10">✅ 更新软件源</h3>

```bash
# 更新源列表
sudo apt update

# 升级已安装软件
sudo apt upgrade -y
```

<h3 class="text-xl font-semibold mb-4 mt-10">📋 其他常用源</h3>

| 源名称 | 地址 |
|--------|------|
| 清华源 | mirrors.tuna.tsinghua.edu.cn |
| 中科大源 | mirrors.ustc.edu.cn |
| 华为源 | repo.huaweicloud.com |

</div>

<div class="mt-8 p-5 bg-green-500/10 border-l-4 border-green-500 rounded-lg">
✅ 换源后软件下载速度会显著提升，建议安装系统后立即更换。
</div>
