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
    from js_finder import swsh_npc_calibration
    swsh_npc_calibration.main()
  `);
}
main().then((_) => enableElements());

function enableElements() {
  motions_input.disabled = false;
  reident_motions_input.disabled = false;
  reident_seed_0_input.disabled = false;
  reident_seed_1_input.disabled = false;
  min_advance.disabled = false;
  max_advance.disabled = false;
  min_npcs.disabled = false;
  max_npcs.disabled = false;
  npc_seed_0_input.disabled = false;
  npc_seed_1_input.disabled = false;
  notice_footer.innerHTML = "Page Loaded.";
}

motions_input.oninput = () => {
  motions_progress.innerText = `${motions_input.value.length}/128`;
}
reident_motions_input.oninput = () => {
  reident_motions_progress.innerText = `${reident_motions_input.value.length}/${Math.ceil(Math.log2(parseInt(max_advance.value) - parseInt(min_advance.value)))}`;
}
min_advance.oninput = reident_motions_input.oninput;
max_advance.oninput = reident_motions_input.oninput;

submit_button.onclick = () => {
  seed_results.innerHTML = pyodide.runPython(`swsh_npc_calibration.find_seed('${motions_input.value}')`);
}
reident_submit_button.onclick = () => {
  reident_results.innerHTML = pyodide.runPython(`swsh_npc_calibration.find_advance('${reident_motions_input.value}', ${min_advance.value}, ${max_advance.value}, 0x${reident_seed_0_input.value}, 0x${reident_seed_1_input.value})`);
}

new_data_point.onclick = () => {
  let data_point = document.createElement('div');
  data_point.innerHTML = `
  <button onclick="deleteHandler(event)" class="button-1">Delete</button>
  <input type="number" name="menu_exit" value="0"/>
  <label for="menu_exit"> - Menu Exit</label>
  <input type="number" name="menu_enter" value="0"/>
  <label for="menu_enter"> - Menu Enter</label>
  `;
  npc_data.appendChild(data_point);
}

npc_submit_button.onclick = () => {
  let data = [];
  for (let i = 0; i < npc_data.children.length; i++) {
    let data_point = npc_data.children[i];
    data.push(
      [
        parseInt(data_point.children[1].value),
        parseInt(data_point.children[3].value),
      ]
    )
  }
  npc_results.innerHTML = pyodide.runPython(`swsh_npc_calibration.find_npc(${JSON.stringify(data)}, ${min_npcs.value}, ${max_npcs.value}, 0x${npc_seed_0_input.value}, 0x${npc_seed_1_input.value})`);
}

function deleteHandler(e) {
  e.target.parentElement.parentElement.removeChild(e.target.parentElement);
}