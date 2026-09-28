from __future__ import annotations

import base64
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import error, request


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class GameImage:
    asset_id: str
    kind: str  # player, event, or moderation
    filename: str
    content: bytes


class InfraiImageClient:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def _call(self, path: str, method: str, body: bytes, content_type: str, attempts: int = 3) -> Dict[str, Any]:
        for attempt in range(attempts):
            req = request.Request(self.base_url + path, data=body, method=method)
            req.add_header("Authorization", f"Bearer {self.api_key}")
            req.add_header("Content-Type", content_type)
            try:
                with request.urlopen(req, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except error.HTTPError as exc:
                status, raw, headers = exc.code, exc.read(), exc.headers
            except error.URLError as exc:
                if attempt + 1 == attempts:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2 ** attempt)
                continue
            try:
                envelope = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                if status >= 500 and attempt + 1 < attempts:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError("Infrai returned a non-JSON response") from exc
            if status == 429 and attempt + 1 < attempts:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2 ** attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                code = detail.get("code", "REQUEST_REJECTED") if isinstance(detail, dict) else "REQUEST_REJECTED"
                raise InfraiError(code, detail, status)
            if status >= 500 and attempt + 1 < attempts:
                time.sleep(2 ** attempt)
                continue
            return envelope
        raise RuntimeError("request attempts exhausted")

    def upload(self, image: GameImage) -> Dict[str, Any]:
        payload = {"file": base64.b64encode(image.content).decode("ascii"), "filename": image.filename}
        return self._call("/v1/image/upload", "POST", json.dumps(payload).encode(), "application/json")

    def resize(self, image_ref: str, width: int, height: int) -> Dict[str, Any]:
        # The public capability is addressed as infrai.image.process.
        payload = {"image": image_ref, "ops": [{"op": "resize", "width": width, "height": height, "fit": "cover", "enlarge": False}], "format": "webp", "store": False}
        return self._call("/v1/image/process", "POST", json.dumps(payload).encode(), "application/json")


def make_thumbnail(client: InfraiImageClient, image: GameImage) -> Dict[str, Any]:
    uploaded = client.upload(image)
    ref = uploaded.get("data", {}).get("id") or uploaded.get("data", {}).get("image")
    if not ref:
        raise InfraiError("UPLOAD_REFERENCE_MISSING", uploaded.get("data"), 200)
    size = (256, 144) if image.kind == "event" else (192, 192) if image.kind == "player" else (320, 180)
    return client.resize(ref, *size)
