import os 
import sys
import pandas as pd 
import collections
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
from  Bio import SeqIO
from matplotlib.transforms import Bbox

matplotlib.rcParams['font.sans-serif']   = ["Helvetica","Arial","Lucida Sans","DejaVu Sans","Lucida Grande","Verdana"]
matplotlib.rcParams['font.family']       = 'sans-serif'
matplotlib.rcParams['font.sans-serif']   = ["Helvetica","Arial","DejaVu Sans","Lucida Grande","Verdana"]
matplotlib.rcParams['font.size']         = 8.0
matplotlib.rcParams["axes.labelcolor"]   = "#000000"
matplotlib.rcParams["axes.linewidth"]    = 1.0
matplotlib.rcParams["xtick.major.width"] = 1.0
matplotlib.rcParams["ytick.major.width"] = 1.0
matplotlib.rcParams['xtick.major.pad']   = 6
matplotlib.rcParams['ytick.major.pad']   = 6
matplotlib.rcParams['xtick.major.size']  = 6
matplotlib.rcParams['ytick.major.size']  = 6

def map_feat(fig, ax, ax2, feats, length, head_length=np.pi * 0.02, unvisible_types=["source"], visible_types=[], enlarge=1.0, format=1, bottom=400):
    if format == 1:
        outer    = 60
        inner    = 48
        bottom_h = bottom
        lane_h   = 70
        normal_w = 1000
        matplotlib.rcParams['font.size'] = 8.0
    else:
        outer    = 60
        inner    = 48
        bottom_h = bottom
        lane_h   = 250
        normal_w = 1000
        matplotlib.rcParams['font.size'] = 7.0

    renderer    = fig.canvas.get_renderer()
    coordinate  = ax2.transData.inverted() 
    y_list    = [] 
    ty_list   = [] 
    visible   = 1
    unvisible = 1 
    gene_position_matrix = [[0] * length]
    text_position_matrix = [np.array([0] * length)] + [np.array([0] * length)] + [np.array([0] * length)]
    label_position_list = [] 
    if len(unvisible_types) == 0:
        visible   = 1
        unvisible = 1
    else:
        unvisible = 0
    
    if len(visible_types) == 0:
        visible = 1
    else:
        visible   = 0 
        unvisible = 0
        unvisible_types = []

    for i, feat in enumerate(feats):
        if feat.type in unvisible_types:
            pass
        
        elif visible == 1 or feat.type in visible_types:
            if "label" in feat.qualifiers:
                if type(feat.qualifiers["label"]) == list:
                    label = feat.qualifiers["label"][0]
                else:
                    label = feat.qualifiers["label"]
            else:
                label = feat.type
            strand = feat.location.strand
            if strand == 1:
                gs_origin = feat.location.parts[0].start.position 
                ge_origin = feat.location.parts[-1].end.position
                gs = gs_origin * 2 * np.pi / length 
                ge = ge_origin * 2 * np.pi / length
            else:
                gs_origin = feat.location.parts[-1].start.position 
                ge_origin = feat.location.parts[0].end.position
                gs = gs_origin * 2 * np.pi / length
                ge = ge_origin * 2 * np.pi / length 
            
            y = 0
            if i > 0:
                flag = 0
                if gs_origin < ge_origin:
                    for y, row in enumerate(gene_position_matrix):
                        if 1 in row[gs_origin:ge_origin]:
                            flag = 1
                        else:
                            flag = 0
                            break    
                    if flag == 1:
                        y += 1 
                        gene_position_matrix.append([0] * length)
                        text_position_matrix.append(np.array([0] * length))
                        text_position_matrix.append(np.array([0] * length))
                        text_position_matrix.append(np.array([0] * length))
                    else:
                        pass 
                else:
                    for y, row in enumerate(gene_position_matrix):
                        if 1 in row[gs_origin:]:
                            flag = 1
                        else:
                            flag = 0
                            break    

                    for y, row in enumerate(gene_position_matrix):
                        if 1 in row[:ge_origin]:
                            flag = 1
                        else:
                            flag = 0
                            break    

                    if flag == 1:
                        y += 1 
                        gene_position_matrix.append([0] * length)
                        text_position_matrix.append(np.array([0] * length))
                        text_position_matrix.append(np.array([0] * length))
                        text_position_matrix.append(np.array([0] * length))
                    else:
                        pass 

            if abs(ge-gs) < head_length * 1.2:
                hl  = abs(ge-gs)
                margin1 = head_length * 0.15 /enlarge
                margin2 = head_length * 0.25 /enlarge
                hl2 = hl - (margin1+margin2)
                if hl2 < 0:
                    hl2 = 0
                    wd2 = 0 
                else:
                    wd2 = 0.8 * ((hl2/hl) ** 1.0)
            else:
                hl  = head_length 
                hl2 = hl*0.85  
                margin1 = hl * 0.15 /enlarge
                margin2 = hl * 0.25 /enlarge
                wd2     = 0.65

            if "facecolor_dbrick" in feat.qualifiers:
                if type(feat.qualifiers["facecolor_dbrick"]) == list:
                    facecolor = feat.qualifiers["facecolor_dbrick"][0] 
                else:
                    facecolor = feat.qualifiers["facecolor_dbrick"]
            else:
                facecolor = "#ffffec" 
            
            if "edgecolor_dbrick" in feat.qualifiers:
                if type(feat.qualifiers["edgecolor_dbrick"]) == list:
                    edgecolor = feat.qualifiers["edgecolor_dbrick"][0] 
                else:
                    edgecolor = feat.qualifiers["edgecolor_dbrick"]
            else:
                if strand == 1:
                    edgecolor = "#FACAC8" 
                elif strand == -1:
                    edgecolor = "#C8DFFA" 
                else:
                    edgecolor = "#CCCCCC"
                
            if "note_dbrick" in feat.qualifiers:
                note   = feat.qualifiers["note_dbrick"]
                if type(note) == list:
                    note   = feat.qualifiers["note_dbrick"][0]
                label = note

            if gs < ge: 
                width  = ge-gs
                middle = (ge+gs)/2
            else:
                width  = ge + (2*np.pi-gs) 
                middle = (ge+gs+2*np.pi)/2  
            
            if format == 1:
                if y < 4:
                    margin = np.pi*(0.004-y*0.0005) 
                else:
                    margin = np.pi*(0.002)

            else:
                if y < 3:
                    margin = np.pi*(0.004-y*0.001) 
                else:
                    margin = np.pi*(0.0015)

            if width > 1.2 * head_length:
                if strand == 1:
                    ax.bar([gs], [outer], bottom=y*lane_h+bottom_h-outer/2, width=width-head_length*0.98, align="edge", fc=edgecolor, lw=0.0, zorder=1)
                    ax.bar([gs+margin], [inner], bottom=y*lane_h+bottom_h-inner/2, width=width-margin-head_length*0.98, align="edge", fc=facecolor, lw=0.0, zorder=2)
                    ax.arrow(x=ge-head_length, y=y*lane_h+bottom_h, dx=head_length, dy=0, width=outer, head_width=outer, head_length=head_length, length_includes_head=True, fc=edgecolor, lw=0.0, zorder=3)
                    ax.arrow(x=ge-head_length, y=y*lane_h+bottom_h, dx=head_length-margin*1.4, dy=0, width=inner, head_width=inner, head_length=head_length-margin*1.4, length_includes_head=True, fc=facecolor, lw=0.0, zorder=4)
                elif strand == -1:
                    ax.bar([gs+head_length*0.98], [outer], bottom=y*lane_h+bottom_h-outer/2, width=width-head_length*0.98, align="edge", fc=edgecolor, lw=0.0, zorder=1)
                    ax.bar([gs+head_length*0.98], [inner], bottom=y*lane_h+bottom_h-inner/2, width=width-margin-head_length*0.98, align="edge", fc=facecolor, lw=0.0, zorder=2)
                    ax.arrow(x=gs+head_length, y=y*lane_h+bottom_h, dx=-1*head_length, dy=0, width=outer, head_width=outer, head_length=head_length, length_includes_head=True, fc=edgecolor, lw=0.0, zorder=3) 
                    ax.arrow(x=gs+head_length, y=y*lane_h+bottom_h, dx=-1*(head_length-margin*1.4), dy=0, width=inner, head_width=inner, head_length=head_length-margin*1.4, length_includes_head=True, fc=facecolor, lw=0.0, zorder=4)

                else:
                    ax.bar([gs], [outer], bottom=y*lane_h+bottom_h-outer/2, width=width, align="edge", fc=edgecolor, lw=0.0)
                    ax.bar([gs+margin], [inner], bottom=y*lane_h+bottom_h-inner/2, width=width-2*margin, align="edge", fc=facecolor, lw=0.0)
            else:
                if strand == 1:
                    ax.arrow(x=ge-width, y=y*lane_h+bottom_h, dx=width, dy=0, width=outer, head_width=outer, head_length=width, length_includes_head=True, fc=edgecolor, lw=0.0)
                    if width > 2.4 * margin:
                        hw = outer * 1.2 * (width-2.4*margin)/width
                        if hw > outer:
                            hw = outer * (width-2.4*margin)/width
                        ax.arrow(x=ge-width+margin, y=y*lane_h+bottom_h, dx=width-2.4*margin, dy=0, width=hw, head_width=hw, head_length=width-2.4*margin, length_includes_head=True, fc=facecolor, lw=0.0)
                
                elif strand == -1:
                    ax.arrow(x=gs+width, y=y*lane_h+bottom_h, dx=-1*width, dy=0, width=outer, head_width=outer, head_length=width, length_includes_head=True, fc=edgecolor, lw=0.0)
                    if width > 2.4 * margin:
                        hw = outer * 1.2 * (width-2.4*margin)/width
                        if hw > outer:
                            hw = outer * (width-2.4*margin)/width
                        ax.arrow(x=gs+width-margin, y=y*lane_h+bottom_h, dx=-1*(width-2.4*margin), dy=0, width=hw, head_width=hw, head_length=width-2.4*margin, length_includes_head=True, fc=facecolor, lw=0.0)
                
                else:
                    ax.bar([gs], [outer], bottom=y*lane_h+375, width=width, align="edge", fc=facecolor, ec=edgecolor, lw=0.0)
                    #ax.arrow(x=gs+margin1, y=y*50+500, dx=ge-gs-(margin1+margin2), dy=0, width=wd2, head_width=wd2, head_length=0, length_includes_head=True, color='k', fc=facecolor, lw=0.0)

            
            label_position_list.append((label, width,  gs, ge,  middle,  y, facecolor, edgecolor))
            if gs_origin < ge_origin:
                for j in range(gs_origin,ge_origin):
                    gene_position_matrix[y][j] = 1  
            else:
                for j in range(gs_origin,length):
                    gene_position_matrix[y][j] = 1 
                for j in range(0, ge_origin):
                    gene_position_matrix[y][j] = 1
            y_list.append(y)
             
    if max(y_list)*lane_h+bottom_h < normal_w:
        fig_width = normal_w
    else:
        fig_width = max(y_list)*lane_h+bottom_h
    #fig_width = 1285

    for tnum, (label, w, gs, ge, x, y, fc, ec) in enumerate(label_position_list):
        if gs < ge: 
            gmiddle = (ge+gs)/2
        else:
            gmiddle = (ge+gs+2*np.pi)/2  

        slide = 0 
        pos_list   = []  
        width_list = []
        for char in label:
            text        = ax2.text(slide, 0, char, ha="right", va="center")
            bbox_text   = text.get_window_extent(renderer=renderer)
            bbox_text   = Bbox(coordinate.transform(bbox_text))
            text.set_visible(False)
            width_list.append(bbox_text.width) 
            pos_list.append(slide+bbox_text.width/2) 
            slide += bbox_text.width
        pos_list = [-1*(p-0.5*slide) * 2*fig_width for p in pos_list]
        new_pos_list = [] 
        for pos, width in zip(pos_list, width_list):
            new_pos_list.append((np.arccos(pos/(y*lane_h+bottom_h))-0.5*np.pi+x, y*lane_h+bottom_h, y, pos, x, width))
        
        t_width = (new_pos_list[-1][0] - new_pos_list[0][0])
        if t_width < w-2*head_length:
            if new_pos_list[len(new_pos_list) // 2][0] < 0.5 * np.pi or new_pos_list[len(new_pos_list) // 2][0] > 1.5 * np.pi:
                rotation = lambda x:(-1.0*x)*180/np.pi 
            else:
                label    = label[::-1]
                slide = 0 
                pos_list   = [] 
                width_list = []
                for char in label:
                    text        = ax2.text(slide, 0, char, ha="right", va="center")
                    bbox_text   = text.get_window_extent(renderer=renderer)
                    bbox_text   = Bbox(coordinate.transform(bbox_text))
                    text.set_visible(False)
                    pos_list.append(slide+bbox_text.width/2) 
                    width_list.append(bbox_text.width) 
                    slide += bbox_text.width
                
                pos_list = [-1*(p-0.5*slide) * 2 * fig_width for p in pos_list]
                new_pos_list = [] 
                for pos, width in zip(pos_list, width_list):
                    new_pos_list.append((np.arccos(pos/(y*lane_h+bottom_h))-0.5*np.pi+x, y*lane_h+bottom_h, y, pos, x, width))
                    
                rotation = lambda x:(-1.0*x)*180/np.pi+180
            
            for char, (theta, height, y, pos, x, width) in zip(label,new_pos_list):
                ax.text(theta, height, char, ha="center", va="center", rotation=rotation(theta), zorder=10)

        else:
            flag = 0 
            sign = 1
            #print(new_pos_list[0][2])
            if format == 1:
                i = 0 
            else:
                i = new_pos_list[0][2] * 3
            while i < len(text_position_matrix):
                if format == 1:
                    if i < 3:
                        y = bottom_h - 58 - i * 55
                    else:
                        y = max(y_list)*lane_h+bottom_h + 58 + (i-3) * 55
                else:
                    if i % 3 == 0:
                        y = (i//3)*lane_h+bottom_h+60
                    elif i % 3 == 1:
                        y = (i//3)*lane_h+bottom_h+113
                    else:
                        y = (i//3)*lane_h+bottom_h+166
                
                ts = np.arccos(new_pos_list[0][3]/y)-0.5*np.pi + x
                te = np.arccos(new_pos_list[-1][3]/y)-0.5*np.pi + x 
                if ts < 0:
                    ts = 2*np.pi + ts
                if te > 2*np.pi:
                    te = te-2*np.pi 
                tts     = int(length * ts / (2 * np.pi))
                tte     = int(length * te / (2 * np.pi))
                ts, te = tts, tte

                sbuf = int(2.0 * length * (np.arcsin(new_pos_list[0][-1]*2*fig_width/y) / (2 * np.pi)))
                ebuf = int(2.0 * length * (np.arcsin(new_pos_list[-1][-1]*2*fig_width/y) / (2 * np.pi)))
                tmp_ts = ts - sbuf 
                if tmp_ts < 0: 
                    tmp_ts = length + tmp_ts 
                
                tmp_te = te + ebuf
                if tmp_te >= length:
                    tmp_te = tmp_te - length

                if tmp_ts <= tmp_te:
                    middle = (tmp_ts + tmp_te) / 2
                    for j in range(0,int((middle-tmp_ts)*0.6)):
                        if tmp_te+j >= length:
                            break
                        if 1 in text_position_matrix[i][tmp_ts+j:tmp_te+j]:
                            pass 
                        else:
                            sign = 1
                            flag = 1
                            break 
                        
                        
                    if flag == 0:
                        for j in range(int((tmp_te-middle)*0.6),-1,-1):
                            if tmp_ts-j <= 0:
                                break
                            if 1 in text_position_matrix[i][tmp_ts-j:tmp_te-j]:
                                pass 
                            else:
                                sign = -1
                                flag = 1
                                break
                            
                else:
                    j = 0
                    if 1 in text_position_matrix[i][tmp_ts:] or 1 in text_position_matrix[i][0:tmp_te]:
                        pass
                    else:
                        flag = 1
                        break

                if flag == 0:
                    pass 
                else: 
                    break
                i += 1 

            if flag == 0:
                if format == 1:
                    if i < 3:
                        y = bottom_h - 58 - i * 55
                    else:
                        y = max(y_list)*lane_h+bottom_h + 58 + (i-3) * 55
                else:
                    y = (i-len(gene_position_matrix)*3) * 60 + len(gene_position_matrix) * lane_h + bottom_h 
                text_position_matrix.append(np.array([0] * length)) 
                if tmp_ts <= tmp_te:
                    text_position_matrix[i][tmp_ts:tmp_te] = 1
                else:
                    text_position_matrix[i][tmp_ts:] = 1
                    text_position_matrix[i][:tmp_te] = 1
            else:
                if tmp_ts <= tmp_te:
                    text_position_matrix[i][tmp_ts+(j*sign):tmp_te+(j*sign)] = 1
                else:
                    text_position_matrix[i][tmp_ts:] = 1
                    text_position_matrix[i][:tmp_te] = 1
            
            modified_pos_list = []
            for old_theta, old_height, old_y, pos, x, width in new_pos_list:
                if flag == 1 and tmp_ts <= tmp_te:
                    new_theta = np.arccos(pos/y)-0.5*np.pi + x + (j*sign)/length * 2 * np.pi
                    target    = np.arccos(pos/y)-0.5*np.pi + x 
                else:
                    new_theta = np.arccos(pos/y)-0.5*np.pi + x
                    target    = np.arccos(pos/y)-0.5*np.pi + x 
                modified_pos_list.append([new_theta, target, old_theta, y, old_height, width]) 

                
            if modified_pos_list[len(new_pos_list) // 2][0] < 0.5 * np.pi or modified_pos_list[len(new_pos_list) // 2][0] > 1.5 * np.pi:
                direction = 1
                rotation = lambda x:(-1.0*x)*180/np.pi 
            else:
                direction = -1
                label    = label[::-1]
                slide = 0 
                pos_list = [] 
                for char in label:
                    text        = ax2.text(slide, 0, char, ha="right", va="center")
                    bbox_text   = text.get_window_extent(renderer=renderer)
                    bbox_text   = Bbox(coordinate.transform(bbox_text))
                    text.set_visible(False)
                    pos_list.append(slide+bbox_text.width/2) 
                    slide += bbox_text.width
                pos_list = [-1*(p-0.5*slide) * 2*fig_width for p in pos_list]
                
                for p, pos in enumerate(pos_list):
                    if flag == 1:
                        new_theta = np.arccos(pos/y)-0.5*np.pi + x + (j*sign)/length * 2 * np.pi
                        target    = np.arccos(pos/y)-0.5*np.pi + x 
                    else:
                        new_theta = np.arccos(pos/y)-0.5*np.pi + x
                        target    = np.arccos(pos/y)-0.5*np.pi + x 
                    
                    modified_pos_list[p][0] = new_theta
                    modified_pos_list[p][1] = target
                
                rotation = lambda x:(-1.0*x)*180/np.pi+180
            
            for char, (theta, target, old_theta, y, old_height, width) in zip(label, modified_pos_list):
                ax.text(theta, y, char, ha="center", va="center", rotation=rotation(theta))
            
            mid = modified_pos_list[len(new_pos_list) // 2]
            s = modified_pos_list[0]
            e = modified_pos_list[-1] 
            sbuf = sbuf*0.4*2*np.pi/length
            ebuf = ebuf*0.4*2*np.pi/length
            sbuf, ebuf = max([sbuf, ebuf]), max([sbuf, ebuf]) 
            ax.plot([gmiddle, gmiddle], [mid[3], mid[4]], lw=0.5, color="k", zorder=0)
            
            if direction == 1:
                ax.bar([s[0]-sbuf], [40], width=e[0]-s[0]+sbuf+ebuf, bottom=s[3]-20, lw=0.5, ec=ec, fc=fc, align="edge")
            elif direction == -1:
                ax.bar([s[0]-ebuf], [40], width=e[0]-s[0]+sbuf+ebuf, bottom=s[3]-20, lw=0.5, ec=ec, fc=fc, align="edge")
           
            ty_list.append(y) 

    y_set = list(set(y_list)) 
    y_set.sort() 
    for y in y_set:
        ax.bar([gs], [40], bottom=y*lane_h+bottom_h-20, width=2*np.pi, align="edge", fc="#EFEFEF", ec=edgecolor, lw=0.0, zorder=0)
    
    ylim = max([max(y_list)*240+400, max(ty_list)]) + 240
    if ylim < normal_w:
        ylim = normal_w
        ax.set_ylim(0,normal_w)
    else:
        ax.set_ylim(0,ylim)
   
    ax.patch.set_alpha(0.0) 
    ax2.patch.set_alpha(0.0)
    if ylim > normal_w:
        fig.set_size_inches(6 * ylim/fig_width, 6 * ylim/fig_width)
    return ax, ax2, y_list, ty_list, fig_width, ylim

def visualize(brick, format=1, unvisible_types=["source"], visible_types=[], bottom=600):
    figure = plt.figure(figsize=(6,6))
    ax      = figure.add_axes([0,0,1,1], polar=True, label="hoge")
    ax2     = figure.add_axes([0,0,1,1], label="fuga")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.spines['polar'].set_visible(False)
    ax.xaxis.set_ticks([])
    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticks([])
    ax.yaxis.set_ticklabels([])
    ax2.set_axis_off()
    ax, ax2, y_list, ty_list, fig_width, ylim = map_feat(figure, ax, ax2, brick.features, len(brick.seq), unvisible_types=unvisible_types, visible_types=visible_types, format=format, bottom=bottom, enlarge=1.0) 
    renderer    = figure.canvas.get_renderer()
    coordinate  = ax2.transData.inverted() 
    brick_id    = brick.name
    text        = ax2.text(0.5, 0.5, brick_id, ha="center", va="center", fontsize=10)
    bbox_text   = text.get_window_extent(renderer=renderer)
    bbox_text   = Bbox(coordinate.transform(bbox_text))
    bp_text     = ax2.text(0.5, 0.5-bbox_text.height-0.01, str(len(brick.seq)) + "bp", ha="center", va="center", fontsize=8)
    
    if bbox_text.width/2 > bottom:
        text.set_visible(False)
        bb_text.set_visible(False) 
    return figure 

if __name__ == "__main__":
    from dbrick import *
    brick = Dbrick(record=sys.argv[1])
    #if brick.name == ".":
    brick.name = sys.argv[1].split("/")[-1].replace(".gbk","")  
    fig   = visualize(brick, format=2, unvisible_types=["primer_bind"], bottom=400) 
    fig.patch.set_alpha(0.0) 
    fig.savefig("{}.pdf".format(brick.name), bbox_inches="tight")