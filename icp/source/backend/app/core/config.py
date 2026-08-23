"""应用配置：支持通过环境变量 / .env 文件覆盖默认值"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置项"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # 应用信息
    app_name: str = "拾叶集 API"
    debug: bool = False

    # 数据库（SQLite）
    database_url: str = "sqlite:///./data/app.db"

    # JWT 密钥与有效期（生产环境务必通过环境变量修改）
    secret_key: str = "change-me-in-production-please-use-a-random-secret"
    token_expire_minutes: int = 60 * 24 * 7  # 默认 7 天

    # 初始管理员账号（首次启动时自动创建）
    admin_username: str = "admin"
    admin_password: str = "admin123"


settings = Settings()
