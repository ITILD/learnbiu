wget https://github.com/Schniz/fnm/releases/latest/download/fnm-linux.zip
unzip fnm-linux.zip -d /usr/local/bin
chmod +x /usr/local/bin/fnm
eval "$(fnm env --use-on-cd)"
source ~/.bashrc

fnm -V
fnm install v22.19.0
fnm use v22.19.0

corepack prepare pnpm@latest --activate
corepack enable


# 检查是否已存在 fnm 配置，避免重复添加
grep -q 'fnm env --use-on-cd --shell bash' ~/.bashrc || \
echo 'eval "$(fnm env --use-on-cd --shell bash)"' >> ~/.bashrc

# 重载配置使当前终端立即生效
source ~/.bashrc