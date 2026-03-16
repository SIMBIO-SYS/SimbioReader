import xml.dom.minidom as md
from re import sub
from pathlib import Path
import copy

def getValue(nodeList: md.Document | md.Element, label: str) -> str:
    """Extracts and returns the text content of the first matching XML element.
    This function searches for an XML element with the specified tag name within
    a given node list and returns the text data of the first matching element's
    first child node.
    Args:
        nodeList (md.Document): The parent XML element to search within.
        label (str): The tag name of the XML element to retrieve.
    Returns:
        str: The text content of the first matching element's first child node.
    Raises:
        IndexError: If no element with the specified label is found.
        AttributeError: If the found element has no firstChild or the firstChild
            has no data attribute.
    Example:
        >>> import xml.dom.minidom as md
        >>> xml_string = '<root><name>John Doe</name><age>30</age></root>'
        >>> doc = md.parseString(xml_string)
        >>> root = doc.documentElement
        >>> getValue(root, 'name')
        'John Doe'
        >>> getValue(root, 'age')
        '30'
    """
    
    elem = nodeList.getElementsByTagName(label)
    if not elem:
        raise IndexError(f"Tag '{label}' not found")

    node = elem[0]
    if node.firstChild is None:
        raise AttributeError(f"Tag '{label}' has no child nodes")

    value = node.firstChild.nodeValue
    if value is None:
        raise AttributeError(f"Tag '{label}' has no text value")

    return value
    


def getElement(doc: md.Document | md.Element, label: str, el: int = 0) -> md.Element:
    """Get a Block of a dom
    
    Args:
        doc (xml.dom): The full Object
        
        label (str): The name of the tag to extract
            
    Returns:
        (xml.dom) The node tree extracted
        
    Todo:
        * implement OnBoard processing class
    """
    if el < 0:
        raise IndexError("Element index cannot be negative")

    elem = doc.getElementsByTagName(label)
    if not elem:
        raise IndexError(f"Tag '{label}' not found")
    if el >= len(elem):
        raise IndexError(
            f"Tag '{label}' has {len(elem)} element(s), index {el} is out of range"
        )

    return elem[el]


def gen_filename(old_filename:Path)->Path:
    new_filename=copy.copy(old_filename.stem)
    # new_filename=new_filename.split('__')[0]
    if 'raw' in new_filename:
        new_filename=new_filename.replace('raw','browse_raw')
    else:
        new_filename=new_filename.replace('_cal_','_browse_cal_')
    return Path(new_filename)

def updateXML(xml: md.Element, label: str, value: str | int | float, idx: int = 0) -> None:
    a = xml.getElementsByTagName(label)[idx]
    child = a.firstChild
    if child is None:
        raise AttributeError(f"Tag '{label}' has no child nodes")
    if not isinstance(child, md.Text):
        raise TypeError(f"Tag '{label}' first child is not a text node")
    child.data = str(value)
    


def getFromXml(xml: md.Element, label: str, idx: int = 0) -> str:
    a = xml.getElementsByTagName(label)[idx]
    child = a.firstChild
    if child is None:
        raise AttributeError(f"Tag '{label}' has no child nodes")
    if not isinstance(child, md.Text):
        raise TypeError(f"Tag '{label}' first child is not a text node")
    return child.data

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


def lvidUpdate(
    tree: md.Document | md.Element, file_name: Path, file_version: str
) -> str:
    oldLVID = getFromXml(tree, "lidvid_reference")
    newLVID = new_lvid(oldLVID, file_name, file_version)
    updateXML(tree, "lidvid_reference", newLVID)
    return newLVID

def pretty_print(dom):
    return '\n'.join([line for line in dom.toprettyxml(indent=' '*4).split('\n') if line.strip()])
