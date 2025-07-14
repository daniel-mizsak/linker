"""
Main application.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import validators
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from linker.constants import LINKER_TOKEN_KEY
from linker.crud import (
    InvalidSlugError,
    NoAvailableSlugsError,
    SlugAlreadyInUseError,
    SlugNotInUseError,
    TargetUrlAlreadyExistsError,
    create_link,
    delete_link,
    get_link,
    list_clicks,
    list_links,
    update_link,
    update_link_clicks,
)
from linker.database import create_db, get_session
from linker.models import ClickRead, LinkCreate, LinkRead, LinkUpdate


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Create the database at startup."""
    create_db()
    yield


app = FastAPI(lifespan=lifespan)

security = HTTPBearer()


def get_linker_token() -> str:
    """Get linker token from environment variables."""
    linker_token = os.getenv(LINKER_TOKEN_KEY)
    if linker_token is None:
        msg = f"Environment variable '{LINKER_TOKEN_KEY}' is not set"
        raise RuntimeError(msg)
    return linker_token


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
    linker_token: str = Depends(get_linker_token),
) -> None:
    """Verify the provided token."""
    if credentials.credentials != linker_token:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/", include_in_schema=False)
def forward_to_docs() -> RedirectResponse:
    """Redirect to the api documentation."""
    return RedirectResponse(url="/docs", status_code=307)


@app.post("/api/v1/links", dependencies=[Depends(verify_token)])
def create_link_endpoint(link_create: LinkCreate, session: Annotated[Session, Depends(get_session)]) -> LinkRead:
    """Create a link with a slug that points to the target url."""
    if not validators.url(link_create.target_url):
        raise HTTPException(status_code=422, detail=f"The provided url '{link_create.target_url}' is not valid")
    try:
        link = create_link(session, link_create.slug, link_create.target_url)
    except (TargetUrlAlreadyExistsError, NoAvailableSlugsError, InvalidSlugError, SlugAlreadyInUseError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return LinkRead.from_link(link)


@app.get("/api/v1/links", dependencies=[Depends(verify_token)])
def list_links_endpoint(session: Annotated[Session, Depends(get_session)]) -> list[LinkRead]:
    """List all links that have a target url."""
    links = list_links(session)
    return [LinkRead.from_link(link) for link in links]


@app.get("/api/v1/links/{slug}", dependencies=[Depends(verify_token)])
def get_link_endpoint(slug: str, session: Annotated[Session, Depends(get_session)]) -> LinkRead:
    """Get a link by its slug."""
    try:
        link = get_link(session, slug)
    except (InvalidSlugError, SlugNotInUseError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return LinkRead.from_link(link)


@app.patch("/api/v1/links/{slug}", dependencies=[Depends(verify_token)])
def update_link_endpoint(
    slug: str,
    link_update: LinkUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> LinkRead:
    """Update the target url of a link."""
    if not validators.url(link_update.target_url):
        raise HTTPException(status_code=422, detail=f"The provided url '{link_update.target_url}' is not valid")
    try:
        link = get_link(session, slug)
    except (InvalidSlugError, SlugNotInUseError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    try:
        link = update_link(session, link, link_update.target_url)
    except TargetUrlAlreadyExistsError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return LinkRead.from_link(link)


@app.delete("/api/v1/links/{slug}", dependencies=[Depends(verify_token)])
def delete_link_endpoint(slug: str, session: Annotated[Session, Depends(get_session)]) -> Response:
    """Delete a link by setting its target url to none and resetting clicks."""
    try:
        link = get_link(session, slug)
    except (InvalidSlugError, SlugNotInUseError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    delete_link(session, link)
    return Response(status_code=204)


@app.get("/{slug}")
def forward_to_target_url(
    slug: str,
    session: Annotated[Session, Depends(get_session)],
    request: Request,
) -> RedirectResponse:
    """Redirect to the target url of the link with the given slug."""
    try:
        link = get_link(session, slug)
    except (InvalidSlugError, SlugNotInUseError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    ip_address = request.client.host if request.client is not None else "unknown"
    update_link_clicks(session, link, ip_address)
    return RedirectResponse(url=str(link.target_url), status_code=307)


@app.get("/api/v1/links/{slug}/clicks", dependencies=[Depends(verify_token)])
def list_clicks_endpoint(slug: str, session: Annotated[Session, Depends(get_session)]) -> list[ClickRead]:
    """List all clicks for a given link."""
    try:
        link = get_link(session, slug)
    except (InvalidSlugError, SlugNotInUseError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return [ClickRead.from_click(click) for click in list_clicks(session, link)]
