"""
Definition of the JournalRepository interface 
In Memory implementation of the journal repository.
"""


from typing import List, Tuple

from weather_companion import weather_journal


class RepositoryError(Exception):
    """
    Defines an exception that is raised when an error occurs in the Repository class.
    """

    def __init__(self, message):
        """
        Creates a new instance of the RepositoryError class.
        """
        super().__init__(message)


class JournalRepository:
    """Interface for a journal repository"""

    def add(
        self, entry: weather_journal.JournalEntry, author_id: weather_journal.AuthorID
    ) -> int:
        pass

    def get(
        self, entry_id: int, author_id: weather_journal.AuthorID
    ) -> weather_journal.JournalEntry:
        pass

    def update(
        self,
        entry_id: int,
        author_id: weather_journal.AuthorID,
        new_journal_entry: weather_journal.JournalEntry,
    ) -> None:
        pass

    def remove(self, entry_id: int, author_id: weather_journal.AuthorID) -> None:
        pass

    def get_all_entries(
        self, author_id: weather_journal.AuthorID
    ) -> List[Tuple[int, weather_journal.JournalEntry]]:
        pass


class InMemoryJournalRepository(JournalRepository):
    def __init__(self):
        self._container = []

    def add(
        self, entry: weather_journal.JournalEntry, author_id: weather_journal.AuthorID
    ) -> int:
        """
        Adds the entry to the container and returns the unique assigned id
        """
        max_id = max([entry[0] for entry in self._container] + [-1])
        self._container.append([max_id + 1, entry, author_id])
        return max_id + 1

    def get(
        self, entry_id: int, author_id: weather_journal.AuthorID
    ) -> weather_journal.JournalEntry:
        """
        Gets the entry with the given id from the container
        Throws RepositoryError if value not found
        """
        for entry in self._container:
            if entry[0] == entry_id and entry[2] == author_id:
                return entry[1]
        raise RepositoryError("Journal entry not found")

    def remove(self, entry_id: int, author_id: weather_journal.AuthorID) -> None:
        """
        Removes the entry with the given id from the container
        Throws RepositoryError if value not found
        """
        for entry in self._container:
            if entry[0] == entry_id and entry[2] == author_id:
                self._container.remove(entry)
                return
        raise RepositoryError("Journal entry not found")

    def update(
        self,
        entry_id: int,
        author_id: weather_journal.AuthorID,
        new_journal_entry: weather_journal.JournalEntry,
    ) -> None:
        """
        Updates the entry with the fiven id for an author
        Throws RepositoryError if value not found
        """
        for entry in self._container:
            if entry[0] == entry_id and entry[2] == author_id:
                entry[1] = new_journal_entry
                return
        raise RepositoryError("Journal entry not found")

    def get_all_entries(
        self, author_id: weather_journal.AuthorID
    ) -> List[Tuple[int, weather_journal.JournalEntry]]:
        """
        Gets the entire journal for an author
        """
        journal = []
        for entry in self._container:
            if entry[2] == author_id:
                journal.append((entry[0], entry[1]))
        return journal
