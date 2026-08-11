#!/bin/sh
# 在容器内统一构建所有教程的静态站点
# 产物落到各 <教程>/ppt/dist（外挂回宿主机），供 nginx 托管
#
# 部署子路径与 nginx.conf、docker-compose.yml 中的挂载点一一对应。
# 不依赖各 package.json 的 build_base 脚本名，统一用 slidev --base 覆盖，
# 因此无需修改源项目即可把教程部署到子路径。
set -e

# 教程名|部署子路径（c++ 目录名含 +，用 | 分隔避免 shell 解析问题）
cat <<'EOF' > /tmp/targets
RAG|/learnbiu_rag/
python|/learnbiu_python/
c++|/learnbiu_cpp/
ubuntu|/learnbiu_ubuntu/
wsl2|/learnbiu_wsl2/
EOF

while IFS='|' read -r name base; do
  [ -z "$name" ] && continue
  dir="/work/$name/ppt"
  if [ ! -d "$dir" ]; then
    echo "!! 跳过 $name：$dir 不存在"
    continue
  fi
  echo "==> 构建 $name (base=$base)"
  cd "$dir"
  if [ -f pnpm-lock.yaml ]; then
    pnpm install --frozen-lockfile || pnpm install
  else
    pnpm install
  fi
  # 静态构建；--base 决定资源引用前缀，需与 nginx location 一致
  pnpm exec slidev build --base "$base"
  echo "==> 完成 $name -> $dir/dist"
done < /tmp/targets

echo "全部构建完成"
