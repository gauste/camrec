function toggle_visibility(id) {
   var e = document.getElementById(id);
   if(e.style.display == 'block')
	  e.style.display = 'none';
   else
	  e.style.display = 'block';
}

function show_best_cameras() {
	show('camera_list');
	hide('camera_settings');
	bold('best_cameras');
	unbold('best_settings');
}

function show_best_settings() {
	hide('camera_list');
	show('camera_settings');
	unbold('best_cameras');
	bold('best_settings');
}

function show(id) {
   var e = document.getElementById(id);
   e.style.display = 'block';
}

function hide(id) {
   var e = document.getElementById(id);
   e.style.display = 'none';
}

function bold(id) {
   var e = document.getElementById(id);
   e.style.fontWeight="bold";
}

function unbold(id) {
   var e = document.getElementById(id);
   e.style.fontWeight="normal";
}
