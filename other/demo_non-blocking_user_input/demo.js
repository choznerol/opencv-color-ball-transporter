const PythonShell = require("python-shell");
const path = require("path");

const libPath = path.resolve(__dirname, "./");
const scriptName = "routine_work_accept_user_input.py";

const options = {
  pythonPath: "python3",
  pythonOptions: ["-u"], // unbuffered：即時顯示 print 結果
  scriptPath: libPath
};

const pyshell = new PythonShell(scriptName, options);

pyshell.send("1"); // send to `sys.stdin`

setTimeout(() => {
  pyshell.send("2");
}, 1000);

setTimeout(() => {
  pyshell.send("4");
}, 3000);

// get message back
pyshell.on("message", function(message) {
  // received a message sent from the Python script (a simple "print" statement)
  console.log(`[${scriptName}] ${message}`);
});
