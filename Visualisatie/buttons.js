// <ul id="nav">

// <li><a href="#">Complete time table</a></li>

var nrStudents = 609
var nrCourses = 29

for(var i = 0; i < nrStudents; i++) {
	var li = document.createElement("LI");
	var a = document.createElement("A");
	var filename = "Student"+toString(i);
	a.innerText += filename;
	li.appendChild(a);
	li.href += "fillTable("+filename+".json)";
	document.getElementById("students").appendChild(li);
}

for(var i = 0; i < nrCourses; i++) {
	var li = document.createElement("LI");
	var a = document.createElement("A");
	var filename = "course"+toString(i);
	a.innerText += filename;
	li.appendChild(a);
	li.href += "fillTable("+filename+".json)";
	document.getElementById("courses").appendChild(li);
}
	

