// This file is used to create all the buttons and their links in the drop 
// down menu's

var nrStudents = 609
var nrCourses = 29

// All Students are created
for(var i = 0; i < nrStudents; i++) {
	var li = document.createElement("LI");
	var a = document.createElement("A");
	var filename = "student"+(i).toString();
	// function from "visualisatie.js" that redraws the timetable
	var f = "fillTable('Data/"+filename+".json')" 
	a.innerText += filename;
	a.href = "#"
	a.setAttribute('onclick', f);
	li.appendChild(a);
	document.getElementById("students").appendChild(li);
	}

// All courses are created
for(var i = 0; i < nrCourses; i++) {
	var li = document.createElement("LI");
	var a = document.createElement("A");
	var filename = "course"+(i).toString();
	var f = "fillTable('Data/"+filename+".json')"
	a.innerText += filename;
	a.href = "#"
	a.setAttribute('onclick', f);
	li.appendChild(a);
	document.getElementById("courses").appendChild(li);
}
	

