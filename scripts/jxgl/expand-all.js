(async () => {
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
  let clicks = 0;
  for (let round = 0; round < 4; round++) {
    const btns = [...document.querySelectorAll('*')].filter(
      (e) => e.children.length === 0 && /^展开(全部|一级|二级|三级|四级)?$/.test(clean(e.innerText))
    );
    if (!btns.length) break;
    for (const b of btns) { b.click(); clicks++; }
    await new Promise((r) => setTimeout(r, 900));
  }
  return JSON.stringify({ clicks, textLen: document.body.innerText.length, tables: document.querySelectorAll('table').length });
})()
