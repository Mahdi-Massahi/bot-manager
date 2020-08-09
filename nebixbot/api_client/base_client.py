class BaseClient:
    """Gives the common functionality for inherited clients"""

    def __init__(self, name, version):
        """Initializes BaseClient"""
        self.name = name
        self.version = version
