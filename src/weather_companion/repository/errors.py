class RepositoryError(Exception):
    """
    Defines an exception that is raised when an error occurs in the Repository class.
    """

    def __init__(self, message):
        """
        Creates a new instance of the RepositoryError class.
        """
        super().__init__(message)
