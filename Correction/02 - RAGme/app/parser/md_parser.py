from markdown import markdown


class MdParser:
    """Parse text from Markdown"""

    @staticmethod
    def to_html(text: str) -> str:
        """
        Convert Markdown to HTML

        Args:
            text (str): MD formatted string to parse

        Returns:
            str: Converted HTML content
        """
        return markdown(text, extensions=['fenced_code'])
