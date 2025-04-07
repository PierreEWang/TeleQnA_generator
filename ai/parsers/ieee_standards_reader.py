import re
import numpy as np 

def sanitize_title(title):
    pattern = r'\t\s+(.*?)$'
    replacement = r'\t\1'
    title = re.sub(pattern, replacement, title)
    
    pattern = r'(\t\d+)?$'
    title = re.sub(pattern, '', title)
    return title

def find_sections(paragraphs):
    pattern = r'^\d+(.)?\t\s?[aA-zZ][^\t]+'
    return [sanitize_title(p) for p in paragraphs if len(re.findall(pattern, p))>0 and not p.isnumeric()]

def find_subsections(paragraphs):
    pattern = r'^\t?\d+.\d+\t?\s?[aA-zZ][^\t]+'
    return [sanitize_title(p) for p in paragraphs if len(re.findall(pattern, p))>0 and not p.isnumeric()]

def get_content(paragraphs, sections_titles):
    sections_content = {}
    current_section = None

    next_section = sections_titles[0]
    sec_idx = -1
    
    while next_section != "-- FINISHED --":
        sec_idx += 1
        for p in paragraphs:
            if sec_idx < len(sections_titles):
                next_section = sections_titles[sec_idx]
            else:
                next_section = "-- FINISHED --"
                
            if next_section in p:
                sec_idx += 1
                current_section = next_section
                sections_content[current_section] = []
        
            if current_section is not None:
                sections_content[current_section] += [p]

    return sections_content

def remove_last_dots(string):
    # Use regular expressions to remove the last repetition of dots
    modified_string = re.sub(r'\.+$', '', string)

    return modified_string.strip()

def split_tex(paragraphs):
    
    sections = []
    sections_title = []
    sections_nwords = []
    
    start_t_o_c = "Content"
    table_of_content_start = np.where([
        start_t_o_c in p
        for p in paragraphs
    ])[0][0]
    
    _start_doc_pattern_1 = "Foreword"
    _start_doc_pattern_2 = "Annex"
    content_start_list = np.where([
        (_start_doc_pattern_1 in p) or (_start_doc_pattern_2 in p)
        for p in paragraphs
    ])[0]
    content_start = [_idx for _idx in content_start_list if _idx > table_of_content_start + 5][0]
    
    
    subsections_titles = find_subsections(paragraphs[table_of_content_start:content_start])
    subsections_titles = [remove_last_dots(title) for title in subsections_titles]
    
    sections_titles = find_sections(paragraphs[table_of_content_start:content_start])
    sections_titles = [remove_last_dots(title) for title in sections_titles if title not in subsections_titles]
    
    content = get_content(paragraphs[content_start:], sections_titles)

    for sec in content:
        sec_text = "\n".join(content[sec])
        n_words = len(sec_text.split())
        if n_words > 6000:
            sec_number = sec[:sec.find("\t")]
            pattern = r"^[{}].".format(sec_number)
            sub_titles = [s for s in subsections_titles if len(re.findall(pattern, s))]
            
            print(pattern)
            print(sub_titles)
            
            sub_content = get_content(content[sec], sub_titles)
    
            for sub_s in sub_content:
                sub_text = "\n".join(sub_content[sub_s])
                n_words = len(sub_text.split())
                if n_words > 5000:
                    sub_text = " ".join(sub_text.split()[:5000])
                    n_words = len(sub_text.split())
                
                sections_title += [sec + " / " + sub_s]
                sections_nwords += [n_words]
                sections += [sub_text]
        else:
            sections_title += [sec]
            sections_nwords += [n_words]
            sections += [sec_text]
    
    return sections_title, sections_nwords, sections

class DocxNode:
    _n_nodes = 0
    def __init__(self, title, nwords, content, is_root=False):
        self.title = title
        self.nwords = nwords
        self.content = content
        self.attributes = {
            "is_root": is_root,
            "id": DocxNode._n_nodes
        }
        self.descendents = []
        DocxNode._n_nodes += 1
        
    def add_attribute(self, attr_name, attr_val):
        self.attributes[attr_name] = attr_val
        
    
    def __str__(self):
        return "DocxNode object: {}".format(self.title)
    
    def __repr__(self):
        return "DocxNode object: {}".format(self.title)
                
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
            DocxNode(title, nwords, content, is_root)
            for title, nwords, content in zip(titles_list, nwords_list, content_list)
        ]
    
class StandardsDoc:
    
    def __init__(self, paragraphs):
        sections_title, sections_nwords, sections_content = split_tex(paragraphs)   
        self.sections = DocxNode.from_lists(sections_title, sections_nwords, sections_content, is_root=True)

    
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
        