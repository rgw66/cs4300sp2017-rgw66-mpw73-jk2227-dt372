/**
 * Created by rgw66 on 4/14/17.
 */

var selected_words = [];
var wc_selection = function(e){
    $("#submit_button").fadeIn(200);
    if (e.target.className == "wc_word") {
        selected_words.push(e.target.id);
        e.target.className = "wc_selected";
    }else{
        var i = selected_words.indexOf(e.target.id);
        selected_words.splice(i,1);
        e.target.className = "wc_word";
    }
};

var submit_form = function(){
    var selection = selected_words.join(" ");
    $("#input").val(selection);
    $("#wc_form").submit();
};

var show_words = function(e){
    $("#main_head").fadeOut(200);
    $("#main_page").delay(200).fadeIn(300);
};