"""
Data structure schemas.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


# TODO: Change the target_url to be BASE64 encoded so GET requests can send the url without issues.
class Link(SQLModel, table=True):
    """Link model saved in the database."""

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    target_url: str | None = Field(index=True)
    clicks: list["Click"] = Relationship(back_populates="link")


class LinkCreate(SQLModel):
    """Data model for creating a link."""

    slug: str | None = None
    target_url: str


class LinkRead(SQLModel):
    """Data model for reading a link."""

    slug: str
    target_url: str | None
    clicks: int

    @classmethod
    def from_link(cls, link: Link) -> "LinkRead":
        """Create a LinkRead instance from a Link instance."""
        return cls(
            slug=link.slug,
            target_url=link.target_url,
            clicks=len(link.clicks),
        )


class LinkUpdate(SQLModel):
    """Data model for updating a link."""

    target_url: str


class Click(SQLModel, table=True):
    """Click model saved in the database."""

    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    ip_address: str

    link_id: int = Field(foreign_key="link.id", index=True)
    link: Link = Relationship(back_populates="clicks")


class ClickRead(SQLModel):
    """Data model for reading a click."""

    timestamp: datetime
    ip_address: str

    @classmethod
    def from_click(cls, click: Click) -> "ClickRead":
        """Create a ClickRead instance from a Click instance."""
        return cls(
            timestamp=click.timestamp,
            ip_address=click.ip_address,
        )
