let pyodide;
async function main() {
  pyodide = await loadPyodide();
  await pyodide.loadPackage("micropip");
  await pyodide.loadPackage("numpy");
  await pyodide.loadPackage("typing-extensions");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install(
    "./../wheels/numba_pokemon_prngs-0.1.0-py3-none-any.whl"
  );
  await micropip.install("./../wheels/js_finder-0.1.0-py3-none-any.whl");
  await pyodide.runPython(`
    from js_finder import bdsp_seed_finder
    bdsp_seed_finder.main()
  `);
}
main().then((_) => enableElements());

function enableElements() {
  notice_footer.innerHTML = "Page Loaded.";
}

function populateDevices() {
  select.innerHTML = "";
  navigator.mediaDevices
    .getUserMedia({
      video: true,
    })
    .then(async () => {
      try {
        const mediaDevices = await navigator.mediaDevices.enumerateDevices();
        mediaDevices.forEach((mediaDevice) => {
          if (mediaDevice.kind == "videoinput") {
            const option = document.createElement("option");
            option.text = mediaDevice.label;
            option.value = mediaDevice.deviceId;
            select.appendChild(option);
            select.value = option.value;
          }
        });
      } catch (error) {
        console.error(error);
      }
    })
    .then(() => {
      loadVideoStream();
    });
}
refresh_button.onclick = populateDevices;

function loadVideoStream() {
  navigator.mediaDevices
    .getUserMedia({
      video: {
        deviceId: { exact: select.value },
      },
    })
    .then((stream) => {
      video.srcObject = stream;
    });
}

select.onchange = loadVideoStream;

populateDevices();

let recorder;
function startRecording() {
  const stream = video.srcObject;
  recorder = new MediaRecorder(stream);
  let data = [];

  recorder.ondataavailable = (event) => {
    data.push(event.data);
  };
  recorder.start();

  let stopped = new Promise((resolve, reject) => {
    recorder.onstop = resolve;
    record_button.innerText = "Stop Recording";
    record_button.onclick = () => {
      record_button.innerText = "Record";
      record_button.onclick = startRecording;
      recorder.stop();
    };
  });

  stopped.then(() => {
    let recordedBlob = new Blob(data, { type: "video/mp4" });
    video_result.src = URL.createObjectURL(recordedBlob);
  });
}

record_button.onclick = startRecording;

blink_button.onclick = () => {
  let blink = document.createElement("div");
  let time = document.createElement("a");
  let blink_type = document.createElement("select");
  time.innerText = video_result.currentTime;
  let single = document.createElement("option");
  single.text = "Single";
  single.value = 0;
  let double = document.createElement("option");
  double.text = "Double";
  double.value = 1;
  blink_type.appendChild(single);
  blink_type.appendChild(double);
  blink.appendChild(time);
  blink.appendChild(blink_type);
  blink.appendChild(document.createElement("br"));
  results.appendChild(blink);
};

calculate_button.onclick = () => {
  let data = [];
  let children = results.children;
  for (let i = 0; i < children.length; i++) {
    let blink = children[i];
    let time = parseFloat(blink.children[0].text);
    let blink_type = blink.children[1].value;
    data.push([time, blink_type]);
  }
  notice_footer.innerHTML = pyodide.runPython(
    `bdsp_seed_finder.calc_seed(((${data
      .map((e) => e.join(","))
      .join("),(")})))`
  );
};
