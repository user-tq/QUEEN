import os 
import re
import sys 
from graphviz import Digraph
sys.path.append("/".join(__file__.split("/")[:-1]))
from qfunction import *

def traceflow(*dnas, operational_function_only=True):
    dnatree_dict = {}   
    histories        = quine(*dnas, _return=True) 
    new_histories    = [] 
    name_dict        = {} 
    unique_name_dict = {}
    unique_name_name_dict = {} 
    for history in histories:
        info = history[2] 
        history = history[1]
        match0  = re.search("(QUEEN.queried_features_dict\['[^\[\]]+'\]) = (.*)",history)
        match1  = re.search("(.*QUEEN.dna_dict\['[^\[\]]+'\]) = ", history)
        match2  = re.search("product='([^=]+)'[,\)]", history)
        if match1 is not None: 
            match3 = list(re.finditer("QUEEN.dna_dict\['([^\[\]]+)'\]", match1.group(1))) 
            if match2 is not None:
                name = match2.group(1)
                if "," not in name and len(match3) > 1:
                    for m, match in enumerate(match3):
                        name_dict[match.group(0)] = match2.group(1)  + "[{}]".format(m) 
                else:
                    for aname, match in zip(name.split(","), match3):
                        name_dict[match.group(0)] = name 
            else:
                for m, match in enumerate(match3): 
                    name_dict[match.group(0)] = match.group(1) 

            for m, match in enumerate(match3): 
                unique_name_dict[match.group(0)] = match.group(1) 
                unique_name_name_dict[match.group(1)] = name_dict[match.group(0)] 
            new_histories.append([history, info]) 
        
        elif operational_function_only==False and match0 is not None:
            match3 = re.search("QUEEN.queried_features_dict\['([^\[\]]+)'\]", match0.group(1))
            if match2 is not None:
                name_dict[match3.group(0)] = match2.group(1) 
            else:
                name_dict[match3.group(0)] = match3.group(1) 

            unique_name_dict[match3.group(0)] = match3.group(1) 
            unique_name_name_dict[match3.group(1)] = name_dict[match3.group(0)] 
            new_histories.append([history, info]) 
        else:
            pass 

    nodes = set([])  
    dg = Digraph(name="cluster_operation")
    dg.attr(rankdir='LR')
    dg.attr(fontname="arial") 
    dg.attr(nodesep="0.1")
    dg.attr(ranksep="0.1")
    
    if operational_function_only==False:
        sdg = Digraph(name="cluster_search")
        sdg.attr(rankdir='LR')
        sdg.attr(fontname="arial") 
        sdg.attr(nodesep="0.1")
        sdg.attr(ranksep="0.1")
    
    product_funcname_dict = {} 
    for h, history in enumerate(new_histories):
        info    = history[1] 
        history = history[0]
        matcho = re.search("(.*QUEEN.dna_dict\['[^\[\]]+'\]) = (.*)", history) 
        matchs = re.search("(QUEEN.queried_features_dict\['[^\[\]]+'\]) = (.*)",history)
        sourcenames = []  
        if matcho is not None:
            source = matcho.group(2) 
        else:
            source = matchs.group(2)  
            
        for key in re.finditer("QUEEN.dna_dict\['([^\[\]]+)'\]", source):
            key = key.group(0)
            sourcename = unique_name_dict[key]
            sourcenames.append(sourcename) 
            if sourcename not in nodes:
                dg.node(sourcename, label=name_dict[key]) 
                nodes.add(sourcename) 
            else:
                pass

        if re.match("cutdna", source) is not None:
            funclabel = "cutdna"
            funcname  = "cutdna_{}".format(h)
        elif re.match("cropdna", source) is not None:
            funclabel = "cropdna"
            funcname  = "cropdna_{}".format(h)
        elif re.match("modifyends", source) is not None:
            funclabel = "modifyends"
            funcname  = "modifyends_{}".format(h)
        elif re.match("flipdna", source) is not None:
            funclabel = "flipdna"
            funcname  = "flipdna_{}".format(h)
        elif re.match("joindna", source) is not None:
            funclabel = "joindna"
            funcname  = "joindna_{}".format(h)
        elif re.match("editsequence", source) is not None:
            funclabel = "editsequence"
            funcname  = "editsequence_{}".format(h)
        elif re.search("searchsequence", source) is not None:
            funclabel = "searchsequence"
            funcname  = "searchsequence_{}".format(h)
        elif re.search("searchfeature", source) is not None:
            funclabel = "searchfeature"
            funcname  = "searchfeature_{}".format(h)
        else:
            funcname = None
        
        if matcho is not None:
            productnames = [] 
            product = matcho.group(1)
            for key in re.finditer("QUEEN.dna_dict\['([^\[\]]+)'\]", product):
                key = key.group(0) 
                productname = unique_name_dict[key]
                productnames.append(productname) 
                if productname not in nodes:
                    dg.node(productname, label=name_dict[key], margin="0.01", shape="oval", fontname="Arial") 
                    nodes.add(productname) 
                else:
                    pass
        
        else:
            productnames = [] 
            product = matchs.group(1)
            for key in re.finditer("QUEEN.queried_features_dict\['[^\[\]]+'\]", product):
                key = key.group(0) 
                productname = unique_name_dict[key]
                productnames.append(productname) 
                if productname not in nodes:
                    sdg.node(productname, label=name_dict[key], margin="0.01", shape="oval", fontname="Arial") 
                    nodes.add(productname) 
                else:
                    pass

        if funcname is None:
            pass 
        else:
            if funclabel == "searchsequence" or funclabel == "searchfeature":
                info      = info.split("; ")
                info_dict = dict([item.split(":") for item in info if ":" in item])
                temp = '<tr><td port="{}" border="1" align="left"><b> </b><i>{} </i> = {}</td></tr>'
                label="".join(['<<table border="0" cellborder="1" cellspacing="0" cellpadding="1">',
                      '<tr>',
                      '<td port="func" border="1" bgcolor="#909090"><font color="white" point-size="16"><b> </b>{}<b> </b></font></td>',
                      '</tr>',
                      '{}',
                      '</table>>'])
                infotext = ""
                
                query_flag      = 0 
                query_match     = re.search("query=([^=]+),", source)
                queryname_match = re.search("QUEEN.dna_dict\['([^\[\]]+)'\]", query_match.group(1))
                if queryname_match is not None:
                    queryname = queryname_match.group(1)
                    info_dict["query"] = query_match.group(1).replace(queryname_match.group(0), name_dict[queryname_match.group(0)])
                    query_flag = 1 
                    
                if info_dict is not None:
                    for key, value in info_dict.items():
                        infotext += temp.format(key, key, value)
                
                if sourcenames[0] + "_search" not in nodes:
                    sdg.node(sourcenames[0] + "_search", label=unique_name_name_dict[sourcenames[0]]) 
                    nodes.add(sourcenames[0] + "_search") 
                else:
                    pass
 
                sdg.node(funcname, label.format(funclabel, infotext), shape="plaintext", fontname="Arial")
                sdg.edge(sourcenames[0] + "_search", funcname+":func", arrowhead="dot")
                
                if query_flag == 1:
                    if queryname + "_search" not in nodes:
                        sdg.node(queryname + "_search", label=unique_name_name_dict[queryname]) 
                        nodes.add(queryname + "_search") 
                    else:
                        pass
                    sdg.edge(queryname + "_search", funcname+":query", arrowhead="dot")
                
                for product in productnames:
                    sdg.edge(funcname+":func", product)

                #for productname in productnames:
                #    product_funcname_dict[productname] = funcname 

            elif funclabel == "joindna":
                info      = info.split("; ")
                info_dict = dict([item.split(":") for item in info])
                temp = '<tr><td border="1" color="#909090" bgcolor="#909090" port="f{}"> </td></tr>'
                label="".join(['<<table border="0" cellborder="1" cellspacing="0" cellpadding="0">',
                      '<tr>',
                      '<td>',
                      '<table cellpadding="0" cellspacing="0" border="0">',
                      '<tr>',
                      '<td border="1" color="#909090" bgcolor="#909090" port="f0"> </td>',
                      '<td port="func" rowspan="{}" border="1" color="#909090" bgcolor="#909090" align="left"><font color="white" point-size="16">joindna</font><b> </b></td>',
                      '</tr>'
                      '{}',
                      '</table>'
                      '</td>'
                      '</tr>'
                      '<tr>',
                      '<td border="1" align="left" height="20"><b> </b><i>topology </i> = {}<b> </b></td>'
                      '</tr>',
                      '</table>>'])
                
                sourcelabel = ""
                for s, source in enumerate(sourcenames[1:]):
                    sourcelabel += temp.format(s+1) 
            
                dg.node(funcname, label.format(len(sourcenames), sourcelabel, info_dict["topology"]), shape="plaintext", fontname="Arial", margin="0.05")
                for s, source in enumerate(sourcenames):
                    dg.edge(source, funcname+":f"+str(s), arrowhead="dot") 
                
                for product in productnames:
                    dg.edge(funcname+":func", product)
            
            elif funclabel == "cropdna":
                info      = info.split("; ")
                info_dict = dict([item.split(":") for item in info if ":" in item])
                temp = '<tr><td port="{}" border="1" align="left"><b> </b><i>{} </i> = {}</td></tr>'
                label="".join(['<<table border="0" cellborder="1" cellspacing="0" cellpadding="1">',
                      '<tr>',
                      '<td port="func" border="1" bgcolor="#909090"><font color="white" point-size="16"><b> </b>{}<b> </b></font></td>',
                      '</tr>',
                      '{}',
                      '</table>>'])
                
                infotext = ""
                if info_dict is not None:
                    for key, value in info_dict.items():
                        infotext += temp.format(key, key, value)
                dg.node(funcname, label.format(funclabel, infotext), shape="plaintext", fontname="Arial")
                dg.edge(sourcenames[0], funcname+":func", arrowhead="dot")
                  
                if operational_function_only == False:
                    start_match = re.search("start=(QUEEN.queried_features_dict\['[^\[\]]+'\])",source)
                    if start_match is not None:    
                        uniquename  = start_match.group(1) 
                        productname = unique_name_dict[uniquename] 
                        #searchname  = product_funcname_dict[productname]  
                        #dg.edge(productname, funcname+":start", style="invis") 
                    
                    end_match = re.search("end=(QUEEN.queried_features_dict\['[^\[\]]+'\])",source) 
                    if end_match is not None:    
                        uniquename  = end_match.group(1) 
                        productname = unique_name_dict[uniquename] 
                        #searchname  = product_funcname_dict[productname]  
                        #dg.edge(productname, funcname+":end", style="invis") 

                for productname in productnames:
                    dg.edge(funcname+":func", productname)
            
            elif funclabel == "cutdna":
                info      = info.split("; ")
                info_dict = dict([item.split(":") for item in info if ":" in item])
                temp = '<tr><td port="{}" border="1" align="left"><b> </b><i>{} </i> = {}</td></tr>'
                label="".join(['<<table border="0" cellborder="1" cellspacing="0" cellpadding="1">',
                      '<tr>',
                      '<td port="func" border="1" bgcolor="#909090"><font color="white" point-size="16"><b> </b>{}<b> </b></font></td>',
                      '</tr>',
                      '{}',
                      '</table>>'])
                
                infotext = ""
                if info_dict is not None:
                    for key, value in info_dict.items():
                        infotext += temp.format(key, key, value)
                dg.node(funcname, label.format(funclabel, infotext), shape="plaintext", fontname="Arial")
                dg.edge(sourcenames[0], funcname+":func", arrowhead="dot")
                
                if operational_function_only == False:
                    for pos_match in re.search("QUEEN.queried_features_dict\['[^\[\]]+'\]",source) is not None:    
                        uniquename  = pos_match.group(1) 
                        productname = unique_name_dict[unique_name] 
                        #seachname   = product_funcname_dict[productname]  
                        #dg.edge(productname, funcname+":positions") 

                for productname in productnames:
                    dg.edge(funcname+":func", productname)

            elif funclabel == "modifyends" and len(sourcenames) > 1:  
                info = info.split("; ")
                if len(info) > 1:
                    info_dict = dict([item.split(":") for item in info])
                else:
                    info_dict = None
                temp = '<tr><td border="1" align="left" port="{}"><b> </b><i>{} </i> = {}</td></tr>'
                label="".join(['<<table border="0" cellborder="1" cellspacing="0" cellpadding="1">',
                      '<tr>',
                      '<td port="func" border="1" bgcolor="#909090"><font color="white" point-size="16"><b> </b>{}<b> </b></font></td>',
                      '</tr>',
                      '{}',
                      '</table>>'])
                
                infotext = ""
                matchl = re.search("left=\.*(QUEEN.dna_dict\['[^\[\]]+'\])", history) 
                if matchl is not None:
                    uniquename = re.search("QUEEN.dna_dict\['([^\[\]]+)'\]", info_dict["leftobj"]).group(0)
                    objname    = name_dict[uniquename]
                    infotext += temp.format("left", "left", info_dict["leftobj"].replace(uniquename, objname))
                else:
                    infotext += temp.format("left", "left", info_dict["left"])
                
                matchr = re.search("right=\.*(QUEEN\.dna.*)", history)
                if matchr is not None:
                    uniquename = re.search("QUEEN.dna_dict\['([^\[\]]+)'\]", info_dict["rightobj"]).group(0)
                    objname    = name_dict[uniquename]
                    infotext += temp.format("right", "right", info_dict["rightobj"].replace(uniquename, objname))
                else:
                    infotext += temp.format("right", "right", info_dict["right"])

                dg.node(funcname, label.format(funclabel, infotext), shape="plaintext", fontname="Arial")
                
                for sourcename in sourcenames:
                    if matchl is not None and sourcename in matchl.group(1):
                        dg.edge(sourcename, funcname+":left", arrowhead="dot")
                    elif matchr is not None and sourcename in matchr.group(1):
                        dg.edge(sourcename, funcname+":right", arrowhead="dot")
                    else:
                        dg.edge(sourcename, funcname+":func", arrowhead="dot")
            
                for productname in productnames:
                    dg.edge(funcname+":func", productname)
            
            elif funclabel == "modifyends":
                info = info.split("; ")
                if len(info) > 1:
                    info_dict = dict([item.split(":") for item in info])
                else:
                    info_dict = None
                temp = '<tr><td border="1" align="left"><b> </b><i>{} </i> = {}</td></tr>'
                label="".join(['<<table border="0" cellborder="1" cellspacing="0" cellpadding="1">',
                      '<tr>',
                      '<td port="func" border="1" bgcolor="#909090"><font color="white" point-size="16"><b> </b>{}<b> </b></font></td>',
                      '</tr>',
                      '{}',
                      '</table>>'])
                infotext = ""
                if info_dict is not None:
                    for key in ["left", "right"]:
                        value = info_dict[key] 
                        infotext += temp.format(key, value)
                dg.node(funcname, label.format(funclabel, infotext), shape="plaintext", fontname="Arial")
                dg.edge(sourcenames[0], funcname+":func", arrowhead="dot")
                
                for productname in productnames:
                    dg.edge(funcname+":func", productname)

            else:
                info = info.split("; ")
                if len(info) > 1:
                    info_dict = dict([item.split(":") for item in info])
                else:
                    info_dict = None
                temp = '<tr><td border="1" align="left"><b> </b><i>{} </i> = {}</td></tr>'
                label="".join(['<<table border="0" cellborder="1" cellspacing="0" cellpadding="1">',
                      '<tr>',
                      '<td port="func" border="1" bgcolor="#909090"><font color="white" point-size="16"><b> </b>{}<b> </b></font></td>',
                      '</tr>',
                      '{}',
                      '</table>>'])
                infotext = ""
                if info_dict is not None:
                    for key, value in info_dict.items():
                        infotext += temp.format(key, value)
                dg.node(funcname, label.format(funclabel, infotext), shape="plaintext", fontname="Arial")
                dg.edge(sourcenames[0], funcname+":func", arrowhead="dot")

                for productname in productnames:
                    dg.edge(funcname+":func", productname)
    
    
    sourcenames = [] 
    for h, history in enumerate(new_histories):
        info    = history[1] 
        history = history[0]
        match   = re.search("(.*QUEEN.dna_dict\['[^\[\]]+'\]) = QUEEN(\(record.*)", history) 
        if match is None:
            break
        else:
            source = match.group(1) 
            for key in re.finditer("QUEEN.dna_dict\['([^\[\]]+)'\]", source):
                key = key.group(0) 
                sourcename = unique_name_dict[key]
                sourcenames.append(sourcename) 
    
    if len(sourcenames) > 1:
        with dg.subgraph() as s:
            s.attr(rank='same')
            for i in range(len(sourcenames[:-1])):
                s.edge(sourcenames[i], sourcenames[i+1], style="invis")

    if operational_function_only == False: 
        pdg = Digraph(name="cluster_operation")
        pdg.attr(rankdir='LR')
        pdg.attr(fontname="arial") 
        pdg.attr(nodesep="0.1")
        pdg.attr(ranksep="0.1")
        pdg.subgraph(sdg) 
        pdg.subgraph(dg)
        dg = pdg  
    
    return dg

