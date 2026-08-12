(() => {
  const data = window.错题本数据;
  const root = document.getElementById("appRoot");
  if (!root || !data || !Array.isArray(data.questions)) {
    document.body.innerHTML = '<div class="page"><div class="error">未加载到错题数据（window.错题本数据）。</div></div>';
    return;
  }

  const book = data.book || "必刷550";
  const subject = data.subject || "税法一";
  const storageKey = `错题本复习:${subject}:${book}`;
  /** @type {Record<string, boolean>} */
  let reviewed = {};
  try {
    reviewed = JSON.parse(localStorage.getItem(storageKey) || "{}");
  } catch {
    reviewed = {};
  }

  const questions = data.questions.slice().sort((a, b) => a.id - b.id);

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function letters(code) {
    return String(code || "")
      .toUpperCase()
      .replace(/[^A-E]/g, "")
      .split("");
  }

  function renderOptions(q, showWrong, showAnswer) {
    const wrong = new Set(showWrong ? letters(q.wrongPick) : []);
    const right = new Set(showAnswer ? letters(q.answer) : []);
    return `<ul class="options">${Object.keys(q.options || {})
      .sort()
      .map((key) => {
        const classes = ["option"];
        if (wrong.has(key)) classes.push("mark-wrong");
        if (right.has(key)) classes.push("mark-right");
        return `<li class="${classes.join(" ")}"><span class="key">${key}.</span><span>${escapeHtml(
          q.options[key]
        )}</span></li>`;
      })
      .join("")}</ul>`;
  }

  function createCard(q) {
    const card = document.createElement("article");
    card.className = "card";
    const key = String(q.id);
    const state = { wrong: false, answer: false, analysis: false, knowledge: false };

    card.innerHTML = `
      <div class="card-head">
        <span class="badge">第 ${q.id} 题</span>
        <span class="badge muted">${escapeHtml(q.type || "")}</span>
        <span class="source">${escapeHtml(q.source || "")}</span>
        ${q.fromSubmit ? `<span class="badge muted">${escapeHtml(q.fromSubmit)}</span>` : ""}
        <label class="reviewed"><input type="checkbox" data-role="reviewed" ${
          reviewed[key] ? "checked" : ""
        }/> 已复习</label>
      </div>
      <div class="card-body">
        <p class="stem">${escapeHtml(q.stem)}</p>
        <div data-role="options">${renderOptions(q, false, false)}</div>
        <div class="controls">
          <button type="button" class="btn" data-reveal="wrong">上次错选</button>
          <button type="button" class="btn" data-reveal="answer">正确答案</button>
          <button type="button" class="btn" data-reveal="analysis">解析</button>
          <button type="button" class="btn" data-reveal="knowledge">知识点</button>
          <button type="button" class="btn ghost" data-role="collapse">全部收起</button>
        </div>
        <div class="reveal wrong" data-panel="wrong"><h3>上次错选</h3><p>${escapeHtml(
          q.wrongPick || "—"
        )}</p></div>
        <div class="reveal answer" data-panel="answer"><h3>正确答案</h3><p>${escapeHtml(
          q.answer || "—"
        )}</p></div>
        <div class="reveal" data-panel="analysis">
          <h3>解析</h3>
          <p>${escapeHtml(q.analysis || "—").replaceAll("\n", "<br>")}</p>
          ${q.whyWrong ? `<h3 style="margin-top:0.7rem">你为什么错</h3><p>${escapeHtml(q.whyWrong)}</p>` : ""}
          ${q.hooks ? `<h3 style="margin-top:0.7rem">记忆钩子</h3><p>${escapeHtml(q.hooks)}</p>` : ""}
        </div>
        <div class="reveal" data-panel="knowledge">
          <h3>知识点</h3>
          <ul>${(q.knowledge || []).map((k) => `<li>${escapeHtml(k)}</li>`).join("") || "<li>暂无</li>"}</ul>
        </div>
      </div>
    `;

    const optionsWrap = card.querySelector('[data-role="options"]');

    function setPanel(name, open) {
      state[name] = open;
      card.querySelector(`[data-panel="${name}"]`)?.classList.toggle("open", open);
      card.querySelector(`[data-reveal="${name}"]`)?.classList.toggle("active", open);
      if (name === "wrong" || name === "answer") {
        optionsWrap.innerHTML = renderOptions(q, state.wrong, state.answer);
      }
    }

    card.querySelectorAll("[data-reveal]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const name = btn.getAttribute("data-reveal");
        setPanel(name, !state[name]);
      });
    });
    card.querySelector('[data-role="collapse"]').addEventListener("click", () => {
      ["wrong", "answer", "analysis", "knowledge"].forEach((n) => setPanel(n, false));
    });
    card.querySelector('[data-role="reviewed"]').addEventListener("change", (ev) => {
      if (ev.target.checked) reviewed[key] = true;
      else delete reviewed[key];
      localStorage.setItem(storageKey, JSON.stringify(reviewed));
      updateStats();
    });

    card._collapseAll = () => {
      ["wrong", "answer", "analysis", "knowledge"].forEach((n) => setPanel(n, false));
    };
    return card;
  }

  function updateStats() {
    const done = questions.filter((q) => reviewed[String(q.id)]).length;
    const el = document.getElementById("statsText");
    if (el) el.textContent = `已复习 ${done} / ${questions.length}`;
  }

  function render() {
    root.innerHTML = `
      <header class="hero">
        <h1>错题本 · ${escapeHtml(book)}</h1>
        <p>默认只显示题目。按需揭开上次错选 / 正确答案 / 解析 / 知识点。科目：${escapeHtml(subject)}。</p>
        <div class="toolbar">
          <button type="button" class="btn ghost" id="collapseAll">全部收起</button>
          <a class="btn ghost" href="./题库/第01章-税法基本原理/做题本.html">打开第01章做题本</a>
          <a class="btn ghost" href="../看板.html">看板</a>
          <span class="spacer"></span>
          <span id="statsText" class="badge muted"></span>
        </div>
      </header>
      <section class="list" id="list"></section>
    `;
    const list = root.querySelector("#list");
    questions.forEach((q) => list.appendChild(createCard(q)));
    root.querySelector("#collapseAll").addEventListener("click", () => {
      list.querySelectorAll(".card").forEach((c) => c._collapseAll && c._collapseAll());
    });
    updateStats();
  }

  render();
})();
