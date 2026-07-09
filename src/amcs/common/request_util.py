# -*- coding: utf-8 -*-
"""AMCS 通用请求工具。

这一层只负责两件事：
1. 统一管理 requests.Session，复用登录后的会话。
2. 统一补齐 base_url、timeout、verify 等公共参数。
"""
from __future__ import annotations

from typing import Any

import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class RequestUtil:
    """统一管理 session、base_url 和默认超时。"""

    def __init__(self, config: dict[str, Any]):
        """保存配置并创建一个可复用的 Session。"""
        self.config = config
        self.session = requests.Session()

    def send_request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """发送 HTTP 请求。

        支持传完整 URL，也支持传相对路径。
        如果调用方没有显式指定 timeout 和 verify，这里会自动套用配置文件里的默认值。
        """
        timeout = self.config.get("timeout", 10)
        verify = self.config.get("verify_ssl", False)
        base_url = self.config.get("base_url", "").rstrip("/")

        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout
        if "verify" not in kwargs:
            kwargs["verify"] = verify

        if url.startswith(("http://", "https://")):
            final_url = url
        else:
            if not base_url:
                raise ValueError("未配置 base_url，请在 AMCS_CONFIG_FILE 指向的外部测试配置中设置访问地址")
            # 相对路径统一拼接到配置中的 base_url 下，避免各接口类重复处理。
            final_url = f"{base_url}/{url.lstrip('/')}"

        return self.session.request(method=method, url=final_url, **kwargs)
