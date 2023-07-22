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
    from js_finder import bdsp_coin_flip
    bdsp_coin_flip.main()
  `);
}
main().then((_) => enableElements());

function enableElements() {
  notice_footer.innerHTML = "Page Loaded.";
}

let last_flip = 0;
let start;

start_button.onclick = () => {
  start_button.disabled = true;
  timer.value = 0;
  start = Date.now();
  setInterval(
    function () {
      timer.value = (Date.now() - start) % 1018;
    },
    1
  );
}

let diff;
let adv;

let intervals = [];
let observations = [];

coin_flip_button.onclick = () => {
  let now = Date.now();
  diff = now - last_flip;
  adv = Math.floor((now - start) / 1018) - Math.floor((last_flip - start) / 1018) + 1;
  last_flip = now;
  heads_button.disabled = false;
  tails_button.disabled = false;
  timer_position.value = timer.value;
}

heads_button.onclick = () => {
  addFlip(0);
}

tails_button.onclick = () => {
  addFlip(1);
}

function addFlip(flip) {
  intervals.push(adv);
  observations.push(flip);
  pyodide.runPython(
    `py_bits_known, py_progress_string = bdsp_coin_flip.progress(${JSON.stringify(intervals)})`
  );
  progress_label.innerHTML = pyodide.runPython('py_progress_string');
  data_label.innerHTML += `${"HT"[flip]} - ${diff/1000} - ${diff/1018} - ${adv}<br>`;
  heads_button.disabled = true;
  tails_button.disabled = true;
  if (pyodide.runPython("py_bits_known") == 128) {
    coin_flip_button.disabled = true;
    progress_label.innerHTML = pyodide.runPython(
      `bdsp_coin_flip.solve(${JSON.stringify(intervals)}, ${JSON.stringify(observations)})`
    );
  }
}