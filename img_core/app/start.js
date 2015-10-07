var thrust = require('node-thrust');
var path = require('path');

thrust(function(err, api) {
	// var url = 'file://'+path.resolve(__dirname, 'start.html');
	var url = 'http://localhost:8000';
  var window = api.window({
    root_url: url,
    size: {
      width: 640,
      height: 480,
    }
  });
  window.show();
  window.focus();
});
