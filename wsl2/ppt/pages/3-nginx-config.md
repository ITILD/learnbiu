---
layout: two-cols
---

<div class="text-3xl font-bold mb-6">⚙️ Nginx 配置与静态站点</div>

<div class="mt-8">
<h3 class="text-xl font-semibold mb-4">📝 自定义 Nginx 配置</h3>

```bash
# 创建配置目录
mkdir -p ~/nginx-conf

# 创建自定义配置
cat > ~/nginx-conf/default.conf <<'EOF'
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }

    location /api {
        return 200 '{"status": "ok"}';
        add_header Content-Type application/json;
    }
}
EOF
```
</div>

::right::

<div class="mt-4">
<h3 class="text-xl font-semibold mb-6">🚀 挂载配置运行</h3>

```bash
docker run -d \
  --name my-nginx-custom \
  -p 8082:80 \
  -v ~/nginx-site:/usr/share/nginx/html:ro \
  -v ~/nginx-conf/default.conf:/etc/nginx/conf.d/default.conf:ro \
  nginx:latest
```

<h3 class="text-xl font-semibold mb-4 mt-10">🧪 验证配置</h3>

```bash
# 访问静态页面
curl http://localhost:8082

# 访问 API 接口
curl http://localhost:8082/api
# {"status": "ok"}

# 检查 Nginx 配置语法
docker exec my-nginx-custom nginx -t

# 重载配置（不中断服务）
docker exec my-nginx-custom nginx -s reload
```
</div>

<div class="mt-6 p-5 bg-pink-500/10 border-l-4 border-pink-500 rounded-lg">
🔧 通过 <b>-v</b> 挂载配置文件，无需重新构建镜像即可修改 Nginx 行为。
</div>