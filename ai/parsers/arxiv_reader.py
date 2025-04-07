
def find_pattern(pattern, txt):
    j = 0
    max_j = len(txt)

    j_list = []

    while j >= 0 and j < max_j:
        j = txt.find(pattern, j)
        if j == -1:
            break
        j_list.append(j)
        j += 1
        
    return j_list


def split_tex(tex, pattern):
    
    sec_idx = find_pattern(pattern, tex)
    
    sec_idx.append(-1)
    
    sections = [
        tex[s:e]
        for s,e in zip(sec_idx[:-1], sec_idx[1:])
    ]

    sections_title = [
        sec[:sec.find("\n")] for sec in sections
    ]

    sections_nwords = [
        len(sec.split())
        for sec in sections
    ]
    
    return sections_title, sections_nwords, sections

class TexNode:
    _n_nodes = 0
    def __init__(self, title, nwords, content, is_root=False):
        self.title = title
        self.nwords = nwords
        self.content = content
        self.attributes = {
            "is_root": is_root,
            "id": TexNode._n_nodes
        }
        self.descendents = []
        TexNode._n_nodes += 1
        
    def add_attribute(self, attr_name, attr_val):
        self.attributes[attr_name] = attr_val
        
    
    def __str__(self):
        return "TexNode object: {}".format(self.title)
    
    def __repr__(self):
        return "TexNode object: {}".format(self.title)
                
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
            TexNode(title, nwords, content, is_root)
            for title, nwords, content in zip(titles_list, nwords_list, content_list)
        ]
    
class ArxivDoc:

    sec_pattern = r"\section"
    subsec_pattern = r"\subsection"
    
    def __init__(self, tex):
        sections_title, sections_nwords, sections_content = split_tex(tex, ArxivDoc.sec_pattern)
        
        self.sections = TexNode.from_lists(sections_title, sections_nwords, sections_content, is_root=True)

        for sec in self.sections:
            sections_title, sections_nwords, sections_content = split_tex(sec.content, ArxivDoc.subsec_pattern)
            if len(sections_title) > 0:
                sec.descendents = TexNode.from_lists(sections_title, sections_nwords, sections_content, is_root=False)
                
    
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
        return results
        