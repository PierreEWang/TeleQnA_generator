import re
import numpy as np 
import PyPDF2
from tqdm import tqdm


def split_tex(pypdf_obj, n_pages_per_sec=3):
    
    sections = []
    sections_title = []
    sections_nwords = []

    for k in tqdm(range((len(pypdf_obj.pages)-1)//n_pages_per_sec + 1)):
        start_pages = k*n_pages_per_sec
        end_pages = np.minimum((k+1)*n_pages_per_sec, len(pypdf_obj.pages))
        content = ""
        for i in range(start_pages, end_pages):
            content += pypdf_obj.pages[i].extract_text()
            content += " \n "

        sections_title += ["Section {}:".format(k)]
        sections_nwords += [len(content.split())]
        sections += [content]

    return sections_title, sections_nwords, sections


class PDFNode:
    _n_nodes = 0
    def __init__(self, title, nwords, content, is_root=False):
        self.title = title
        self.nwords = nwords
        self.content = content
        self.attributes = {
            "is_root": is_root,
            "id": PDFNode._n_nodes
        }
        self.descendents = []
        PDFNode._n_nodes += 1
        
    def add_attribute(self, attr_name, attr_val):
        self.attributes[attr_name] = attr_val
        
    
    def __str__(self):
        return "PDFNode object: {}".format(self.title)
    
    def __repr__(self):
        return "PDFNode object: {}".format(self.title)
                
    def apply(self, func, ind=0, reccursive=True):
        func(self, ind)
        if reccursive:
            for desc in self.descendents:
                desc.apply(func, ind+1, reccursive=True)
                
    def show(self, ind=0, show_structure=False):
        func = lambda _node, _ind: print("\t"*_ind + _node.title)
        self.apply(func, ind, reccursive=show_structure)
    
    @classmethod
    def from_lists(cls, titles_list, nwords_list, content_list, is_root=False):
        return [
            PDFNode(title, nwords, content, is_root)
            for title, nwords, content in zip(titles_list, nwords_list, content_list)
        ]
    
class PDFDoc:
    
    def __init__(self, pypdf_obj):
        sections_title, sections_nwords, sections_content = split_tex(pypdf_obj)   
        self.sections = PDFNode.from_lists(sections_title, sections_nwords, sections_content, is_root=True)

    
    def show(self, show_structure=True):
        for sec in self.sections:
            sec.show(ind=0, show_structure=show_structure)
            print()
            
    def apply(self, func, func_between=None, reccursive=True):
        for sec in self.sections:
            sec.apply(func, ind=0, reccursive=reccursive)
            if not func_between is None:
                func_between(sec)
                
    def _find_func(self, func):
        _results = []
        def _find(_node, _ind):
            if func(_node):
                _results.append(_node)
        self.apply(_find, reccursive=True)
        return _results
    
    def find(self, node_title):
        results = self._find_func(lambda _node: node_title in _node.title) 