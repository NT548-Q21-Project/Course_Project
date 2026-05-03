import httpx
from fastapi import HTTPException, status

from app.core.config import settings


async def call_llm(prompt: str) -> str:
    if not settings.LLM_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="LLM_API_KEY is not configured",
        )

    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an AI recruitment assistant. "
                    "You evaluate CV-job matching results. "
                    "You must return only valid JSON. "
                    "Do not return markdown."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.2,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            response = await client.post(
                url,
                headers=headers,
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    except httpx.TimeoutException as err:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM request timed out",
        ) from err

    except httpx.HTTPStatusError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM provider returned error: {err.response.status_code}",
        ) from err

    except KeyError as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid LLM provider response format",
        ) from err

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to call LLM provider",
        ) from err
