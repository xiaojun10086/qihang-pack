(() => {
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const tip = (el, name, prefix) => {
    const e = el.querySelector(`[data-original-title${prefix ? '^' : ''}="${name}"]`);
    return e ? clean(e.innerText) : '';
  };
  const rows = [...document.querySelectorAll('tbody tr')].map((tr) => {
    const tds = [...tr.querySelectorAll('td')];
    if (tds.length < 6) return null;
    const c1 = tds[1];
    const a = c1.querySelector('h4 a');
    return {
      name: a ? clean(a.innerText) : '',
      code: tip(c1, '课程代码'),
      dept: tip(c1, '开课部门', true),
      type: tip(c1, '课程类型'),
      hours: tip(c1, '总学时'),
      lang: tip(c1, '授课语言'),
      exam: tip(c1, '考核方式'),
      required: tip(c1, '是否必修'),
      cat: clean(c1.innerText),
      lesson: clean(tds[2].innerText),
      credits: clean(tds[3].innerText),
      teacher: clean(tds[4].innerText),
      timeplace: clean(tds[5].innerText),
    };
  }).filter((r) => r && r.name);
  const m = document.body.innerText.match(/of\s*([\d,]+)/);
  return JSON.stringify({ url: location.href, total: m ? m[1] : '', count: rows.length, rows });
})()
