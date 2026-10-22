/* Visor de pantallas: capa pantalla / atención predicha / puntos de lectura por integrante.
   Adaptado de «Investigacion-pantallas-de-recompra/datos/pagina.js». Lee el objeto global D. */
const NS = "http://www.w3.org/2000/svg";
function el(t, a, txt) { const n = document.createElementNS(NS, t); for (const k in a) n.setAttribute(k, a[k]); if (txt != null) n.textContent = txt; return n; }
document.querySelectorAll(".visor").forEach(function (v) {
  const primero = v.querySelector("[data-p]"); let capa = "atencion", perfil = primero ? primero.dataset.p : "";
  const chk = v.querySelector("input[type=checkbox]"), pie = v.querySelector("[data-pie]");
  function pintar() {
    v.querySelectorAll("[data-c]").forEach(b => b.setAttribute("aria-pressed", b.dataset.c === capa));
    v.querySelectorAll("[data-p]").forEach(b => b.setAttribute("aria-pressed", b.dataset.p === perfil));
    v.querySelector(".perf").hidden = capa !== "lectura";
    pie.textContent = D.pies[capa];
    v.querySelectorAll("svg.ov").forEach(function (s) {
      const k = s.dataset.k, Z = D.zonas[k], marco = s.parentNode;
      marco.querySelector(".sal").hidden = capa !== "atencion";
      marco.querySelector(".base").style.opacity = capa === "lectura" ? .38 : 1;
      s.replaceChildren();
      if (chk.checked) D.pliegues.forEach(function (y) {
        s.append(el("line", { x1: 0, x2: Z.ancho, y1: y, y2: y, stroke: "#FF5A36", "stroke-width": 1.5, "stroke-dasharray": "6 4" }));
        s.append(el("rect", { x: 0, y: y - 15, width: 108, height: 15, fill: "#FF5A36" }));
        s.append(el("text", { x: 4, y: y - 4, "font-size": 10.5, "font-weight": 700, fill: "#fff", "font-family": "system-ui,sans-serif" }, "pliegue a " + y + " px"));
      });
      const cap = v.querySelector('.cap[data-k="' + k + '"]');
      if (capa !== "lectura") { cap.textContent = capa === "atencion" ? "Más claro = más atención predicha." : "Alto del frame: " + Z.alto + " px."; return; }
      const L = D.lectura[k][perfil], vist = {}; L.vistazo[D.vel].forEach(x => vist[x[0]] = x[1]);
      const pts = []; let n = 0;
      L.pasos.forEach(function (p) {
        const z = Z.zonas[p.zona], c = z.caja, cx = (c[0] + c[2]) / 2, cy = (c[1] + c[3]) / 2;
        if (p.estado !== "leida") {
          s.append(el("rect", { x: c[0] - 3, y: c[1] - 3, width: c[2] - c[0] + 6, height: c[3] - c[1] + 6, fill: "none", stroke: "#5A6B64", "stroke-width": 1.5, "stroke-dasharray": "4 3", rx: 4 }));
          return;
        }
        n++; pts.push({ cx, cy, n, r: 10 + Math.min(p.dur, 5) * 3.2, dentro: p.zona in vist, parcial: p.zona in vist && vist[p.zona] < z.palabras && p.zona !== "ilustracion" });
      });
      s.append(el("polyline", { points: pts.map(p => p.cx + "," + p.cy).join(" "), fill: "none", stroke: "#0B3B2E", "stroke-width": 1.5, "stroke-opacity": .55 }));
      pts.forEach(function (p) {
        s.append(el("circle", { cx: p.cx, cy: p.cy, r: p.r, fill: p.dentro ? "#FF5A36" : "#FFFFFF", "fill-opacity": p.dentro ? (p.parcial ? .55 : .9) : .85, stroke: p.dentro ? "#8C1D00" : "#0B3B2E", "stroke-width": 1.5, "stroke-dasharray": p.parcial ? "3 2" : "none" }));
        s.append(el("text", { x: p.cx, y: p.cy + 4, "text-anchor": "middle", "font-size": 12, "font-weight": 750, fill: p.dentro ? "#fff" : "#0B3B2E", "font-family": "system-ui,sans-serif" }, p.n));
      });
      const noLe = L.pasos.filter(p => p.estado !== "leida").map(p => Z.zonas[p.zona].nombre);
      cap.textContent = "Lectura completa estimada: " + L.total + " s." + (noLe.length ? " No lee: " + noLe.join(", ") + "." : "");
    });
  }
  v.querySelectorAll("[data-c]").forEach(b => b.addEventListener("click", function () { capa = b.dataset.c; pintar(); }));
  v.querySelectorAll("[data-p]").forEach(b => b.addEventListener("click", function () { perfil = b.dataset.p; pintar(); }));
  chk.addEventListener("change", pintar);
  pintar();
});
