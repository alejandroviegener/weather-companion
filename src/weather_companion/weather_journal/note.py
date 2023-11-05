class Note:
    MAX_LENGTH = 1000

    def __init__(self, content: str):
        """
        Create a Note, content must be:
          - a non empty string
          - alphanumeric only
          - less than 1000 characters
        """
        self._content = self._validate_content(content)

    def content(self) -> str:
        return self._content

    def _validate_content(self, content: str) -> str:
        """
        check if content is valid: less than 1000 characters, alphanumeric only
        """
        content = content.strip()
        if not content:
            raise ValueError("The content cannot be empty.")
        if len(content) > Note.MAX_LENGTH:
            raise ValueError("The content cannot be longer than 1000 characters.")

        return content

    def __eq__(self, __value: object) -> bool:
        return self._content == __value._content
