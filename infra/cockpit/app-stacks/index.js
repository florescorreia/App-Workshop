"use strict";
const helper = "/usr/local/libexec/cockpit-app-stacks";
const message = document.getElementById("message");
const rows = document.getElementById("stacks");
let busy = false;
async function refresh() {
  if (busy) return;
  busy = true;
  document.getElementById("refresh").disabled = true;
  try {
    const data = JSON.parse(await cockpit.spawn([helper, "list"], {err: "message"}));
    rows.replaceChildren();
    for (const stack of data) {
      const row = document.createElement("tr");
      for (const value of [stack.description, stack.state]) {
        const cell = document.createElement("td"); cell.textContent = value; row.append(cell);
      }
      const actions = document.createElement("td");
      for (const verb of ["start", "stop"]) {
        const button = document.createElement("button");
        button.textContent = verb === "start" ? "Start" : "Stop";
        button.addEventListener("click", async () => {
          if (busy) return;
          busy = true;
          document.querySelectorAll("button").forEach(b => b.disabled = true);
          message.textContent = `${button.textContent}: ${stack.description}…`;
          try {
            await cockpit.spawn([helper, verb, stack.unit], {err: "message"});
            message.textContent = `${stack.description}: ${verb === "start" ? "started" : "stopped"}.`;
          } catch (error) { message.textContent = error.message; }
          finally { busy = false; await refresh(); }
        });
        actions.append(button);
      }
      row.append(actions); rows.append(row);
    }
    if (!data.length) message.textContent = "No application stacks deployed for this account yet.";
  } catch (error) { message.textContent = error.message; }
  finally {
    busy = false;
    document.querySelectorAll("button").forEach(b => b.disabled = false);
  }
}
document.getElementById("refresh").addEventListener("click", refresh);
refresh();
