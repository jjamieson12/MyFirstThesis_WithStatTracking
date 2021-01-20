#############################################################
### Some helpful functions for making stat-tracking plots ###
#############################################################
###                                                       ###
### Author: Jonathan Jamieson                             ###
### Edit:   16/01/2021                                    ###
###                                                       ###
#############################################################

from colourMaps import COLSETS
from matplotlib.patches import Rectangle #For post-processing... not doctoring
import matplotlib.patheffects as pe #More ...post-processing
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap #Custom cmaps 
from math import floor

def add_annotation(ax,yslice,xslice,colour,offset,total=False,logy=True):
    fracstring=""
    if logy:
        if yslice.iloc[-1] != 0:
            yloc = yslice.iloc[-1]
        else:
            yloc=2.1 #limit of log scale seems to be 2 by default?
    else:
        yloc = yslice.iloc[-1]
    if total != False:
        fracstring = " ("+str('{0:.1f}'.format((yslice.iloc[-1]/total)*100.0))+"%)"
    ax.annotate(str(round(yslice.iloc[-1],1))+fracstring, color=colour, size=14,
    xy=(xslice.iloc[-1]+offset,yloc), xycoords='data',
    xytext=((xslice.iloc[-1]+offset)*1.02,yloc), textcoords='data',
    arrowprops=dict(arrowstyle="-",connectionstyle="arc3,rad=0.0",color=colour,lw=2),
    verticalalignment='center'
    )
    return None


