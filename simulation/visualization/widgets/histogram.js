//noinspection JSUnusedGlobalSymbols
/**
 * Created by marek on 28.04.2017.
 */

var Histogram = function(bins, canvas_width, canvas_height) {
    // Create the elements

    // Create the tag:
    var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
    canvas_tag += "style='border:1px dotted'></canvas>";
    // Append it to body:
    var canvas = $(canvas_tag)[0];
    $("body").append(canvas);
    // Create the context and the drawing controller:
    var context = canvas.getContext("2d");

    // Prep the chart properties and series:
    var datasets = [{
        label: "Data",
        fillColor: "rgba(151,187,205,0.5)",
        strokeColor: "rgba(151,187,205,0.8)",
        highlightFill: "rgba(151,187,205,0.75)",
        highlightStroke: "rgba(151,187,205,1)",
        data: []
    }];

    // Add a zero value for each bin
    //noinspection JSUnusedLocalSymbols
    for (var _ in bins)
        datasets[0].data.push(0);

    var data = {
        labels: bins,
        datasets: datasets
    };

    var options = {
        scaleBeginsAtZero: true,
        animationSteps: 1
    };

    // Create the chart object
    var chart = Chart.Bar(context, {
        data: data,
        options: options
    })

    //noinspection JSUnusedGlobalSymbols
    this.render = function (data) {
        for (var i in data) { //noinspection JSUnfilteredForInLoop
            chart.config.data.datasets[0].data[i].value = data[i];
        }
        chart.update();
    };

    //noinspection JSUnusedGlobalSymbols
    this.reset = function() {
        chart.destroy();
        chart = Chart.Bar(context, {
            data: data,
            options: options
        })
    };
};
