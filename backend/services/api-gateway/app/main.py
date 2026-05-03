import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from app.core.config import settings
from app.security import decode_access_token, get_bearer_token

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}

HTTP_METHODS: tuple[str, ...] = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")


def _build_forward_headers(request: Request, claims=None) -> dict[str, str]:
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }

    if claims is not None:
        headers.update(
            {
                "X-User-Id": str(claims.user_id),
                "X-Auth-Id": str(claims.auth_id),
                "X-User-Email": claims.email,
                "X-User-Role": claims.role,
            }
        )

    return headers


async def _proxy_request(
    request: Request,
    upstream_base_url: str,
    path: str,
    require_auth: bool = False,
) -> Response:
    claims = None
    if require_auth:
        token = get_bearer_token(request)
        claims = decode_access_token(token)

    body = await request.body()
    query_string = request.url.query
    target_url = f"{upstream_base_url.rstrip('/')}/{path.lstrip('/')}"
    if not path:
        target_url = upstream_base_url.rstrip("/")

    async with httpx.AsyncClient(timeout=60.0) as client:
        upstream_response = await client.request(
            request.method,
            target_url,
            params=query_string,
            content=body,
            headers=_build_forward_headers(request, claims),
        )

    response_headers = {
        key: value
        for key, value in upstream_response.headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
        media_type=upstream_response.headers.get("content-type"),
    )


@app.get("/health")
def health_check():
    return {"service": "api-gateway", "status": "ok"}


@app.api_route("/api/auth", methods=list(HTTP_METHODS))
@app.api_route("/api/auth/{path:path}", methods=list(HTTP_METHODS))
async def proxy_auth(request: Request, path: str = ""):
    new_path = f"auth/{path}" if path else "auth"
    return await _proxy_request(request, settings.IDENTITY_SERVICE_URL, new_path)


@app.api_route("/api/recruitment", methods=list(HTTP_METHODS))
@app.api_route("/api/recruitment/{path:path}", methods=list(HTTP_METHODS))
async def proxy_recruitment(request: Request, path: str = ""):
    new_path = f"recruitment/{path}" if path else "recruitment"
    return await _proxy_request(
        request,
        settings.RECRUITMENT_SERVICE_URL,
        new_path,
        require_auth=True,
    )


@app.api_route("/api/ai", methods=list(HTTP_METHODS))
@app.api_route("/api/ai/{path:path}", methods=list(HTTP_METHODS))
async def proxy_ai(request: Request, path: str = ""):
    new_path = f"ai/{path}" if path else "ai"
    return await _proxy_request(
        request,
        settings.AI_SERVICE_URL,
        new_path,
        require_auth=True,
    )