def make_graph_by_commit(ax,yslices_uns,ylabels_uns,xslice,
                         incinlines=True,
                         redtext=False,
                         trackable="Words",
                         colset="JJcool",
                         title="Cumulative words per commit",
                         annotate=True,
                         logy=True,
                         percommit=False
):
    
    #Set up colour sets ------------------------------------
    colours=[]
    if colset in COLSETS.keys():
        colours=COLSETS[colset]
    else:
        print("Please provide viable colour set, options are: "+str(list(COLSETS.keys())))
        return None
  
    #Check inputs are correct ------------------------------------
    if type(yslices_uns) is not list:
        print("Please input yslices to be plotted as LIST of dataframe elements")
        print("e.g. make_graph_by_commit(ax=axis,yslices=[stats_norm.w_total,stats_norm.w_text],ylabels=['Total words','Words in text'],xslice=stats_norm.id)")
        return None
    if len(yslices_uns) > len(colours):
        print("Trying to plot more slices than there are defined colours, no can do chief, sorry about that")
        return None

    #Sort values
    sorting_list=[]
    for s in yslices_uns:
        sorting_list.append(sum(s))
    sorting_idx_list = sorted(range(len(sorting_list)),key=lambda x:sorting_list[x],reverse=True)
    ylabels = [ylabels_uns[i] for i in sorting_idx_list ]
    yslices = [yslices_uns[i] for i in sorting_idx_list ]

    #Make plots ------------------------------------
    slicetot=-1
    xoffset=1.0/(len(yslices)+1.0)
    for i,s in enumerate(yslices):
        if "total words" in ylabels[i].lower():
            slicetot = s.iloc[-1]
        if percommit:
            ax.bar(xslice+i*xoffset,s,xoffset,align='edge',tick_label=xslice,color=colours[i],label=ylabels[i])
            if "total" in ylabels[i] or "Total" in ylabels[i]:
                ax.plot(xslice[1:],s[1:].expanding(1).mean(),color=colours[i],linestyle='--',label="Rolling average")
        else:
            ax.bar(xslice,s,1,align='edge',tick_label=xslice,color=colours[i],label=ylabels[i])
    if redtext is not False:
        ax.step(redtext[0]+1,redtext[1],where='pre',color="red",linewidth=2.5,label="Red text",path_effects=[pe.Stroke(linewidth=5, foreground='w'), pe.Normal()])

    #Do legend manually to control order
    handles,labels = ax.get_legend_handles_labels()
    if redtext is not False and percommit is not False:
        handles_ord = handles[2:]+[handles[0],handles[1]]
        labels_ord = labels[2:]+[labels[0],labels[1]]
    elif redtext is not False:
        handles_ord = handles[1:]+[handles[0]]
        labels_ord = labels[1:]+[labels[0]]
    elif percommit is not False:
        handles_ord = handles[1:]+[handles[0]]
        labels_ord = labels[1:]+[labels[0]]

    else:
        handles_ord = handles
        labels_ord = labels
        
    ncols=(len(labels_ord)//4 + 1)         
    leg=ax.legend(handles_ord,labels_ord,loc=(0.025,1.0-(len(labels_ord)*0.045/ncols)), frameon=True, framealpha=1,borderaxespad=3,ncol=ncols)
    for text in leg.get_texts():
        plt.setp(text, color = 'black', size=18)

    #Plot formatting -------------------------------
    if logy: ax.set_yscale("log")     
    ax.set_title(title,fontsize=18)
    ax.set_xlabel("Commit number",fontsize=18,labelpad=13)
    if percommit:
        ax.set_xticks(xslice.iloc[1:]+(0.5*(1-xoffset)))
    else:
        ax.set_xticks(xslice.iloc[1:]+0.5)
    ax.set_xticklabels(xslice.iloc[1:],fontsize=16,rotation=270)
    ax.set_ylabel(trackable,fontsize=18,rotation=0,labelpad=40)
    ax.tick_params(axis='y', which='major', labelsize=16)
    ax.margins(0.1, 0.25) #Add a bit of space at top and bottom of plot

    if annotate:
        ax.set_xlim([xslice.iloc[1],(xslice.iloc[-1]+1)*1.2]) #Add space to the right of plot
        
        #Add annotations
        posx_rect = Rectangle((xslice.iloc[-1]+1,0),(xslice.iloc[-1]+1)*0.2,yslices[0].iloc[-1],linewidth=1,edgecolor='white',facecolor='white')
        ax.add_patch(posx_rect) #White rectangle covering the extended right hand side of plot
        for i, yslice in enumerate(yslices):
            if ylabels[i] != "In-line math symbols" or incinlines:
                if "total words" in ylabels[i].lower() or slicetot==-1:
                    add_annotation(ax,yslice,xslice,colours[i],offset=1,total=False,logy=logy)
                else:
                    add_annotation(ax,yslice,xslice,colours[i],offset=1,total=slicetot,logy=logy)
    
        if redtext is not False:
            add_annotation(ax,redtext[1],redtext[0],"red",offset=1,total=slicetot,logy=logy)

    else:
        if percommit:
            ax.set_xlim([xslice.iloc[1],(xslice.iloc[-1]+1)]) #Fill x-axis
        else:
            ax.set_xlim([xslice.iloc[1],(xslice.iloc[-1])]) #Fill x-axis

            
    return None


#Similar functionality to _by_commit but much simpler
def make_graph_by_day(ax,yslices_uns,ylabels_uns,xslice,trackable="Words",redtext=[False],incinlines=True,colset="JJcool",title="Cumulative words per day",logy=True):
    
    #Set up colour sets ------------------------------------
    colours=[]
    if colset in COLSETS.keys():
        colours=COLSETS[colset]
    else:
        print("Please provide viable colour set, options are: "+str(list(COLSETS.keys())))
        return None
  
    #Check inputs are correct ------------------------------------
    if type(yslices_uns) is not list:
        print("Please input yslices to be plotted as LIST of dataframe elements")
        print("e.g. make_graph_by_commit(ax=axis,yslices=[stats_norm.w_total,stats_norm.w_text],ylabels=['Total words','Words in text'],xslice=dsfc)")
        return None
    if len(yslices_uns) > len(colours):
        print("Trying to plot more slices than there are defined colours, no can do chief, sorry about that")
        return None
        
    #Sort values
    sorting_list=[]
    for s in yslices_uns:
        sorting_list.append(sum(s))
    sorting_idx_list = sorted(range(len(sorting_list)),key=lambda x:sorting_list[x],reverse=True)
    ylabels = [ylabels_uns[i] for i in sorting_idx_list ]
    yslices = [yslices_uns[i] for i in sorting_idx_list ]
    
    #Make plots ------------------------------------
    slicetot=-1
    for i,s in enumerate(yslices):
        if "total words" in ylabels[i].lower():
            slicetot = s.iloc[-1]
        ax.plot(xslice,s,color=colours[i],linewidth=2.5,label=ylabels[i])
    if redtext[0] != False:
        ax.plot(xslice,redtext[1],color="red",linewidth=2.5,label="Red text")
        
    handles,labels = ax.get_legend_handles_labels()
    ncols=(len(labels)//4 + 1) 
    leg=ax.legend(loc=(0.025,1.0-(len(labels)*0.045/ncols)), frameon=True, framealpha=1,borderaxespad=3,ncol=ncols)
    for text in leg.get_texts():
        plt.setp(text, color = 'black', size=18)
        
    #Make custom x-axis ticks
    lastday = floor(xslice.iloc[-1])
    cust_xticks = list(range(0,lastday,10)) + [lastday]
    
    #Plot formatting -------------------------------
    if logy: ax.set_yscale("log")
    ax.set_xlim([xslice.iloc[0],xslice.iloc[-1]*1.2])
    ax.set_title(title,fontsize=18)
    ax.set_xlabel("Days since first commit",fontsize=18,labelpad=15)
    ax.set_xticks(cust_xticks)
    ax.set_xticklabels(cust_xticks,fontsize=16,rotation=0)
    ax.set_ylabel(trackable,fontsize=18,rotation=0,labelpad=35)
    ax.tick_params(axis='y', which='major', labelsize=16)
    ax.margins(0.1, 0.25) #Add a bit of space at top of plot
    
    
    #Add annotations
    posx_rect = Rectangle((xslice.iloc[-1],0),(xslice.iloc[-1])*0.2,yslices[0].iloc[-1],linewidth=1,edgecolor='white',facecolor='white')
    ax.add_patch(posx_rect) #White rectangle covering the extended right hand side of plot
    for i, yslice in enumerate(yslices):
        if ylabels[i] != "In-line math symbols" or incinlines:
            if "total words" in ylabels[i].lower() or slicetot==-1:
                add_annotation(ax,yslice,xslice,colours[i],offset=0,total=False,logy=logy)
            else:
                add_annotation(ax,yslice,xslice,colours[i],offset=0,total=slicetot,logy=logy)
    if redtext[0] != False:
        add_annotation(ax,redtext[1],xslice,"red",offset=0,total=False,logy=logy)
        
    return None


#Make stylised sentiment plot
def make_sentiment(ax,yslice,xslice,xlabel,markersize=500,colset="JJrg",title="Writing Sentiment"):
    
    #Set up colour sets ------------------------------------
    colours=[]
    if colset in COLSETS.keys():
        colours=COLSETS[colset]
    else:
        print("Colset options for Sentiment are: "+str(list(COLSETS.keys())[-4:]))
        print("defaulting to red to green")
        colours=["r","g"]
  
    
    #Make plot ------------------------------------
    cmap=LinearSegmentedColormap.from_list('cust_col',colours, N=10) 
    ax.scatter(xslice,yslice,s=markersize,c=yslice,cmap=cmap,marker="X")
    rolling_av = [yslice[0]]
    rolling_av[1:] = yslice[1:].expanding(1).mean()
    ax.plot(xslice,rolling_av,color="black",linestyle='--',label="Rolling average",lw=3.5)
        
    #Make custom x-axis ticks
    lastday = floor(xslice.iloc[-1])
    cust_xticks = list(range(0,lastday,10)) + [lastday]
    
    #Make custom y-axis ticks
    cust_yticks = [0,5,10]
    
    #Plot formatting -------------------------------
    ax.set_xlim([xslice.iloc[0],xslice.iloc[-1]*1.05])
    ax.set_title(title,fontsize=18)
    ax.set_xlabel(xlabel,fontsize=18,labelpad=15)
    ax.set_xticks(cust_xticks)
    ax.set_xticklabels(cust_xticks,fontsize=16,rotation=0)
    ax.set_yticks(cust_yticks)
    ax.set_yticklabels(["\N{disappointed face}","\N{neutral face}","\N{smiling face with open mouth}"],fontsize=44,rotation=0)
    ax.get_yticklabels()[0].set_color(colours[0])
    ax.get_yticklabels()[2].set_color(colours[-1])
    if len(colours)>2: ax.get_yticklabels()[1].set_color(colours[1])


    ax.tick_params(axis='y', which='major', pad=30)
        
    return None
