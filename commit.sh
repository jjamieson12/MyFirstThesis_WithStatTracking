#!/bin/bash

#Master script for updating stat plots and adding them to the current commit, run this instead of regular git commit command
#Usage guide: 'bash commit.sh "your commit message" commit_sentiment_value [on the scale 1(sad) to 10(happy)]'

LoadingPhrases=("muse on the futility of life" "wonder at the enormity of the universe" "have a little cry" "think about the immortality of the crab" "imagine all the better things you could be doing with your time" "try solving the heirarchy problem" "get a fucking grip")
LoadingPhrase=${LoadingPhrases[$(printf "%.0f\n" `echo "scale=2 ; $RANDOM / 32767 * (${#LoadingPhrases[@]} - 1)" | bc`)]}

countpages()
{
    make qcontent #Make content only 
    #numpage_content_only=$(mdls -name kMDItemNumberOfPages -raw JJthesis.pdf) #Much nicer way using pdf metadata but only works on mac :(

    if [[ -f JJthesis.pdf ]]; then
	numpage_content_only=$(pdftotext JJthesis.pdf - | grep -c $'\f')
    else
	echo "Compilation failed, check LaTeX is bug free before committing in a stat-trackable way"
	exit 1
    fi
    
    make clean
    make quietly #make fully

    if [[ -f JJthesis.pdf ]]; then
	numpage_total=$(pdftotext JJthesis.pdf - | grep -c $'\f')
    else
	echo "Compilation failed, check LaTeX is bug free before committing in a stat-trackable way"
	exit 1
    fi
}

outstanding_changes=$(git status | grep "Changes not staged for commit" | wc -l)
if [[ ! ${outstanding_changes} == 0 ]]; then 
    echo "Caution there are changes in the working repo that haven't been staged:\n $(git status | grep -A 1000 "Changes not staged for commit")"
    echo "Are you sure you want to commit anyway?"
    read -p '[y/n]: ' cont

    if [[ ! ${cont} == "y" ]]; then
	echo "quiting unceremoniously"
	exit 4
    fi
fi

current_date="$(date +"%d-%m-%Y")"
current_month="$(date +%b)"
epoch_time="$(date +%s)"
epoch_days="$((${epoch_time}/86400))"

if [[ "$#" -ne 2 ]]; then
    echo "Please supply 2 arguments of the form: 'your commit message' commit_sentiment_value [on the scale 1(sad) to 10(happy)]"
    exit 2
else
    echo "Commit message will be: ${1}"
    echo "Commit sentiment is: ${2}/10"
    echo "Date of commit: ${current_date}"
fi

echo "Counting pages... This requires compiling the full document twice, while you wait why not ${LoadingPhrase}" 
countpages

echo "The number of pages of content is: ${numpage_content_only}"
echo "The total number of pages is: ${numpage_total}"

echo "Counting words... This shouldn't take too long" 

total_string="$(texcount -inc -brief JJthesis.tex | tail -1)"
appendix_string="$(texcount -inc -brief JJthesis.tex | grep "appendices")"
n_chapters="$(texcount -inc -brief JJthesis.tex | grep -c "Section_")"

num='([0-9^]+)' #regexps for lovely bash parsing (any number)
nonum='[^0-9^]+' #Match any other character
anything='.*' #Match anything
plus='\+' #Match a plus sign


if [[ ${total_string} =~ $num$plus$num$plus$num$plus$num$nonum$num$nonum$num$nonum$num$nonum$num$nonum ]] ; then
    w_text=${BASH_REMATCH[1]}
    w_header=${BASH_REMATCH[2]}
    w_caption=${BASH_REMATCH[3]}
    w_redtext=${BASH_REMATCH[4]}
    n_headers=${BASH_REMATCH[5]}
    n_figures=${BASH_REMATCH[6]}
    n_inlines=${BASH_REMATCH[7]}
    n_equations=${BASH_REMATCH[8]}
    
elif [[ ${total_string} =~ $num$plus$num$plus$num$nonum$num$nonum$num$nonum$num$nonum$num$nonum ]] ; then
    w_text=${BASH_REMATCH[1]}
    w_header=${BASH_REMATCH[2]}
    w_caption=${BASH_REMATCH[3]}
    w_redtext=0
    n_headers=${BASH_REMATCH[4]}
    n_figures=${BASH_REMATCH[5]}
    n_inlines=${BASH_REMATCH[6]}
    n_equations=${BASH_REMATCH[7]}
    

