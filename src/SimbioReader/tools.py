import xml.dom.minidom as md
from re import sub

def getValue(nodeList: md.Element, label: str) -> str:
    """Get the value from a tag
    
    Args:
        nodelist: The xml block to evaluate
    
    Returns:
         The value of the tag

    """
    # for item in nodeList:
    #     print(item)
    elem = nodeList.getElementsByTagName(label)
    return elem[0].firstChild.data
    # return item


def getElement(doc, label, el=0) -> md.Element:
    """Get a Block of a dom
    
    Args:
        doc (xml.dom): The full Object
        
        label (str): The name of the tag to extract
            
    Returns:
        (xml.dom) The node tree extracted
        
    Todo:
        * implement OnBoard processing class
    """
    elem = doc.getElementsByTagName(label)
    return elem[el]


def camel_case(text)-> str:
    """
    Converts a given string to camelCase.

    The function transforms a string by removing underscores or hyphens,
    capitalizing the first letter of each word except the first one,
    and then joining them together to form a camelCase string.

    Args:
        text (str): The input string, typically in snake_case or kebab-case.

    Returns:
        str: The converted string in camelCase.

    Example:
        >>> camel_case('hello_world')
        'helloWorld'
        >>> camel_case('hello-world')
        'helloWorld'
    """
    text = sub(r"(_|-)+", " ", text).title().replace(" ", "")
    return ''.join([text[0].lower(), text[1:]])


def snake_case(text)->str:
    """
    Converts a given string to snake_case.

    The function transforms a camelCase or PascalCase string to snake_case,
    replacing capital letters with underscores followed by the lowercase equivalent.

    Args:
        text (str): The input string, typically in camelCase or PascalCase.

    Returns:
        str: The converted string in snake_case.

    Example:
        >>> snake_case('helloWorld')
        'hello_world'
        >>> snake_case('HelloWorld')
        'hello_world'
    """
    return '_'.join(
        sub('([A-Z][a-z]+)', r' \1',
            sub('([A-Z]+)', r' \1',
                text.replace('-', ' '))).split()).lower()
