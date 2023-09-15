import xml.dom.minidom as md

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
