import pandas as pd #For data handling
import matplotlib.pyplot as plt
import numpy as np
import wordcloud as cloud #For fancy wordmap
from PIL import Image
from plotHelpers import add_annotation, make_graph_by_commit, make_graph_by_day, make_sentiment

#Configuration parameters
#--------------------------------------------------------------------------
plotdir = "../stats/figures/"
#plotdir = "../stats/figures/example_"
statfile = r"../stats/masterStats.json" #Actual thesis stats
#statfile = r"../stats/exampleStats.json" #Representative example
wordfreqfile = "../stats/master_wordcloud.txt" #Actual thesis word frequencies
#wordfreqfile = "../stats/example_wordcloud.txt" #Representative example taken from current int-note draft

colourmap = "../stats/wordcloud_masks/ttbar_colourmap.jpg" #Simple shape to fit the wordcloud to
cm_overlay = "../stats/wordcloud_masks/ttbar_colourmap_overlay.jpg"#Optional fine detail overlay
cm_colourmask = "../stats/wordcloud_masks/ttbar_colourmap_colourmask.png" #block colour diagram to clean up edges when word colouring (can be duplicate of colourmap)
max_cloudwords = 1000

stats=pd.read_json(statfile)  
inc_inlines = True #Whether in-line maths count towards total word-count or not

stats_norm = pd.json_normalize(stats['commit']) #pandify the stats

#Pre-calculate some more things we'll need
#--------------------------------------------------------------------------
#Time things
first_epoch = stats_norm.epoch_time[0] #first commit epoch time
seconds_in_day = 86400.0
dsfc = ((stats_norm.epoch_time - first_epoch)/seconds_in_day).round(2) #days since first commit

#For red-text as step function
stats_norm_step = stats_norm.copy() #deep copy
stats_norm_step = stats_norm_step.append(stats_norm.iloc[-1], ignore_index=True)

#Adjust total if inlines included
if inc_inlines:
    stats_norm.w_total = stats_norm.w_total + stats_norm.n_inlines

#Calculate difference between ith and (i-1)th commit for each stat
per_commits={}
stats=[stats_norm.w_total,stats_norm.w_text,stats_norm.w_caption,stats_norm.n_inlines,stats_norm.w_header,stats_norm.n_headers,stats_norm.n_figures,stats_norm.n_equations,stats_norm.n_page_total,stats_norm.n_page_content,stats_norm.n_chapters,stats_norm.w_redtext,stats_norm_step.w_redtext,dsfc]
labels=["w_total","w_text","w_caption","n_inlines","w_header","n_headers","n_figures","n_equations","n_page_total","n_page_content","n_chapters","w_redtext","step_w_redtext","dsfc"]
for s,l in zip(stats,labels):
    per_commits[l] = s.diff(1)
    per_commits[l].iloc[0]=s.iloc[0]
    
#Calculate writing rates by commit
tot_rate_by_commit = per_commits["w_total"]/per_commits["dsfc"]
txt_rate_by_commit = per_commits["w_text"]/per_commits["dsfc"]
    
#Now let's make some plots
#--------------------------------------------------------------------------

print("Making plots Vs commit number.....")
f_w_by_commit, w_by_commit = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_commit(w_by_commit,
                     yslices_uns=[stats_norm.w_text,stats_norm.w_total,stats_norm.w_caption,stats_norm.n_inlines,stats_norm.w_header],
                     ylabels_uns=["Words in text","Total words","Words in captions","In-line math symbols","Words in headers"],
                     xslice=stats_norm.id,
                     incinlines=inc_inlines,
                     redtext=[stats_norm_step.id,stats_norm_step.w_redtext],
                     trackable="Words",
                     colset="JJcool",
                     title="Cumulative word-count by commit",
                     annotate=True,
                     logy=True,
                    )
