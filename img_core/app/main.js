// required packages
var app = require('app');  // Module to control application life.
var BrowserWindow = require('browser-window');  // Module to create native browser window.
var globalShortcut = require('global-shortcut'); // https://github.com/atom/electron/blob/master/docs/api/global-shortcut.md
var http = require('http'); // Make web requests to the server process: https://docs.nodejitsu.com/articles/HTTP/clients/how-to-create-a-HTTP-request
var spawn = require('child_process').spawn; // used to make server process

// Report crashes to our server.
require('crash-reporter').start();

///////////////////////////////////
///////////////////////////////////
///////////////
/////////////// DEFINE SERVER SUBPROCESS AND CHECK THAT IT IS RUNNING
/////////////// Keep global variable that can be terminated when other stuff is done.
///////////////
// processes: http://krasimirtsonev.com/blog/article/Nodejs-managing-child-processes-starting-stopping-exec-spawn
// https://nodejs.org/api/child_process.html#child_process_child_process_spawn_command_args_options
// http://www.graemeboy.com/node-child-processes
// https://www.npmjs.com/package/virtualenv

// 1. define host (maybe with random url identifier)
var port = '8000';
var host = 'localhost:' + port;

// 2. define environment vars
var env = process.env;
var env_duplicate = {};

// Duplicate the parent's environment object
var dummy_env;
for (dummy_env in env) {
  env_duplicate[dummy_env] = env[dummy_env];
}

// Now, extend this with some new variables:
env_duplicate['PYTHONPATH'] = '.';
// env_duplicate['DJANGO_SETTINGS_MODULE'] = 'img_gui.woot.settings';
env_duplicate['DJANGO_SETTINGS_MODULE'] = 'testsite.settings';

// 3. spawn server process
// var tornado_proc = spawn('python3.4', ['./img_gui/tornado_main.py'], {env: env_duplicate});
var tornado_proc = spawn('python3.4', ['./testsite/tornado_main.py'], {env: env_duplicate});
console.log('tornado process id: ' + tornado_proc.pid);

tornado_proc.stdout.on('data',
  function (data) {
	  console.log('tail output: ' + data);
  }
);

///////////////////////////////////
///////////////////////////////////
///////////////
/////////////// SET UP BROWSER WINDOW THAT WILL RUN THE INTERFACE
/////////////// Some keyboard shortcuts will control window events. Others will send requests to
/////////////// the server process via "http"
///////////////

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
var mainWindow = null;

// Quit when all windows are closed.
app.on('window-all-closed', function() {
  // On OS X it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform != 'darwin') {
    app.quit();
  }
});

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.on('ready', function() {

	///////////////////////////////////
	/////////////// BROWSER WINDOW
	///////////////
	// browser window api: https://github.com/atom/electron/blob/master/docs/api/browser-window.md
	// frameless: https://github.com/atom/electron/blob/master/docs/api/frameless-window.md

  // Create the browser window.
  mainWindow = new BrowserWindow({width: 1024, height: 768, 'title-bar-style': 'hidden'});

  // POINT AT THE SERVER PROCESS URL HERE
	mainWindow.loadUrl('file://' + __dirname + '/startup.html'); // temporary until server process is loaded
	// setTimeout(function() {
	// 	mainWindow.loadUrl('http://' + host + '/');
	// }, 3000);

  // Emitted when the window is closed.
  mainWindow.on('closed', function() {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    mainWindow = null;
		tornado_proc.kill();
  });

	///////////////////////////////////
	/////////////// KEYBOARD SHORTCUTS: https://github.com/atom/electron/blob/master/docs/api/global-shortcut.md
	///////////////
	// using requests to server process: https://docs.nodejitsu.com/articles/HTTP/clients/how-to-create-a-HTTP-request


});

app.on('quit', function () { // when cmd + Q or anything else is pressed
	tornado_proc.kill();
});
