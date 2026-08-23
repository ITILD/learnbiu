"""Casbin 鉴权初始化：admin 可读写，游客只读"""

from pathlib import Path

import casbin

_BASE_DIR = Path(__file__).parent

# RBAC 模型：主体(用户名/角色) + 资源(接口路径) + 动作(HTTP 方法)
enforcer = casbin.Enforcer(
    str(_BASE_DIR / "casbin_model.conf"),
    str(_BASE_DIR / "casbin_policy.csv"),
)


def add_admin_role(username: str) -> None:
    """为管理员账号授予 admin 角色（已存在则自动跳过）"""
    enforcer.add_role_for_user(username, "admin")


def check_permission(subject: str, path: str, method: str) -> bool:
    """校验主体对指定路径 + 方法是否有权限"""
    return enforcer.enforce(subject, path, method)