f_w_by_commit.savefig(plotdir+'w_by_commit.png',bbox_inches = 'tight',pad_inches = 0.15)
f_w_by_commit.savefig(plotdir+'w_by_commit_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail 

f_n_by_commit, n_by_commit = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_commit(n_by_commit,
                     yslices_uns=[stats_norm.n_headers,stats_norm.n_figures,stats_norm.n_equations],
                     ylabels_uns=["(Sub)Sections","Figures","Equations"],
                     xslice=stats_norm.id,
                     incinlines=False,
                     redtext=False,
                     trackable="N",
                     colset="JJsunset",
                     title="Cumulative number of (sub)sections/figures/equations by commit",
                     annotate=True,
                     logy=True,
                    )
f_n_by_commit.savefig(plotdir+'n_by_commit.png',bbox_inches = 'tight',pad_inches = 0.15)
f_n_by_commit.savefig(plotdir+'n_by_commit_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_p_by_commit, p_by_commit = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_commit(p_by_commit,
                     yslices_uns=[stats_norm.n_page_total,stats_norm.n_page_content,stats_norm.n_chapters],
                     ylabels_uns=["Pages (Total)","Pages (Body + Appendix)","Chapters"],
                     xslice=stats_norm.id,
                     incinlines=False,
                     redtext=False,
                     trackable="N",
                     colset="JJvibrancy",
                     title="Cumulative number of pages/chapters by commit",
                     annotate=True,
                     logy=False,
                    )
f_p_by_commit.savefig(plotdir+'p_by_commit.png',bbox_inches = 'tight',pad_inches = 0.15)
f_p_by_commit.savefig(plotdir+'p_by_commit_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_w_per_commit, w_per_commit = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_commit(w_per_commit,
                     yslices_uns=[per_commits["w_text"],per_commits["w_total"],per_commits["w_caption"],per_commits["n_inlines"],per_commits["w_header"]],
                     ylabels_uns=["Words in text","Total words","Words in captions","In-line math symbols","Words in headers"],
                     xslice=stats_norm.id,
                     redtext=[stats_norm_step.id,per_commits["step_w_redtext"]],
                     trackable="$\Delta$N\n words",
                     colset="JJcool",
                     title="Change in word-count per commit",
                     annotate=False,
                     logy=False,
                     percommit=True,
                    )
f_w_per_commit.savefig(plotdir+'w_per_commit.png',bbox_inches = 'tight',pad_inches = 0.15)
f_w_per_commit.savefig(plotdir+'w_per_commit_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_n_per_commit, n_per_commit = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_commit(n_per_commit,
                     yslices_uns=[per_commits["n_headers"],per_commits["n_figures"],per_commits["n_equations"]],
                     ylabels_uns=["(Sub)Sections","Figures","Equations"],
                     xslice=stats_norm.id,
                     redtext=False,
                     trackable="$\Delta$N\n items",
                     colset="JJsunset",
                     title="Change in number of (sub)sections/figures/equations per commit",
                     annotate=False,
                     logy=False,
                     percommit=True,
                    )
f_n_per_commit.savefig(plotdir+'n_per_commit.png',bbox_inches = 'tight',pad_inches = 0.15)
f_n_per_commit.savefig(plotdir+'n_per_commit_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_p_per_commit, p_per_commit = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_commit(p_per_commit,
                     yslices_uns=[per_commits["n_page_total"],per_commits["n_page_content"],per_commits["n_chapters"]],
                     ylabels_uns=["Pages (Total)","Pages (Body + Appendix)","Chapters"],
                     xslice=stats_norm.id,
                     redtext=False,
                     trackable="$\Delta$N\n pages",
                     colset="JJvibrancy",
                     title="Change in number of pages/chapters per commit",
                     annotate=False,
                     logy=False,
                     percommit=True,
                    )
f_p_per_commit.savefig(plotdir+'p_per_commit.png',bbox_inches = 'tight',pad_inches = 0.15)
f_p_per_commit.savefig(plotdir+'p_per_commit_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_r_per_commit, r_per_commit = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_commit(r_per_commit,
                     yslices_uns=[tot_rate_by_commit,txt_rate_by_commit],
                     ylabels_uns=["Total word rate","Text word rate"],
                     xslice=stats_norm.id,
                     redtext=False,
                     trackable="Rate\n $(wd^{-1})$",
                     colset="JJaquasalmon",
                     title="Writing rate per commit",
                     annotate=False,
                     logy=False,
                     percommit=True,
                    )
f_r_per_commit.savefig(plotdir+'r_per_commit.png',bbox_inches = 'tight',pad_inches = 0.15)
f_r_per_commit.savefig(plotdir+'r_per_commit_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

print("Making plots Vs time.....")
f_w_by_day, w_by_day = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_day(w_by_day,
                     yslices_uns=[stats_norm.w_text,stats_norm.w_total,stats_norm.w_caption,stats_norm.n_inlines,stats_norm.w_header],
                     ylabels_uns=["Words in text","Total words","Words in captions","In-line math symbols","Words in headers"],
                     xslice=dsfc,
                     trackable="Words",
                     redtext=[True,stats_norm.w_redtext],
                     incinlines=inc_inlines,
                     colset="JJcool",
                     title="Cumulative word-count over time",
                     logy=False,
                    )
f_w_by_day.savefig(plotdir+'w_by_day.png',bbox_inches = 'tight',pad_inches = 0.15)
f_w_by_day.savefig(plotdir+'w_by_day_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_n_by_day, n_by_day = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_day(n_by_day,
                     yslices_uns=[stats_norm.n_headers,stats_norm.n_figures,stats_norm.n_equations],
                     ylabels_uns=["(sub)sections","Figures","Equations"],
                     xslice=dsfc,
                     trackable="N",
                     redtext=[False],
                     incinlines=inc_inlines,
                     colset="JJsunset",
                     title="Cumulative number of (sub)sections/figures/equations over time",
                     logy=False,
                    )
f_n_by_day.savefig(plotdir+'n_by_day.png',bbox_inches = 'tight',pad_inches = 0.15)
f_n_by_day.savefig(plotdir+'n_by_day_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_p_by_day, p_by_day = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_day(p_by_day,
                     yslices_uns=[stats_norm.n_page_total,stats_norm.n_page_content,stats_norm.n_chapters],
                     ylabels_uns=["Pages (Total)","Pages (Body + Appendix)","Chapters"],
                     xslice=dsfc,
                     trackable="N",
                     redtext=[False],
                     incinlines=inc_inlines,
                     colset="JJvibrancy",
                     title="Cumulative number of pages/chapters over time",
                     logy=False,
                    )
f_p_by_day.savefig(plotdir+'p_by_day.png',bbox_inches = 'tight',pad_inches = 0.15)
f_p_by_day.savefig(plotdir+'p_by_day_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

f_r_by_day, r_by_day = plt.subplots(figsize=(22.74, 12.29)) #1080p once pad tightening is applied...
make_graph_by_day(r_by_day,
                     yslices_uns=[tot_rate_by_commit.expanding(1).mean(),txt_rate_by_commit.expanding(1).mean()],
                     ylabels_uns=["Total word rate","Text word rate"],
                     xslice=dsfc,
                     trackable="Rate\n $(wd^{-1})$",
                     redtext=[False],
                     incinlines=inc_inlines,
                     colset="JJaquasalmon",
                     title="Writing rate over time",
                     logy=False,
                    )
f_r_by_day.savefig(plotdir+'r_by_day.png',bbox_inches = 'tight',pad_inches = 0.15)
f_r_by_day.savefig(plotdir+'r_by_day_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail

print("Calculating Sentiment.....")
f_sentiment, s_by_day = plt.subplots(figsize=(22.74, 12.29))
make_sentiment(s_by_day,
               yslice=stats_norm.sentiment,
               xslice=dsfc,
               xlabel="Days since first commit",
               markersize=10000/len(dsfc),
               colset="JJrg",
               title="Writing Sentiment",
              )
f_sentiment.savefig(plotdir+'s_by_day.png',bbox_inches = 'tight',pad_inches = 0.15)
f_sentiment.savefig(plotdir+'s_by_day_thumb.png',bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail
print("Ooft")


#Lastly lets make a wordcloud
frequencies = {}
with open(wordfreqfile) as f:
    for line in f:
       (key, val) = line.split(": ")
       frequencies[str(key)] = int(val)
        
boring_words=[
    "the",
    "of",
    "and",
    "to",
    "in",
    "is",
    "a",
    "for",
    "are",
    "with",
    "as",
    "on",
    "by",
    "from",
    "this",
    "at",
]

for key in boring_words:
    if key in frequencies:
        del frequencies[key]
print("Generating word-cloud with "+str(len(frequencies))+" words")

mask = np.array(Image.open(colourmap)) #Simple jet shapes to fit the wordcloud to
overlay = np.array(Image.open(cm_overlay)) #Overlay containing internal small jets and feynman lines
colourmask = np.array(Image.open(cm_colourmask)) #3 block colour diagram to clean up word colouring

wordcloud_thesis = cloud.WordCloud(background_color="white", mode="RGBA", max_words=max_cloudwords, mask=mask).fit_words(frequencies)

# create coloring from image
image_colors = cloud.ImageColorGenerator(colourmask)
f_wordmap, a_wmp = plt.subplots(figsize=(22.74, 12.29))
a_wmp.imshow(wordcloud_thesis.recolor(color_func=image_colors), interpolation="none")
a_wmp.imshow(overlay,alpha=0.3)

a_wmp.text(0.42,0.62,r"$\bar{t}$",horizontalalignment='center',verticalalignment='center', transform=a_wmp.transAxes, fontsize=16,color="black")
a_wmp.text(0.32,0.7,r"$w^{-}$",horizontalalignment='center',verticalalignment='center', transform=a_wmp.transAxes, fontsize=16,color="black")
a_wmp.text(0.31,0.95,r"$\ell^{-}$",horizontalalignment='center',verticalalignment='center', transform=a_wmp.transAxes, fontsize=16,color="black")
a_wmp.text(0.125,0.785,r"$\nu$",horizontalalignment='center',verticalalignment='center', transform=a_wmp.transAxes, fontsize=16,color="black")
a_wmp.text(0.51,0.905,r"Leptonic $b$-jet",horizontalalignment='center',verticalalignment='center', transform=a_wmp.transAxes, fontsize=18,color="#41a043")
a_wmp.text(0.515,0.25,r"Hadronic top",horizontalalignment='center',verticalalignment='center', transform=a_wmp.transAxes, fontsize=18,color="#ee524b")
a_wmp.text(0.735,0.65,r"Additonal jet",horizontalalignment='center',verticalalignment='center', transform=a_wmp.transAxes, fontsize=18,color="#3f65fb")

a_wmp.axis("off")

plt.savefig(plotdir+"wordcloud.png", format="png", bbox_inches='tight', pad_inches=0.15)
plt.savefig(plotdir+'wordcloud_thumb.png',format="png", bbox_inches = 'tight',pad_inches = 0.15,dpi=30) #Additionally save low-res thumbnail
