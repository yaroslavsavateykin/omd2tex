import re
from typing import Any, Callable, List, Union


def remove_elements(lst: List[Any], elem: Any) -> List[Any]:
    """Remove all occurrences of a value from a list.

    Args:
        lst: List to filter.
        elem: Element to remove wherever it appears.

    Returns:
        New list without items equal to ``elem``.
    """
    return [item for item in lst if item != elem]


def return_func(string: Union[str, List[str]], elem: str, func: Callable[[str], str]) -> str:
    """Split a string by a delimiter and apply a function to alternating parts.

    Handles cases where the string begins with the delimiter differently from others, mirroring the original logic.

    Args:
        string: Source text to process.
        elem: Delimiter to split on.
        func: Callable applied to selected split segments.

    Returns:
        Recombined string after processing segments.
    """
    string = "".join(string).split(elem)  # .strip().split(elem)

    if string[0] == "":
        string = remove_elements(string, "")
        if len(string) == 1:
            N = 1
        else:
            N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i
            string[j] = func(string[j])

    else:
        string = remove_elements(string, "")
        N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i + 1
            string[j] = func(string[j])

    string = "".join(string)

    return string


def return_regular(string: str, regular: str, function: Callable[[str], str]) -> str:
    """Split a string by regex groups and apply a function to alternating parts.

    Mirrors the behavior of ``return_func`` but splits using a regular expression pattern.

    Args:
        string: Source text to process.
        regular: Regular expression pattern defining split groups.
        function: Callable applied to selected segments after splitting.

    Returns:
        Reconstructed string after applying the transformation.
    """
    string = re.split(regular, string)

    if string[0] == "":
        string = remove_elements(string, "")
        if len(string) == 1:
            N = 1
        else:
            N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i
            # string[j] = "\\ul{" + string[j] + "}"
            string[j] = function(string[j])

    else:
        string = remove_elements(string, "")
        N = int(len(string) / 2)
        for i in range(N):
            j = 2 * i + 1
            string[j] = function(string[j])
            # string[j] = "\\ul{" + string[j] + "}"

    string = "".join(string)

    return string
