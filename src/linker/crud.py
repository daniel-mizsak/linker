"""
Create, Read, Update, Delete operations for Link model.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from sqlmodel import Session, select

from linker.models import Click, Link


def create_link(session: Session, slug: str | None, target_url: str) -> Link:
    """Create a link with a slug that points to the target url.

    Args:
        session (Session): Database session.
        slug (str | None): Slug for the link. Randomly generated if not provided.
        target_url (str): Target url to link to.

    Returns:
        Link: The created link object.

    Raises:
        TargetUrlAlreadyExistsError: If the target url already exists in the database.
        NoAvailableSlugsError: If no unused slugs are available in the database.
        InvalidSlugError: If the slug is not valid.
        SlugAlreadyInUseError: If the slug is already in use.
    """
    statement = select(Link).where(Link.target_url == target_url).limit(1)
    existing_link = session.exec(statement).first()
    if existing_link is not None:
        msg = f"Link with target url '{target_url}' already exists under slug '{existing_link.slug}'"
        raise TargetUrlAlreadyExistsError(msg)

    if slug is None:
        statement = select(Link).where(Link.target_url.is_(None)).order_by(Link.id.asc()).limit(1)  # type: ignore[union-attr]
        link = session.exec(statement).first()
        if link is None:
            msg = "No unused slugs are available in the database"
            raise NoAvailableSlugsError(msg)
    else:
        statement = select(Link).where(Link.slug == slug).limit(1)
        link = session.exec(statement).first()
        if link is None:
            msg = f"Slug '{slug}' is not valid"
            raise InvalidSlugError(msg)
        if link.target_url is not None:
            msg = f"Slug '{slug}' is already in use for target url '{link.target_url}'"
            raise SlugAlreadyInUseError(msg)

    link.target_url = target_url
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def list_links(session: Session) -> list[Link]:
    """List all links that have a target url.

    Args:
        session (Session): Database session.

    Returns:
        list[Link]: List of links.
    """
    statement = select(Link).where(Link.target_url.is_not(None)).order_by(Link.id.asc())  # type: ignore[union-attr]
    return list(session.exec(statement).all())


def get_link(session: Session, slug: str) -> Link:
    """Get a link by its slug.

    Args:
        session (Session): Database session.
        slug (str): Slug of the link.

    Returns:
        Link: The link object.

    Raises:
        InvalidSlugError: If the slug is not valid.
        SlugNotInUseError: If the slug is not in use.
    """
    statement = select(Link).where(Link.slug == slug).limit(1)
    link = session.exec(statement).first()
    if link is None:
        msg = f"Slug '{slug}' is not valid"
        raise InvalidSlugError(msg)
    if link.target_url is None:
        msg = f"Slug '{slug}' is not in use"
        raise SlugNotInUseError(msg)
    return link


def update_link(session: Session, link: Link, target_url: str) -> Link:
    """Update the target url of a link.

    Args:
        session (Session): Database session.
        link (Link): Link object to update.
        target_url (str): Updated target url to link to.

    Returns:
        Link: The updated Link object.

    Raises:
        TargetUrlAlreadyExistsError: If the target url already exists in the database.
    """
    statement = select(Link).where(Link.target_url == target_url).limit(1)
    existing_link = session.exec(statement).first()
    if existing_link is not None:
        msg = f"Link with target url '{target_url}' already exists under slug '{existing_link.slug}'"
        raise TargetUrlAlreadyExistsError(msg)

    link.target_url = target_url
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def delete_link(session: Session, link: Link) -> None:
    """Delete a link by setting its target url to none and resetting clicks.

    Args:
        session (Session): Database session.
        link (Link): Link object to delete.
    """
    link.target_url = None
    for click in link.clicks:
        session.delete(click)
    session.add(link)
    session.commit()
    session.refresh(link)


def update_link_clicks(session: Session, link: Link, ip_address: str) -> None:
    """Update the clicks for a link.

    Args:
        session (Session): Database session.
        link (Link): Link object to increment clicks for.
        ip_address (str): The ip address of the client.
    """
    click = Click(ip_address=ip_address, link=link)
    session.add(click)
    session.commit()
    session.refresh(click)


def list_clicks(session: Session, link: Link) -> list[Click]:
    """List all clicks for a given link."""
    statement = select(Click).where(Click.link_id == link.id).order_by(Click.timestamp.desc())  # type: ignore[attr-defined]
    return list(session.exec(statement).all())


class LinkError(Exception):
    """Base exception for all link errors."""


class TargetUrlAlreadyExistsError(LinkError):
    """Raised when a target url already exists in the database."""


class NoAvailableSlugsError(LinkError):
    """Raised when no unused slugs are available in the database."""


class InvalidSlugError(LinkError):
    """Raised when a slug is not valid."""


class SlugAlreadyInUseError(LinkError):
    """Raised when a slug is already in use."""


class SlugNotInUseError(LinkError):
    """Raised when a slug is not in use."""
