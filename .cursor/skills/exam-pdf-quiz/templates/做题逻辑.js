(() => {
  const meta = document.getElementById("appRoot");
  const chapter = window.习题册章节;
  if (!meta || !chapter || !Array.isArray(chapter.questions)) {
    document.body.innerHTML = '<div class="page"><div class="error">未加载到题目数据（window.习题册章节）。</div></div>';
    return;
  }

  const book = meta.dataset.book || chapter.book || "必刷550";
  const subject = meta.dataset.subject || chapter.subject || "税法一";
  const chapterId = meta.dataset.chapterId || chapter.chapterId || "";
  const chapterTitle = meta.dataset.chapterTitle || chapter.chapterTitle || "";
  const wrongbookHref = meta.dataset.wrongbookHref || "../../错题本.html";
  const favbookHref = meta.dataset.favbookHref || "../../收藏题本.html";
  const boardHref = meta.dataset.boardHref || "../../../看板.html";
  const storageKey = `习题册交卷:${subject}:${book}:${chapterId}`;
  const favKey = `习题册收藏:${subject}:${book}`;

  const questions = chapter.questions.slice().sort((a, b) => a.id - b.id);

  /** @type {Record<string, string[]>} */
  let answers = {};
  let currentIndex = 0;
  /** @type {null | { results: Record<string, boolean>, wrong: any[], at: string }} */
  let submitted = null;
  /** @type {Record<string, any>} */
  let favorites = {};

  loadSnapshot();
  loadFavorites();

  function isMulti(q) {
    return /多选/.test(String(q.type || ""));
  }

  function norm(letters) {
    return [...new Set(String(letters || "").toUpperCase().replace(/[^A-E]/g, "").split(""))]
      .sort()
      .join("");
  }

  function escapeHtml(text) {
    return String(text)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function loadSnapshot() {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return;
      const data = JSON.parse(raw);
      answers = data.answers || {};
      if (data.submitted) submitted = data.submitted;
    } catch {
      /* ignore */
    }
  }

  function saveSnapshot() {
    localStorage.setItem(
      storageKey,
      JSON.stringify({ answers, submitted, savedAt: new Date().toISOString() })
    );
  }

  function loadFavorites() {
    try {
      favorites = JSON.parse(localStorage.getItem(favKey) || "{}");
    } catch {
      favorites = {};
    }
  }

  function saveFavorites() {
    localStorage.setItem(favKey, JSON.stringify(favorites));
  }

  function toggleFavorite(q) {
    const id = String(q.id);
    if (favorites[id]) delete favorites[id];
    else favorites[id] = { ...q, wrongPick: (pickOf(q.id) || []).join("") || undefined };
    saveFavorites();
    render();
  }

  function exportFavorites() {
    const list = Object.values(favorites);
    if (!list.length) {
      alert("当前没有收藏题。");
      return;
    }
    const payload = {
      book,
      subject,
      chapterId,
      chapterTitle,
      exportedAt: new Date().toISOString(),
      questions: list,
    };
    const stamp = new Date().toISOString().slice(0, 10).replaceAll("-", "");
    const filename = `收藏导出-${book}-${stamp}.json`;
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function pickOf(qid) {
    return answers[String(qid)] || [];
  }

  function setPick(qid, key, multi) {
    if (submitted) return;
    const id = String(qid);
    if (multi) {
      const set = new Set(pickOf(qid));
      if (set.has(key)) set.delete(key);
      else set.add(key);
      answers[id] = [...set].sort();
    } else {
      answers[id] = [key];
    }
    saveSnapshot();
    render();
  }

  function gradeAll() {
    const results = {};
    const wrong = [];
    for (const q of questions) {
      const user = norm((pickOf(q.id) || []).join(""));
      const ok = user === norm(q.answer);
      results[String(q.id)] = ok;
      if (!ok) {
        wrong.push({
          ...q,
          wrongPick: user || "（未作答）",
          whyWrong: user ? `本次作答 ${user}，正解 ${norm(q.answer)}。` : "本次未作答。",
        });
      }
    }
    return { results, wrong, at: new Date().toISOString() };
  }

  function doSubmit() {
    const unanswered = questions.filter((q) => pickOf(q.id).length === 0).length;
    if (unanswered > 0) {
      const ok = confirm(`仍有 ${unanswered} 题未作答，确认交卷？`);
      if (!ok) return;
    }
    submitted = gradeAll();
    document.body.classList.add("submitted");
    saveSnapshot();
    render();
  }

  function clearRedo() {
    if (!confirm("清除本章作答与交卷结果并重做？（不会删除已合并进仓库的错题数据）")) return;
    answers = {};
    submitted = null;
    document.body.classList.remove("submitted");
    localStorage.removeItem(storageKey);
    currentIndex = 0;
    render();
  }

  function exportWrong() {
    if (!submitted) return;
    const payload = {
      book,
      subject,
      chapterId,
      chapterTitle,
      exportedAt: new Date().toISOString(),
      questions: submitted.wrong,
    };
    const stamp = new Date().toISOString().slice(0, 10).replaceAll("-", "");
    const filename = `错题导出-${book}-${chapterId}-${stamp}.json`;
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function sheetClass(q, idx) {
    const classes = [];
    if (idx === currentIndex) classes.push("current");
    const picked = pickOf(q.id).length > 0;
    if (picked) classes.push("answered");
    if (submitted) {
      classes.push(submitted.results[String(q.id)] ? "correct" : "wrong");
    }
    return classes.join(" ");
  }

  function renderOptions(q) {
    const multi = isMulti(q);
    const picked = new Set(pickOf(q.id));
    const showAns = Boolean(submitted);
    const right = new Set(showAns ? norm(q.answer).split("") : []);
    const wrongUser = showAns && !submitted.results[String(q.id)] ? new Set(picked) : new Set();

    return Object.keys(q.options || {})
      .sort()
      .map((key) => {
        const classes = ["option"];
        if (picked.has(key)) classes.push("selected");
        if (showAns && right.has(key)) classes.push("mark-right");
        if (showAns && wrongUser.has(key) && !right.has(key)) classes.push("mark-wrong");
        const disabled = submitted ? "disabled" : "";
        return `<button type="button" class="${classes.join(" ")}" data-key="${key}" ${disabled}>
          <span class="key">${key}.</span>
          <span>${escapeHtml(q.options[key])}</span>
        </button>`;
      })
      .join("");
  }

  function renderPostPanels(q) {
    if (!submitted) return "";
    const ok = submitted.results[String(q.id)];
    const user = norm(pickOf(q.id).join("")) || "未作答";
    return `
      <div class="controls">
        <button type="button" class="btn" data-reveal="analysis">看解析</button>
        <button type="button" class="btn" data-reveal="knowledge">看知识点</button>
      </div>
      <div class="reveal ${ok ? "answer" : "wrong"} open">
        <h3>${ok ? "作答正确" : "作答有误"}</h3>
        <p>你的答案：${escapeHtml(user)}　正解：${escapeHtml(norm(q.answer))}</p>
      </div>
      <div class="reveal" data-panel="analysis">
        <h3>解析</h3>
        <p>${escapeHtml(q.analysis || "—").replaceAll("\n", "<br>")}</p>
        ${q.hooks ? `<h3 style="margin-top:0.7rem">记忆钩子</h3><p>${escapeHtml(q.hooks)}</p>` : ""}
      </div>
      <div class="reveal" data-panel="knowledge">
        <h3>知识点</h3>
        <ul>${(q.knowledge || []).map((k) => `<li>${escapeHtml(k)}</li>`).join("") || "<li>暂无</li>"}</ul>
        ${q.lecture ? `<p style="margin-top:0.5rem;color:var(--muted)">${escapeHtml(q.lecture)}</p>` : ""}
      </div>
    `;
  }

  function render() {
    if (submitted) document.body.classList.add("submitted");
    const q = questions[currentIndex];
    const answeredCount = questions.filter((x) => pickOf(x.id).length > 0).length;
    const correctCount = submitted
      ? questions.filter((x) => submitted.results[String(x.id)]).length
      : 0;

    meta.innerHTML = `
      <header class="hero">
        <h1>做题本 · ${escapeHtml(book)} · ${escapeHtml(chapterId)} ${escapeHtml(chapterTitle)}</h1>
        <p>交卷前不显示对错与解析。多选题须全对才得分。进度 ${answeredCount}/${questions.length}。
          ${submitted ? `已交卷：对 ${correctCount} / 错 ${questions.length - correctCount}。` : "尚未交卷。"}
        </p>
        <div class="toolbar">
          <button type="button" class="btn primary" id="submitBtn" ${submitted ? "disabled" : ""}>交卷</button>
          <button type="button" class="btn" id="exportBtn" ${submitted && submitted.wrong.length ? "" : "disabled"}>导出错题 JSON</button>
          <button type="button" class="btn" id="exportFavBtn">导出收藏 JSON</button>
          <a class="btn ghost" href="${wrongbookHref}">错题本</a>
          <a class="btn ghost" href="${favbookHref}">收藏题本</a>
          <a class="btn ghost" href="${boardHref}">看板</a>
          <button type="button" class="btn ghost" id="redoBtn">清除重做</button>
          <span class="spacer"></span>
          <span class="badge muted">${escapeHtml(subject)}</span>
        </div>
        ${
          submitted
            ? `<p style="margin-top:0.75rem;color:var(--muted)">已自动收集 ${submitted.wrong.length} 道错题。导出 JSON 放入「导出」文件夹后，对 Agent 说：按习题册交互技能合并错题。</p>`
            : ""
        }
      </header>

      ${
        submitted
          ? `<div class="score-banner ${submitted.wrong.length ? "warn" : ""}">交卷结果：正确 ${correctCount} / ${questions.length}；错题 ${submitted.wrong.length} 道已入篮。</div>`
          : ""
      }

      <div class="layout">
        <aside class="panel sheet">
          <h2>答题卡</h2>
          <div class="sheet-grid" id="sheetGrid">
            ${questions
              .map(
                (item, idx) =>
                  `<button type="button" data-idx="${idx}" class="${sheetClass(item, idx)}">${item.id}</button>`
              )
              .join("")}
          </div>
        </aside>

        <article class="card" id="questionCard">
          <div class="card-head">
            <span class="badge">第 ${q.id} 题</span>
            <span class="badge muted">${escapeHtml(q.type || "")}${isMulti(q) ? " · 全对得分" : ""}</span>
            ${
              submitted
                ? submitted.results[String(q.id)]
                  ? '<span class="badge ok">正确</span>'
                  : '<span class="badge bad">错误</span>'
                : ""
            }
            <span class="source">${escapeHtml(q.source || "")}</span>
            <button type="button" class="btn ${favorites[String(q.id)] ? "active" : "ghost"}" id="favBtn" style="margin-left:auto">
              ${favorites[String(q.id)] ? "已收藏" : "收藏"}
            </button>
          </div>
          <div class="card-body">
            <p class="stem">${escapeHtml(q.stem)}</p>
            <div class="options" id="optionList">${renderOptions(q)}</div>
            <div class="nav-row">
              <button type="button" class="btn" id="prevBtn" ${currentIndex === 0 ? "disabled" : ""}>上一题</button>
              <button type="button" class="btn" id="nextBtn" ${currentIndex >= questions.length - 1 ? "disabled" : ""}>下一题</button>
            </div>
            ${renderPostPanels(q)}
          </div>
        </article>
      </div>
    `;

    meta.querySelector("#submitBtn")?.addEventListener("click", doSubmit);
    meta.querySelector("#exportBtn")?.addEventListener("click", exportWrong);
    meta.querySelector("#exportFavBtn")?.addEventListener("click", exportFavorites);
    meta.querySelector("#favBtn")?.addEventListener("click", () => toggleFavorite(q));
    meta.querySelector("#redoBtn")?.addEventListener("click", clearRedo);
    meta.querySelector("#prevBtn")?.addEventListener("click", () => {
      currentIndex = Math.max(0, currentIndex - 1);
      render();
    });
    meta.querySelector("#nextBtn")?.addEventListener("click", () => {
      currentIndex = Math.min(questions.length - 1, currentIndex + 1);
      render();
    });
    meta.querySelectorAll("#sheetGrid button").forEach((btn) => {
      btn.addEventListener("click", () => {
        currentIndex = Number(btn.getAttribute("data-idx"));
        render();
      });
    });
    meta.querySelectorAll("#optionList .option").forEach((btn) => {
      btn.addEventListener("click", () => {
        setPick(q.id, btn.getAttribute("data-key"), isMulti(q));
      });
    });
    meta.querySelectorAll("[data-reveal]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const name = btn.getAttribute("data-reveal");
        const panel = meta.querySelector(`[data-panel="${name}"]`);
        if (!panel) return;
        const open = !panel.classList.contains("open");
        panel.classList.toggle("open", open);
        btn.classList.toggle("active", open);
      });
    });
  }

  render();
})();
