from langchain.text_splitter import RecursiveCharacterTextSplitter, Language 

class PHPTextSplitter(RecursiveCharacterTextSplitter):
    """Attempts to split the text along PHP-formatted layout elements."""

    def __init__(self, **kwargs):
        """Initialize a PHPTextSplitter."""
        separators = self.get_separators_for_language(Language.PHP)
        super().__init__(separators=separators, **kwargs)

class CSharpTextSplitter(RecursiveCharacterTextSplitter):
    """Attempts to split the text along PHP-formatted layout elements."""

    def __init__(self, **kwargs):
        """Initialize a CSharpTextSplitter."""
        separators = self.get_separators_for_language(Language.CSHARP)
        super().__init__(separators=separators, **kwargs)

