"""
This module manages the settings for the app.
Change them in the app or directly in the settings.yaml file.
"""
import yaml
from dataclasses import dataclass, field

@dataclass
class Source:
    """Dataclass for source settings"""
    name: str
    enabled: bool
    api_url: str | None = None

    def __repr__(self) -> str:
        return f"{' [enabled]' if self.enabled else '[disabled]'} {self.name.replace('_',' ').capitalize()}"

    def __str__(self) -> str:
        return self.__repr__()

@dataclass
class Settings:
    """Dataclass holding the app settings"""

    file_path: str = "settings.yaml"
    user_email: str = "user@example.com"
    openalex_settings: dict = field(default_factory=dict, init=False)
    raw_settings: dict = field(default_factory=dict, init=False, repr=False)
    sources: list[Source] = field(default_factory=list, init=False)
    def __post_init__(self):
        self.load()
        if self.raw_settings:
            self.parse_settings()

    def load(self) -> None:
        """Load the settings from the settings.yaml file"""
        try:
            with open(self.file_path) as f:
                self.raw_settings = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            print(f"Error while loading settings from {self.file_path}: {e}")
            self.raw_settings = {}

    def parse_settings(self) -> None:
        """Parse the settings into the dataclass"""
        for source in self.raw_settings.get("sources", []):
            self.sources.append(Source(**source))
        self.sources = sorted(self.sources, key=lambda x: x.enabled, reverse=True)

        for key, value in self.raw_settings.items():
            if key == "sources":
                continue
            setattr(self, key, value)

    def __repr__(self) -> str:
        return f"""
Settings file: {self.file_path}
User email:    {self.user_email}
Sources:       {'\n               '.join(map(str, self.sources))}
        """

SETTINGS = Settings()
