import base64
import os
import subprocess
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ENGINE_URL = os.getenv("VOICEVOX_ENGINE_URL", "http://voicevox-engine:50021")
TIMEOUT = httpx.Timeout(60.0, connect=10.0)

app = FastAPI(title="VOICEVOX Wrapper API")


class SynthesisRequest(BaseModel):
    speaker: int = Field(..., ge=0)
    text: str = Field(..., min_length=1)


class SynthesisResponse(BaseModel):
    base64_mp3: str


@app.on_event("startup")
async def startup_event() -> None:
    app.state.http_client = httpx.AsyncClient(base_url=ENGINE_URL, timeout=TIMEOUT)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    client: httpx.AsyncClient = app.state.http_client
    await client.aclose()


@app.get("/speakers")
async def get_speakers() -> Any:
    client: httpx.AsyncClient = app.state.http_client
    try:
        response = await client.get("/speakers")
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"VOICEVOX engine error: {exc}") from exc
    return response.json()


def wav_to_mp3_base64(wav_bytes: bytes) -> str:
    try:
        process = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-i", "pipe:0", "-codec:a", "libmp3lame", "-f", "mp3", "pipe:1"],
            input=wav_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise HTTPException(status_code=500, detail="Failed to convert audio to MP3") from exc

    return base64.b64encode(process.stdout).decode("ascii")


@app.post("/synthesize", response_model=SynthesisResponse)
async def synthesize(request: SynthesisRequest) -> SynthesisResponse:
    client: httpx.AsyncClient = app.state.http_client

    try:
        audio_query_response = await client.post(
            "/audio_query",
            params={"text": request.text, "speaker": request.speaker},
        )
        audio_query_response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"VOICEVOX engine error during audio_query: {exc}") from exc

    try:
        synthesis_response = await client.post(
            "/synthesis",
            params={"speaker": request.speaker},
            json=audio_query_response.json(),
        )
        synthesis_response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"VOICEVOX engine error during synthesis: {exc}") from exc

    base64_mp3 = wav_to_mp3_base64(synthesis_response.content)
    return SynthesisResponse(base64_mp3=base64_mp3)

