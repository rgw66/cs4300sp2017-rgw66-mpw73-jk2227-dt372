/**
 * Created by rgw66 on 4/14/17.
 */
var color = d3.scaleLinear().domain([-1,1])
      .interpolate(d3.interpolateHcl)
      .range([d3.rgb("#F4002D"), d3.rgb("#1AF40A")]);

var selected_words = [];
var wc_selection = function(e){
    if (e.target.className == "wc_word") {
        selected_words.push(e.target.id);
        e.target.className = "wc_selected";
    }else if (e.target.className == "wc_selected"){
        var i = selected_words.indexOf(e.target.id);
        selected_words.splice(i,1);
        e.target.className = "wc_word";
    }
    // else if (e.target.className == "wc_word hotel"){
    //     selected_words.push(e.target.innerHTML);
    //     e.target.className = "wc_selected hotel";
    // }else if (e.target.className == "wc_word airbnb"){
    //     selected_words.push(e.target.innerHTML);
    //     e.target.className = "wc_selected airbnb";
    // }else if (e.target.className == "wc_selected airbnb") {
    //     var i = selected_words.indexOf(e.target.id);
    //     selected_words.splice(i, 1);
    //     e.target.className = "wc_word airbnb";
    // }else if (e.target.className == "wc_selected hotel") {
    //     var i = selected_words.indexOf(e.target.id);
    //     selected_words.splice(i, 1);
    //     e.target.className = "wc_word hotel";
    // }
    var selection = selected_words.join(" ");
    $("#input").val(selection);
};

var refine_words = function(){
    if ($.trim($("#hotel_refine").html()) == "") {
        $.ajax({
            url: "/pt/refine", success: function (result) {
                var hotel_words = result['hotel_words'];
                var airbnb_words = result['airbnb_words'];
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

                $("#refine_form").slideDown("slow", function(){});
            }
        })
    }
};

var submit_form = function(e){
    var element;
    if (e.target.className == "refine"){
        element = e.target.parentNode
    }else{
        element = e.target
    }

    element.childNodes.forEach(function(elem){
        if (elem.className == "refine"){
            selected_words.push(elem.innerHTML)
        }
    });
    console.log(selected_words)
    var selection = selected_words.join(" ");
    $("#input").val(selection);
    $("#wc_form").submit();
};

var show_words = function(e){
    $("#main_head").fadeOut(200);
    $("#main_page").delay(200).slideDown(300);
};

var change_list = function(e){
    if (e.target.value == "hotel"){
        $("#airbnb_output").fadeOut(200);
        $("#total_output").fadeOut(200);
        $("#hotel_output").delay(300).fadeIn(200);
    }else if (e.target.value == "airbnb"){
        $("#airbnb_output").delay(300).fadeIn(200);
        $("#total_output").fadeOut(200);
        $("#hotel_output").fadeOut(200);
    }else{
        $("#airbnb_output").fadeOut(200);
        $("#total_output").delay(300).fadeIn(200);
        $("#hotel_output").fadeOut(200);
    }
};

$(document).ready(function(){
    d3.selectAll('.sentiments').each(function(){
        console.log(parseInt(this.innerHTML));

        this.style = "background-color: " + color(this.innerHTML) + ";"
    });
});