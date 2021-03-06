// Based on source: http://bl.ocks.org/dk8996/5538271

// Start variables are entered
var groups = [];
var groupStatus = {
    "SUCCEEDED" : "bar",
    "FAILED" : "bar-failed",
    "RUNNING" : "bar-running",
    "KILLED" : "bar-killed"
};
var groupNames = [ "A1.04","A1.06","A1.08","A1.10","B0.201","C0.110","C1.112" ];
var minDate = new Date("Mon Nov 30 09:00:00 2015");
var maxDate = new Date("Fri Dec 04 19:00:00 2015");

// The starts of all days are defined
var startMo = minDate;
var startTu = d3.time.day.offset(minDate,1);
var startWe = d3.time.day.offset(minDate,2);
var startTh = d3.time.day.offset(minDate,3);
var startFr = d3.time.day.offset(minDate,4);

// The SVG is drawn. Opening timedomain is defined.
var format = "%H:%M";
var timeDomainString = "1week";
var gantt = d3.gantt().taskTypes(groupNames).taskStatus(groupStatus).tickFormat(format).height(450).width(800);

// Not exactly sure what this does...
gantt.timeDomainMode("fixed");
changeTimeDomain(timeDomainString);
gantt(groups);

// Function for looking at different days
function changeTimeDomain(timeDomainString) {
    this.timeDomainString = timeDomainString;

    switch (timeDomainString) {
    case "mo":
    format = "%H:%M";
    gantt.timeDomain([startMo, d3.time.hour.offset(startMo,10)]);
    break;
    case "tu":
    format = "%H:%M";
    gantt.timeDomain([startTu, d3.time.hour.offset(startTu,10)]);
    break;
    case "we":
    format = "%H:%M";
    gantt.timeDomain([startWe, d3.time.hour.offset(startWe,10)]);
    break;
    case "th":
    format = "%H:%M";
    gantt.timeDomain([startTh, d3.time.hour.offset(startTh,10)]);
    break;
    case "fr":
    format = "%H:%M";
    gantt.timeDomain([startFr, d3.time.hour.offset(startFr,10)]);
    break;
    case "1week":
    format = "%a%H:%M";
    gantt.timeDomain([ minDate, maxDate ]);
    break;

    default:
    format = "%H:%M"
    }
    gantt.tickFormat(format);
    gantt.redraw(groups);
}   

function addGroup(startTime, day, room, validity) {
    // Adds a random group to the schedule
    if (day == "mo") {
        date = startMo;
    }
    if (day == "tu") {
        date = startTu;
    }
    if (day == "we") {
        date = startWe;
    }
    if (day == "th") {
        date = startTh;
    }
    if (day == "fr") {
        date = startFr;
    }
    if (validity == "True") {var n = 2;}
    else {var n = 1;}
    var groupStatusKeys = Object.keys(groupStatus);
    var groupStatusName = groupStatusKeys[n];

    groups.push({
    "startDate" : d3.time.hour.offset(date, startTime),
    "endDate" : d3.time.hour.offset(date, startTime+2),
    "taskName" : room,
    "status" : groupStatusName
    });
};

d3.json("Data/main.json", function(json) {
    for(var i = 0; i < json.length; i++) {
        addGroup(
            json[i].startTime, 
            json[i].day,
            json[i].roomName,
            json[i].validity
            )
    }
    gantt.redraw(groups);
})

function fillTable(filename) {
    groups = []
    d3.json(filename, function(json) {
    for(var i = 0; i < json.length; i++) {
        addGroup(
            json[i].startTime, 
            json[i].day,
            json[i].roomName,
            json[i].validity
            )
        }
    gantt.redraw(groups);
    })
}