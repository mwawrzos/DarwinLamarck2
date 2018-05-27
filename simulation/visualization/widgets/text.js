/**
 * Created by marek on 30.04.2017.
 * Based on mesa/examples/Flockers/flockers/simple_continuous_canvas.js
 */

//noinspection JSUnusedGlobalSymbols
var VerySimpleSpan = function () {
    this.id = Math.random();
    var span = "<span id='" + this.id + "'></span>";
    $("body").append(span);

    //noinspection JSUnusedGlobalSymbols
    this.render = function (data) {
        document.getElementById(this.id).innerHTML = data;
    };

    //noinspection JSUnusedGlobalSymbols
    this.reset = function () {
        document.getElementById(this.id).innerHTML = "";
    };
};
