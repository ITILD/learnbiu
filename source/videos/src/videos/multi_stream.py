"""接入一路 RTSP 流，用 200x200 窗口显示，最简实现（带断线重连）。

用法（在 source/videos 目录下）：
    uv run videos        # 按 q 退出；公网源首帧约需 8~15 秒
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import cv2
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[2] / "stream_source.yaml"
WINDOW = "rtsp"

# 本机 UDP 被阻断，强制 RTSP over TCP + 低延迟参数（须在打开流之前设置）
os.environ.setdefault(
    "OPENCV_FFMPEG_CAPTURE_OPTIONS",
    "rtsp_transport;tcp|fflags;nobuffer|flags;low_delay|max_delay;0",
)


def main() -> None:
    stream = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))["streams"][0]
    url = stream["url"]
    print(f"连接 {stream['id']}: {url}（首帧约需 8~15 秒）")

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW, 200, 200)

    cap, delay = None, 2.0
    while True:
        if cap is None:
            # 公网源会瞬时拒绝连接，打开失败就退避重试
            cap = cv2.VideoCapture(
                url, cv2.CAP_FFMPEG,
                [cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 15000,
                 cv2.CAP_PROP_READ_TIMEOUT_MSEC, 15000],
            )
            if not cap.isOpened():
                cap.release()
                cap = None
                print(f"打开失败，{delay:.0f}s 后重试", flush=True)
                time.sleep(delay)
                delay = min(delay * 2, 30.0)
                continue
            delay = 2.0

        ok, frame = cap.read()
        if not ok:
            # 直播中断：释放后回到上面的打开分支
            print("读取中断，准备重连", flush=True)
            cap.release()
            cap = None
            continue

        cv2.imshow(WINDOW, frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