"""
def add_key(adict, parent=None, child=None):
    if parent is None:
        adict[child] = {}
        return adict  
    elif parent not in adict:
        for key in adict:
            adict[key] = add_key(adict[key], parent, child) 
    else:
        adict[parent][child] = {} 
    return adict

def get_depth(adict, target, depth=0):
    depth_list = []
    if target in adict:
        return depth
    else:
        depth += 1
        if len(list(adict.keys())) > 0:
            for key in adict:
                depth_list.append(get_depth(adict[key], target, depth)) 
        else:
            return -1
    return max(depth_list)

if __name__ == "__main__":
    adict = {} 
    add_key(adict, None, "A") 
    add_key(adict, None, "B") 
    add_key(adict, None, "C") 
    add_key(adict, "A", "D") 
    add_key(adict, "B", "E") 
    add_key(adict, "D", "E") 
    add_key(adict, "C", "E") 
    add_key(adict, "E", "F") 
    add_key(adict, "E", "G")
    add_key(adict, "E", "H")
    add_key(adict, "H", "I") 

    import pprint 
    pp = pprint.PrettyPrinter(width=10,compact=True)
    pp.pprint(adict)
    
    for target in ["A", "B", "C", "D", "E", "F", "G", "H", "I"]:
        depth = get_depth(adict, target)
        print(depth, target)
"""