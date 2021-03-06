function centerSimileAjax(date) {
    tl.getBand(0).setCenterVisibleDate(SimileAjax.DateTime.parseGregorianDateTime(date));
}



function setupFilterHighlightControls(div, timeline, bandIndices, theme) {
    var table = document.createElement("table");
    var tr = table.insertRow(0);
    
    // var td = tr.insertCell(0);
    // td.innerHTML = "Show Only:";
    
    // td = tr.insertCell(1);
    // td.innerHTML = "Highlight:";
    
    var handler = function(elmt, evt, target) {
        onKeyPress(timeline, bandIndices, table);
    };
    
    tr = table.insertRow(1);
    tr.style.verticalAlign = "top";
    
    td = tr.insertCell(0);
    
    var input = document.createElement("input");
    input.type = "text";
    input.className="form-control";
    input.placeholder="Show Only"
    SimileAjax.DOM.registerEvent(input, "keypress", handler);
    td.appendChild(input);
    
    for (var i = 0; i < 1; i++) {
        td = tr.insertCell(i + 1);
        
        input = document.createElement("input");
        input.type = "text";
        input.className="form-control";
        input.placeholder="Highlight"
        SimileAjax.DOM.registerEvent(input, "keypress", handler);
        td.appendChild(input);
        
        var divColor = document.createElement("div");
        divColor.style.height = "0.5em";
        divColor.style.background = theme.event.highlightColors[i];
        td.appendChild(divColor);
    

    td = tr.insertCell(tr.cells.length);
    var button = document.createElement("button");
    button.innerHTML = "Clear Filter/Highlight";
    button.className="btn btn-default";
    SimileAjax.DOM.registerEvent(button, "click", function() {
        clearAll(timeline, bandIndices, table);
    });
    td.appendChild(button);
    
    div.appendChild(table);
}
}

var timerID = null;
function onKeyPress(timeline, bandIndices, table) {
    if (timerID != null) {
        window.clearTimeout(timerID);
    }
    timerID = window.setTimeout(function() {
        getfilterinfo()
        gethighlightinfo()
        performFiltering(timeline, bandIndices, table);
    }, 300);
}
function cleanString(s) {
    return s.replace(/^\s+/, '').replace(/\s+$/, '');
}

var event_highlight_list=[]
var event_filter_list=[]


function performFiltering(timeline, bandIndices, table) {
    timerID = null;
    
    var tr = table.rows[1];
    var text = cleanString(tr.cells[0].firstChild.value);
    
    var filterMatcher = null;
    if (text.length > 0) {
        var regex = new RegExp(text, "i");
        filterMatcher = function(evt) {
            var eventid = evt.getProperty('TopicID');
            if (regex.test(evt.getText()) || regex.test(evt.getDescription())){
                //do nothing
                }else{
                    event_filter_list.push(eventid)
                };
            return regex.test(evt.getText()) || regex.test(evt.getDescription());
        };
    }
    
    var regexes = [];
    var hasHighlights = false;
    for (var x = 1; x < tr.cells.length - 1; x++) {
        var input = tr.cells[x].firstChild;
        var text2 = cleanString(input.value);
        if (text2.length > 0) {
            hasHighlights = true;
            regexes.push(new RegExp(text2, "i"));
        } else {
            regexes.push(null);
        }
    }

    
    var highlightMatcher = hasHighlights ? function(evt) {
        var text = evt.getText();
        var description = evt.getDescription();
       
        
        for (var x = 0; x < regexes.length; x++) {
            var regex = regexes[x];
            if (regex != null && (regex.test(text) || regex.test(description))) {
                var eventid = evt.getProperty('TopicID');
                event_highlight_list.push(eventid);
                return x;
            }
        }
        return -1;
    } : null;
    
    for (var i = 0; i < bandIndices.length; i++) {
        var bandIndex = bandIndices[i];
        timeline.getBand(bandIndex).getEventPainter().setFilterMatcher(filterMatcher);
        
        timeline.getBand(bandIndex).getEventPainter().setHighlightMatcher(highlightMatcher);
        
    }
    timeline.paint();
}
function clearAll(timeline, bandIndices, table) {
    var tr = table.rows[1];
    for (var x = 0; x < tr.cells.length - 1; x++) {
        tr.cells[x].firstChild.value = "";
    }
    
    for (var i = 0; i < bandIndices.length; i++) {
        var bandIndex = bandIndices[i];
        timeline.getBand(bandIndex).getEventPainter().setFilterMatcher(null);
        timeline.getBand(bandIndex).getEventPainter().setHighlightMatcher(null);
    }
    for (var i = 0; i < filter_marker_list.length; i++) {
        var marker = filter_marker_list[i];
        marker.setMap(Map);
    }
    
    loadMapMarkers()
    event_highlight_list= [];
    event_filter_list = [];
    console.log(event_highlight_list, event_filter_list)
    timeline.paint();
}

function gethighlightinfo(){
    
    for (var i = 0; i < event_highlight_list.length; i++) {
        var eventid = event_highlight_list[i];
        
        var marker = marker_dict[eventid]
        console.log(marker)
        marker.setIcon("https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_yellow.png")
        ;
        
    }
}

var filter_marker_list = []

function getfilterinfo(){
    
    for (var i = 0; i < event_filter_list.length; i++) {
        var eventid = event_filter_list[i];
        var marker = marker_dict[eventid]

        filter_marker_list.push(marker)
        marker.setMap(null)
    }
}

// theme.event.highlightColors.length