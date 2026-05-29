from abc import ABC, abstractmethod

class TafsirAdapter(ABC):
    @abstractmethod
    def fetch(self, surah: int, ayah: int) -> str | None:
        """Fetch the tafsir text for a specific surah and ayah."""
        pass

    @abstractmethod
    def search(self, query: str, surah_filter: list[int] | None = None, limit: int = 20) -> list[dict]:
        """Search the tafsir for a query and return a list of dicts: [{'surah': int, 'ayah': int, 'text': str}]."""
        pass
