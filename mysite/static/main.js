/**
 * Created by rgw66 on 4/14/17.
 */

var selected_words = [];
var wc_selection = function(e){
    if (e.target.className == "wc_word") {
        selected_words.push(e.target.id);
        e.target.className = "wc_selected";
        // console.log(selected_words);
    }else{
        var i = selected_words.indexOf(e.target.id);
        selected_words.splice(i,1);
        e.target.className = "wc_word";
        // console.log(selected_words);
    }
};

var submit_form = function(){
    var selection = selected_words.join(" ");
    document.getElementById("input").value = selection;
    // console.log(document.getElementById("input").value);
    document.getElementById("wc_form").submit();
};