import xml.dom.minidom as md
from re import sub
from pathlib import Path
import copy

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


def gen_filename(old_filename:Path)->str:
    new_filename=copy.copy(old_filename.stem)
    # new_filename=new_filename.split('__')[0]
    if 'raw' in new_filename:
        new_filename=new_filename.replace('raw','browse_raw')
    else:
        new_filename=new_filename.replace('_cal_','_browse_cal_')
    return new_filename

def updateXML(xml: md.Element, label: str, value: str | int | float, idx: int = 0) -> None:
    a = xml.getElementsByTagName(label)[idx]
    a.firstChild.nodeValue = value
    


def getFromXml(xml:md.Element, label, idx=0):
    a = xml.getElementsByTagName(label)[idx]
    return a.firstChild.nodeValue

def lidGenerator(old_lid: str , file_name: Path, calib:bool=False)-> str:
    parts = old_lid.split(':')
    if calib:
        parts[-2] = 'browse_calibrated'
    parts[-1] = file_name.stem.split('__')[0]
    newLid = ':'.join(parts)
    return newLid

def lidUpdate(tree, fileName, calib: bool = False):
    # conf.log.debug("LID update", verbosity=3)
    oldLid = getFromXml(tree, "logical_identifier")
    # parts = oldLid.split(':')
    # if calib:
    #     parts[-2] = 'data_calibrated'
    # parts[-1] = fileName.stem.split('__')[0]
    # newLid = ':'.join(parts)
    if not isinstance(fileName, Path):
        fileName=Path(fileName)
    newLid =lidGenerator(old_lid=oldLid,file_name=fileName, calib=calib)
    updateXML(tree, "logical_identifier", newLid)
    return newLid
    

def new_lvid(old:str, file_name: Path, file_version:str):
    parts=old.split('::')
    new_main=parts[0].split(':')
    if 'cal' in file_name.stem:
        new_main[-2]='data_calibrated'
    newLVID=f"{':'.join(new_main[0:-1])}:{file_name.stem.split('__')[0]}::{file_version}"
    return newLVID


def lvidUpdate(tree:str, file_name: Path, file_version:str):
    oldLVID = getFromXml(tree, "lidvid_reference")
    newLVID=new_lvid(oldLVID, file_name, file_version)
    updateXML(tree, "lidvid_reference", newLVID)
    
    pass

def pretty_print(dom):
    return '\n'.join([line for line in dom.toprettyxml(indent=' '*4).split('\n') if line.strip()])