/**
 * Created by marek on 30.04.2017.
 * Based on mesa/examples/Flockers/flockers/simple_continuous_canvas.js
 */

var AgentVisualization = function (width, height, context) {
    this.draw = function (objects) {
        for (var i = 0; i < objects.length; i++) {
            var p = objects[i];
            this.drawCircle(p.x, p.y, p.r, p.Color, true);   // agent
            // this.drawCircle(p.x, p.y, p.rs, 'green', false); // sight
            this.drawVector(p.x, p.y, p.vx, p.vy, p.v2x, p.v2y);           // vector
        }
    };
    
    this.drawCircle = function (x, y, radius, color, fill) {
        var cx = x * width;
        var cy = y * height;
        var r = radius * width;

        context.beginPath();
        context.arc(cx, cy, r, 0, Math.PI * 2, false);
        context.closePath();

        context.strokeStyle = color;
        context.stroke();

        if (fill) {
            context.fillStyle = color;
            context.fill();
        }
    };

    this.drawVector = function (x, y, vx, vy, v2x, v2y) {
        var cx = x*width;
        var cy = y*width;
        var cvx = vx*width;
        var cvy = vy*width;
        var cv2x = v2x * width;
        var cv2y = v2y * width;

        context.beginPath();
        context.moveTo(cx, cy);
        context.lineTo(cvx, cvy);
        context.stroke();

        context.strokeStyle = '#880000FF'
        context.beginPath();
        context.moveTo(cx, cy);
        context.lineTo(cv2x, cv2y);
        context.stroke()
    };

    this.resetCanvas = function () {
        context.clearRect(0, 0, height, width);
        context.beginPath();
    }
};

//noinspection JSUnusedGlobalSymbols
var VerySimpleContinuousModule = function (canvas_width, canvas_height) {
    var canvas_tag =
        "<canvas width='" + canvas_width + "' height='" + canvas_height + "' style='border:1px dotted'></canvas>";
    var canvas = $(canvas_tag)[0];
    $("body").append(canvas);

    var context = canvas.getContext("2d");
    var canvasDraw = new AgentVisualization(canvas_width, canvas_height, context);

    //noinspection JSUnusedGlobalSymbols
    this.render = function (data) {
        canvasDraw.resetCanvas();
        canvasDraw.draw(data);
    };

    //noinspection JSUnusedGlobalSymbols
    this.reset = function () {
        canvasDraw.resetCanvas();
    };
};