else
    echo "layout of totals for 'texcount -brief JJthesis.pdf' has changed, please check it and update me"
    exit 3
fi

if [[ ${appendix_string} =~ $num$plus$num$plus$num$plus$num$anything ]] ; then
    let w_appendix=${BASH_REMATCH[1]}+${BASH_REMATCH[2]}+${BASH_REMATCH[3]}+${BASH_REMATCH[4]}
elif [[ ${appendix_string} =~ $num$plus$num$plus$num$anything ]] ; then
    let w_appendix=${BASH_REMATCH[1]}+${BASH_REMATCH[2]}+${BASH_REMATCH[3]}
else
    echo "layout of appendix for 'texcount -brief JJthesis.pdf' has changed, please check it and update me"
    exit 3
fi
let w_total=${w_text}+${w_header}+${w_caption}+${w_redtext}
let w_total_noapp=${w_total}-${w_appendix}

echo "number of chapters is: ${n_chapters}"
echo "number of words in text is: ${w_text}"
echo "number of words in headers is: ${w_header}"
echo "number of words in captions is: ${w_caption}"
echo "number of words in red is: ${w_redtext}"
echo "number of headers is: ${n_headers}"
echo "number of figures is: ${n_figures}"
echo "number of inlines is: ${n_inlines}"
echo "number of equations is: ${n_equations}"
echo "number of words in total is: ${w_total}"
echo "number of words in total minus the appendix is: ${w_total_noapp}"

echo "Writing values to json file for pretty plots"

if [[ -f stats/masterStats.json ]]; then
    old_json=stats/masterStats.json
else
    old_json=stats/template.json
fi
commit_id=$(jq '.commit[-1].id + 1' ${old_json})
cp ${old_json} stats/tmp_masterStats.json

jq --argjson id "$commit_id" \
   --arg msg "${1}" \
   --arg date "${current_date}" \
   --argjson e_time "${epoch_time}" \
   --argjson e_days "${epoch_days}" \
   --argjson smnt "${2}" \
   --argjson wtxt "${w_text}" \
   --argjson whed "${w_header}" \
   --argjson wcap "${w_caption}" \
   --argjson wred "${w_redtext}" \
   --argjson wtot "${w_total}" \
   --argjson wtna "${w_total_noapp}" \
   --argjson nhed "${n_headers}" \
   --argjson nfig "${n_figures}" \
   --argjson ninl "${n_inlines}" \
   --argjson neqs "${n_equations}" \
   --argjson nchp "${n_chapters}" \
   --argjson npct "${numpage_content_only}" \
   --argjson nptl "${numpage_total}" \
   '.commit += [{"id": $id, "message": $msg, "date": $date, "epoch_time": $e_time, "epoch_days": $e_days, "sentiment": $smnt, "w_text": $wtxt, "w_header": $whed, "w_caption": $wcap, "w_redtext": $wred, "w_total": $wtot, "w_total_noapp": $wtna, "n_headers": $nhed, "n_figures": $nfig, "n_inlines": $ninl, "n_equations": $neqs, "n_chapters": $nchp, "n_page_content": $npct, "n_page_total": $nptl}]' stats/tmp_masterStats.json > stats/masterStats.json

rm stats/tmp_masterStats.json

echo "done"
echo "Word counts and other trackable stats written to file: ./stats/masterStats.json"

echo "Updating word map at stats/master_wordcloud.txt"
texcount -inc -brief -freq JJthesis.tex | grep -A 1000 -- "---" | sed '1d; $d' > ./stats/master_wordcloud.txt

htmlflag=""
if [[ ! -f stats/${current_month}_fullStats.html ]]; then
    echo "Updating monthly snapshot at stats/snapshots/${current_month}_fullStats.html"
    texcount -inc -html -out=stats/snapshots/${current_month}_fullStats.html JJthesis.tex
    htmlflag="html snapshot, "
fi

echo "Updating plots inside stats/figures/"
LoadingPhrase=${LoadingPhrases[$(printf "%.0f\n" `echo "scale=2 ; $RANDOM / 32767 * (${#LoadingPhrases[@]} - 1)" | bc`)]}
echo "This could take upwards of 30s, while you wait why not ${LoadingPhrase}"

cd scripts
python statPlots.py
cd -

echo "Adding stats, plots, ${htmlflag}and wordmap into git commit"

git status

echo "I've done all I can without knowing your git password, you still need to push this commit to your online repo:"
echo "git push origin master &&"
echo "Or try pressing <up> and <enter> or !! if you really trust me"
history -s "git push origin master"
