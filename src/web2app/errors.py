class TitleNotFound(Exception):
    """
    Exception for when the `<title`> element is not found in a page.
    """
    pass

class FaviconNotFound(Exception):
    """
    Exception for when the favicon is not found in a page.
    """
    pass