(() => {
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const items = [...document.querySelectorAll('.module-tpl, table')];
  const modules = [], outer = [];
  let ctx1 = null, ctx2 = null;
  const num = (t, k) => { const m = new RegExp(k + '\\s*([\\d.]+)').exec(t || ''); return m ? parseFloat(m[1]) : null; };
  for (const it of items) {
    if (it.classList.contains('module-tpl')) {
      const depth = +(/depth-(\d+)/.exec(it.className) || [0, 0])[1];
      const name = clean(it.querySelector('.module-name')?.innerText);
      const headBox = [...it.children].find(c => !c.classList.contains('module-tpl'));
      const head = clean(headBox?.innerText);
      const node = {
        name, depth,
        req: num(head, '要求'), done: num(head, '已完成'), undone: num(head, '未完成'), reading: num(head, '在读'),
        subReq: num(head, '子模块：要求'), subDone: /子模块[^|]*已完成\s*([\d.]+)/.exec(head)?.[1] ?? null,
        head, courses: [], subs: [],
      };
      if (depth <= 1) { ctx1 = node; ctx2 = null; modules.push(node); }
      else { ctx2 = node; (ctx1 ? ctx1.subs : modules).push(node); }
    } else {
      const rows = [...it.querySelectorAll('tr')];
      if (rows.length < 2) continue;
      const header = clean(rows[0].innerText);
      const isPlan = header.includes('开课学期') && header.includes('是否必修');
      const courses = [];
      for (const tr of rows.slice(1)) {
        const td = [...tr.querySelectorAll('td')].map(x => clean(x.innerText));
        if (td.length < 5) continue;
        courses.push(isPlan
          ? { name: td[0].replace(/^\d+\.\s*/, ''), code: td[1], term: td[2], required: td[3], credits: parseFloat(td[4]) || 0, check: td[7], note: td[9] }
          : { name: td[0].replace(/^\d+\.\s*/, ''), code: td[1], credits: parseFloat(td[2]) || 0, check: td[5], note: td[6] });
      }
      if (!isPlan) { outer.push(...courses); continue; }
      (ctx2 || ctx1)?.courses.push(...courses);
    }
  }
  // 合并同名一级模块
  const merged = [], idx = {};
  for (const m of modules) {
    if (m.depth > 1) continue;
    if (idx[m.name]) { idx[m.name].courses.push(...m.courses); idx[m.name].subs.push(...m.subs); }
    else { idx[m.name] = m; merged.push(m); }
  }
  const tot = /([\d.]+)\s*\/\s*([\d.]+)\s*已完成\/要求学分/.exec(clean(document.body.innerText));
  return JSON.stringify({ totalDone: tot?.[1], totalReq: tot?.[2], modules: merged, outer }, null, 1);
})()
