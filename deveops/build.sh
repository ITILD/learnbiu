#!/bin/sh
# 自动发现并构建所有 <教程>/ppt，聚合到 deveops/sites/ 供 nginx 自动托管
# 新增教程无需改 nginx.conf 或 docker-compose.yml，重新运行本脚本即可生效
#
# 用法：
#   build.sh               # 自动发现并构建全部教程
#   build.sh RAG python    # 只构建指定教程（教程目录名）
#
# URL 规则：/learnbiu_<slug>/ ，slug = 教程目录名小写（c++ -> cpp）
set -e

ROOT="/work"
SITES="$ROOT/deveops/sites"

# 教程目录名 -> URL slug
slug_for() {
  case "$1" in
    "c++") echo "cpp" ;;                 # + 不宜出现在 URL 路径
    *)     echo "$1" | tr '[:upper:]' '[:lower:]' ;;
  esac
}

build_one() {
  name=$1
  dir="$ROOT/$name/ppt"
  [ -d "$dir" ] || { echo "!! 跳过 $name：$dir 不存在"; return; }
  [ -f "$dir/package.json" ] || { echo "!! 跳过 $name：无 package.json"; return; }
  slug=$(slug_for "$name")
  base="/learnbiu_$slug/"
  echo "==> 构建 $name (base=$base)"
  cd "$dir"
  if [ -f pnpm-lock.yaml ]; then
    pnpm install --frozen-lockfile || pnpm install
  else
    pnpm install
  fi
  pnpm exec slidev build --base "$base"
  # 同步产物到 sites（拷贝；web 容器看不到源码挂载点，故不能用软链）
  rm -rf "$SITES/learnbiu_$slug"
  mkdir -p "$SITES/learnbiu_$slug"
  cp -a "$dir/dist/." "$SITES/learnbiu_$slug/"
  echo "==> 完成 $name -> sites/learnbiu_$slug"
}

mkdir -p "$SITES"

if [ $# -gt 0 ]; then
  for name in "$@"; do build_one "$name"; done
else
  # 自动发现所有带 ppt/package.json 的教程目录
  for ppt_dir in "$ROOT"/*/ppt; do
    [ -d "$ppt_dir" ] || continue
    [ -f "$ppt_dir/package.json" ] || continue
    build_one "$(basename "$(dirname "$ppt_dir")")"
  done
fi

# 自动生成导航页：列出 sites 下所有教程
echo "==> 生成导航页 sites/index.html"
{
  printf '<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>LearnBiu 教程</title><body style="font:16px system-ui;max-width:640px;margin:2rem auto;padding:0 1rem"><h1>LearnBiu 教程</h1><ul style="line-height:2">\n'
  for d in "$SITES"/learnbiu_*/; do
    [ -d "$d" ] || continue
    site=$(basename "$d")
    label=${site#learnbiu_}
    printf '<li><a href=/%s/>%s</a>\n' "$site" "$label"
  done
  printf '</ul>\n'
} > "$SITES/index.html"

echo "全部完成"
