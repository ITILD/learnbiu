#!/bin/bash
# 开启严格模式：任何命令执行失败或变量未定义时，立即退出脚本
set -euo pipefail

CURRENT_USER_PASSWORD="qwer1234"

# 1. 初始验证密码，获取 sudo 权限并建立缓存
echo "${CURRENT_USER_PASSWORD}" | sudo -S -v > /dev/null 2>&1

# 2. 启动后台 Keep-Alive 进程，每 50 秒刷新一次 sudo 时间戳
(
  while true; do
    echo "${CURRENT_USER_PASSWORD}" | sudo -S -v > /dev/null 2>&1
    sleep 50
  done
) &
# 记录后台进程 PID
SUDO_KEEP_ALIVE_PID=$!

# 3. 定义清理函数：确保脚本结束时彻底关闭后台进程并回收资源
cleanup() {
    # 强制杀死后台 Keep-Alive 进程 (使用 -9 确保在 sleep 期间也能立即终止)
    kill -9 $SUDO_KEEP_ALIVE_PID 2>/dev/null || true
    # 等待进程真正退出，防止产生僵尸进程
    wait $SUDO_KEEP_ALIVE_PID 2>/dev/null || true
}

# 4. 注册 Trap：捕获退出(EXIT)、中断(INT/Ctrl+C)、终止(TERM)信号
trap cleanup EXIT INT TERM

# --- 后续命令无需再传递密码，且权限永不过期 ---

# 5. 定位公钥文件路径（脚本同目录下的 id_ed25519.pub）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PUB_KEY_FILE="${SCRIPT_DIR}/id_ed25519.pub"

# 验证公钥文件是否存在
if [[ ! -f "${PUB_KEY_FILE}" ]]; then
    echo "Error: Public key file not found: ${PUB_KEY_FILE}"
    exit 1
fi

# 读取公钥内容并去除首尾空白
PUB_KEY_CONTENT="$(cat "${PUB_KEY_FILE}" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"

if [[ -z "${PUB_KEY_CONTENT}" ]]; then
    echo "Error: Public key file is empty: ${PUB_KEY_FILE}"
    exit 1
fi

echo "Info: Loaded public key from: ${PUB_KEY_FILE}"

# 6. 为指定用户配置 authorized_keys 的函数
setup_ssh_key_for_user() {
    local TARGET_USER="$1"
    local USER_HOME
    USER_HOME="$(eval echo "~${TARGET_USER}")"

    echo "Info: Setting up SSH public key for user: ${TARGET_USER} (home: ${USER_HOME})"

    # 创建 .ssh 目录（若不存在）
    sudo mkdir -p "${USER_HOME}/.ssh"

    # 创建 authorized_keys 文件（若不存在），并确保追加时不会重复添加相同公钥
    local AUTH_KEYS="${USER_HOME}/.ssh/authorized_keys"

    # 使用临时文件来安全地处理内容
    local TEMP_FILE
    TEMP_FILE="$(mktemp)"

    # 先保留原有内容（跳过空行和注释行来判断是否已存在相同公钥）
    if [[ -f "${AUTH_KEYS}" ]]; then
        # 提取已有的纯公钥行（去掉注释，只比较密钥主体）
        sudo grep -v '^\s*$' "${AUTH_KEYS}" | grep -v '^\s*#' > "${TEMP_FILE}" || true
    fi

    # 检查公钥是否已存在（使用公钥的核心部分进行匹配，避免注释差异导致重复）
    local KEY_CORE
    KEY_CORE="$(echo "${PUB_KEY_CONTENT}" | awk '{print $1" "$2}')"

    if grep -Fq "${KEY_CORE}" "${TEMP_FILE}" 2>/dev/null; then
        echo "Info: Public key already exists for user ${TARGET_USER}, skipping."
        rm -f "${TEMP_FILE}"
    else
        # 追加新公钥到临时文件
        echo "${PUB_KEY_CONTENT}" >> "${TEMP_FILE}"

        # 将最终内容写回 authorized_keys
        sudo cp "${TEMP_FILE}" "${AUTH_KEYS}"
        rm -f "${TEMP_FILE}"
        echo "Info: Public key added for user ${TARGET_USER}."
    fi

    # 收敛权限为 sshd 可接受范围：.ssh 目录 700，authorized_keys 600
    sudo chmod 700 "${USER_HOME}/.ssh"
    sudo chmod 600 "${AUTH_KEYS}"

    # 确保所有者正确
    sudo chown -R "${TARGET_USER}:$(id -gn "${TARGET_USER}")" "${USER_HOME}/.ssh"
}

# 7. 为当前普通用户配置公钥
CURRENT_USER="$(whoami)"
setup_ssh_key_for_user "${CURRENT_USER}"

# 8. 为 root 用户配置公钥
# setup_ssh_key_for_user "root"

# 9. 验证配置结果
echo "Info: Verifying SSH public key configuration..."

verify_key_for_user() {
    local TARGET_USER="$1"
    local USER_HOME
    USER_HOME="$(eval echo "~${TARGET_USER}")"
    local AUTH_KEYS="${USER_HOME}/.ssh/authorized_keys"
    local KEY_CORE
    KEY_CORE="$(echo "${PUB_KEY_CONTENT}" | awk '{print $1" "$2}')"

    if sudo grep -Fq "${KEY_CORE}" "${AUTH_KEYS}" 2>/dev/null; then
        local PERMS
        PERMS="$(sudo stat -c '%a' "${AUTH_KEYS}")"
        local DIR_PERMS
        DIR_PERMS="$(sudo stat -c '%a' "${USER_HOME}/.ssh")"

        if [[ "${PERMS}" == "600" && "${DIR_PERMS}" == "700" ]]; then
            echo "Success: User ${TARGET_USER} - public key configured correctly (perms: dir=${DIR_PERMS}, file=${PERMS})."
            return 0
        else
            echo "Error: User ${TARGET_USER} - permission mismatch (dir=${DIR_PERMS}, file=${PERMS}), expected dir=700, file=600."
            return 1
        fi
    else
        echo "Error: User ${TARGET_USER} - public key not found in authorized_keys."
        return 1
    fi
}

VERIFY_RESULT=0
verify_key_for_user "${CURRENT_USER}" || VERIFY_RESULT=1
# verify_key_for_user "root" || VERIFY_RESULT=1

if [[ ${VERIFY_RESULT} -eq 0 ]]; then
    echo "Success: All operations completed. SSH public key configured for ${CURRENT_USER} and root."
else
    echo "Error: Verification failed for one or more users."
    exit 1
fi

# 脚本执行到此处后，将自动触发 EXIT 信号，执行 cleanup 函数关闭后台进程
