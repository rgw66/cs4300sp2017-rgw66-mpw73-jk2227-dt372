/**
 * Created by rgw66 on 4/14/17.
 */
var color = d3.scaleLinear().domain([-1,1])
      .interpolate(d3.interpolateHcl)
      .range([d3.rgb("#F4002D"), d3.rgb("#1AF40A")]);

var selected_words = [];
var wc_selection = function(e){
    if (e.target.className == "wc_word") {
        if (selected_words.indexOf(e.target.id) == -1) {
            selected_words.push(e.target.id);
            e.target.className = "wc_selected";
        }
    }else if (e.target.className == "wc_selected"){
        var i = selected_words.indexOf(e.target.id);
        selected_words.splice(i,1);
        e.target.className = "wc_word";
    }

    var selection = selected_words.join(" ");
    $("#input").val(selection);
};

var refine_words = function(){
        $.ajax({
            url: "/pt/refine",
            type:"GET",
            data: {
                words: selected_words.join(" ")
            },
            success: function (result) {
                $("#refine_form").slideUp("fast", function(){});
                setTimeout(function(){
                    $("#hotel_refine").empty();
                    $("#airbnb_refine").empty();
                    var hotel_words = result['hotel_words'];
                    var airbnb_words = result['airbnb_words'];
                    if (hotel_words.length == 0){
                        hotel_words = ["No Refining Words Available", "Try Selecting More Words"]
                    }
                    if (airbnb_words.length == 0){
                        airbnb_words = ["No Refining Words Available", "Try Selecting More Words"]
                    }
                    hotel_words.forEach(function (d) {
                        $("#hotel_refine").append(
                            '<span class="refine">' + d + '</span>'
                        )
                    });
                    airbnb_words.forEach(function (d) {

                        $("#airbnb_refine").append(
                            '<span class="refine">' + d + '</span>'
                        )
                    });
                $("#refine_form").slideDown("fast", function(){});
                }, 500);
            }
        });
};

var submit_form = function(e) {
    var element;
    if (e.target.className == "refine") {
        element = e.target.parentNode
    } else {
        element = e.target
    }
    if ($(element).hasClass("selected")){
        element.childNodes.forEach(function (elem) {
            if (elem.className == "refine") {
                selected_words.splice(selected_words.indexOf(elem))
            }
        });
        $(element).removeClass("selected");
    }else{
        var select = 0;
        element.childNodes.forEach(function (elem) {
            if (elem.className == "refine") {
                if (selected_words.indexOf(elem.innerHTML) == -1) {
                    if (elem.innerHTML!="No Refining Words Available" && elem.innerHTML!="Try Selecting More Words") {
                        select = 1;
                        selected_words.push(elem.innerHTML)
                    }
                }
            }
        });
        if (select) {
            $(element).addClass("selected");
        }
    }
    console.log(selected_words)
    var selection = selected_words.join(" ");
    $("#input").val(selection);
};

var show_words = function(e){
    $("#main_head").fadeOut(200);
    $("#main_page").delay(200).slideDown(300);
};

var change_list = function(e){
    if (e.target.value == "hotel-airbnb"){
        $("#airbnb_output").delay(300).fadeIn(300);
        $("#total_output").fadeOut(300);
        $("#hotel_output").delay(300).fadeIn(200);
    }else{
        $("#airbnb_output").fadeOut(300);
        $("#hotel_output").fadeOut(300);
        $("#total_output").delay(300).fadeIn(200);

    }
};

$(document).ready(function(){
    d3.selectAll('.sentiments').each(function(){
        this.style = "background-color: " + color(this.innerHTML) + ";"
    });

    $('.toggle-review').on('click', function() {  
        $(this).children('.review').toggle();
        curr_text = $(this).children('.show-hide').text(); 
        if (curr_text.indexOf('Show') > -1){
            new_text = curr_text.replace("Show", "Hide");
        }
        else{
            new_text = new_text.replace("Hide", "Show");
        }
        curr_text = $(this).children('.show-hide').text(new_text); 
    });
});





