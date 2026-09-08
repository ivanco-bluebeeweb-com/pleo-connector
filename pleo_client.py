"""Official Pleo Open API v1 client aligned with openapi.pleo.io."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_PLEO_BASE = "https://openapi.pleo.io/v1"

class PleoClient:
    def __init__(self, api_key: str, base_url: str = ""):
        self.api_key = api_key.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_PLEO_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Pleo/0.1.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _sanitize_msg(self, msg: str) -> str:
        if not msg:
            return ""
        if self.api_key and len(self.api_key) > 6:
            msg = msg.replace(self.api_key, self.api_key[:3] + "..." + self.api_key[-3:])
        return msg

    def _classify_error(self, resp: httpx.Response, action_name: str) -> dict[str, Any]:
        status = resp.status_code
        err_msg = ""
        try:
            data = resp.json()
            if "errors" in data and isinstance(data["errors"], list) and len(data["errors"]) > 0:
                err_msg = "; ".join(e.get("message", "") for e in data["errors"])
            elif "message" in data:
                err_msg = data["message"]
            elif "error" in data:
                err_msg = str(data["error"])
        except Exception:
            err_msg = resp.text[:200]
        err_msg = self._sanitize_msg(err_msg)

        if status == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            return {
                "status": "error",
                "code": "RATE_LIMITED",
                "message": f"Pleo API rate limit reached during {action_name}. Retry after {retry_after}s: {err_msg}"
            }
        elif status == 401:
            return {
                "status": "error",
                "code": "UNAUTHORIZED",
                "message": f"Invalid or expired Pleo API key during {action_name}: {err_msg}"
            }
        elif status == 403:
            return {
                "status": "error",
                "code": "FORBIDDEN",
                "message": f"Permission denied for {action_name} in Pleo: {err_msg}"
            }
        return {
            "status": "error",
            "code": f"HTTP_{status}",
            "message": f"Pleo API error {status} during {action_name}: {err_msg}"
        }

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/expenses", headers=self.headers, params={"limit": 1})
                if resp.status_code in (200, 201):
                    return {"status": "ok", "verified": True}
                return self._classify_error(resp, "verify_auth")
            except Exception as e:
                return {"status": "error", "code": "CONNECTION_FAILED", "message": self._sanitize_msg(str(e))}

    async def list_expenses(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                params = {"limit": limit}
                if cursor:
                    params["cursor"] = cursor
                resp = await client.get(f"{self.base_url}/expenses", headers=self.headers, params=params)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "list_expenses")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_expense(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/expenses/{item_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "get_expense")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_expense(self, payload: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if payload is None: payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/expenses", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "create_expense")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_expense(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/expenses/{item_id}", headers=self.headers, json=payload)
                if resp.status_code in (200, 204):
                    return resp.json() if resp.text else {"id": item_id, "updated": True}
                return self._classify_error(resp, "update_expense")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_expense(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/expenses/{item_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"id": item_id, "deleted": True}
                return self._classify_error(resp, "delete_expense")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_cards(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                params = {"limit": limit}
                if cursor:
                    params["cursor"] = cursor
                resp = await client.get(f"{self.base_url}/cards", headers=self.headers, params=params)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "list_cards")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_card(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/cards/{item_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "get_card")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_card(self, payload: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if payload is None: payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/cards", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "create_card")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_card(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/cards/{item_id}", headers=self.headers, json=payload)
                if resp.status_code in (200, 204):
                    return resp.json() if resp.text else {"id": item_id, "updated": True}
                return self._classify_error(resp, "update_card")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_card(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/cards/{item_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"id": item_id, "deleted": True}
                return self._classify_error(resp, "delete_card")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_reports(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                params = {"limit": limit}
                if cursor:
                    params["cursor"] = cursor
                resp = await client.get(f"{self.base_url}/reports", headers=self.headers, params=params)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "list_reports")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_report(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/reports/{item_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "get_report")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_report(self, payload: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if payload is None: payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/reports", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "create_report")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_report(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/reports/{item_id}", headers=self.headers, json=payload)
                if resp.status_code in (200, 204):
                    return resp.json() if resp.text else {"id": item_id, "updated": True}
                return self._classify_error(resp, "update_report")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_report(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/reports/{item_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"id": item_id, "deleted": True}
                return self._classify_error(resp, "delete_report")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_policies(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/policies", headers=self.headers, params={"limit": limit, "cursor": cursor})
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "list_policies")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_policy(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/policies/{item_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "get_policy")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_policy(self, payload: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if payload is None: payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/policies", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "create_policy")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_policy(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/policies/{item_id}", headers=self.headers, json=payload)
                if resp.status_code in (200, 204):
                    return resp.json() if resp.text else {"id": item_id, "updated": True}
                return self._classify_error(resp, "update_policy")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_policy(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/policies/{item_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"id": item_id, "deleted": True}
                return self._classify_error(resp, "delete_policy")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_merchants(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/merchants", headers=self.headers, params={"limit": limit, "cursor": cursor})
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "list_merchants")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_merchant(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/merchants/{item_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "get_merchant")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_merchant(self, payload: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if payload is None: payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/merchants", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "create_merchant")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_merchant(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/merchants/{item_id}", headers=self.headers, json=payload)
                if resp.status_code in (200, 204):
                    return resp.json() if resp.text else {"id": item_id, "updated": True}
                return self._classify_error(resp, "update_merchant")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_merchant(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/merchants/{item_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"id": item_id, "deleted": True}
                return self._classify_error(resp, "delete_merchant")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def list_reimbursements(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/reimbursements", headers=self.headers, params={"limit": limit, "cursor": cursor})
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "list_reimbursements")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def get_reimbursement(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/reimbursements/{item_id}", headers=self.headers)
                if resp.status_code == 200:
                    return resp.json()
                return self._classify_error(resp, "get_reimbursement")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def create_reimbursement(self, payload: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if payload is None: payload = {"name": name, **(details or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/reimbursements", headers=self.headers, json=payload)
                if resp.status_code in (200, 201):
                    return resp.json()
                return self._classify_error(resp, "create_reimbursement")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def update_reimbursement(self, item_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.patch(f"{self.base_url}/reimbursements/{item_id}", headers=self.headers, json=payload)
                if resp.status_code in (200, 204):
                    return resp.json() if resp.text else {"id": item_id, "updated": True}
                return self._classify_error(resp, "update_reimbursement")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}

    async def delete_reimbursement(self, item_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.delete(f"{self.base_url}/reimbursements/{item_id}", headers=self.headers)
                if resp.status_code in (200, 204):
                    return {"id": item_id, "deleted": True}
                return self._classify_error(resp, "delete_reimbursement")
            except Exception as e:
                return {"status": "error", "code": "NETWORK_ERROR", "message": self._sanitize_msg(str(e))}
