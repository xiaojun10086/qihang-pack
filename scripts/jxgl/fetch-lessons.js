// 全校开课查询：在页面内分块 fetch 全部分页，按 lessonId 去重后返回 JSON。
// 同源请求自动携带登录态；不写死学期 ID / 入口 ID，由调用方或页面推导。
//
// 运行前先在同一个标签页写入入口参数（学期 ID 与入口 ID 从落地 URL、页面自身请求或
// 页面内嵌状态里取，每次都可能不同）：
//   qihang-bridge eval "window.__QIHANG__={semester:'<学期ID>',entry:'<入口ID>'}" --tab lesson-search --port <端口>
// 再执行：
//   qihang-bridge eval --file scripts/jxgl/fetch-lessons.js --tab lesson-search --port <端口> > all-courses.json
(async () => {
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const cfg = window.__QIHANG__ || {};
  const html = document.documentElement.innerHTML;

  // 入口 ID：优先显式配置，其次从当前 URL 推导，最后从页面内嵌状态里找
  const entry =
    cfg.entry ||
    (/\/lesson-search\/index\/(\d+)/.exec(location.pathname) || [])[1] ||
    (/lesson-search\/semester\/\d+\/search\/(\d+)/.exec(html) || [])[1] ||
    null;

  // 学期 ID：只能来自显式配置或页面内嵌状态，无法从 URL 推导
  const semester =
    cfg.semester ||
    (/lesson-search\/semester\/(\d+)\/search\//.exec(html) || [])[1] ||
    null;

  if (!semester || !entry) {
    return JSON.stringify({
      err: '缺少入口参数',
      hint: "先在目标页执行 eval \"window.__QIHANG__={semester:'<学期ID>',entry:'<入口ID>'}\"（两个 ID 从落地 URL 与页面自身请求里取，不要沿用上一次的）",
      detected: { path: location.pathname, entry, semester },
    });
  }

  const biz = cfg.biz || 2;
  const PAGE_SIZE = cfg.pageSize || 300;
  const CHUNK = cfg.chunk || 5; // 每次 5 页，避免单次返回体过大
  const API = '/student/for-std/lesson-search/semester/' + semester + '/search/' + entry;

  const nm = (o) => (o && (o.nameZh ?? o.name)) ?? null;
  const slim = (d) => ({
    lessonId: d.id,
    lessonName: d.nameZh,
    lessonCode: d.code,
    courseName: d.course && d.course.nameZh,
    courseCode: d.course && d.course.code,
    credits: d.course && d.course.credits,
    courseType: nm(d.courseType) || nm(d.course && d.course.courseType),
    courseProperty: nm(d.course && d.course.courseProperty) || nm(d.courseProperty),
    openDept: nm(d.openDepartment),
    campus: nm(d.campus),
    examMode: nm(d.examMode),
    teachLang: nm(d.teachLang),
    stdCount: d.stdCount,
    limitCount: d.limitCount,
    totalHours: d.requiredPeriodInfo && d.requiredPeriodInfo.total,
    weeks: d.requiredPeriodInfo && d.requiredPeriodInfo.weeks,
    teachers: (d.teacherAssignmentList || []).map((t) => nm(t.teacher) || nm(t)).filter(Boolean).join(',') || d.teacherAssignmentStr || null,
    schedule: d.scheduleText && d.scheduleText.dateTimePlaceText && d.scheduleText.dateTimePlaceText.textZh,
    tags: ((d.course && d.course.tags) || []).map((t) => t.nameZh).join(',') || null,
  });

  const all = [];
  let total = 0;
  let totalPages = 1;
  for (let from = 1; from <= totalPages; from += CHUNK) {
    const to = from + CHUNK - 1;
    for (let p = from; p <= to && p <= totalPages; p++) {
      const r = await fetch(API + '?bizTypeAssoc=' + biz + '&queryPage__=' + p + ',' + PAGE_SIZE + '&_=' + Date.now(), {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      if (!r.ok) return JSON.stringify({ err: 'HTTP ' + r.status + ' page ' + p, fetched: all.length });
      const j = await r.json();
      if (j._page_) { total = j._page_.totalRows; totalPages = j._page_.totalPages; }
      all.push(...(j.data || []).map(slim));
    }
    if (to >= totalPages) break;
  }

  // 去重（同一教学班可能重复出现）
  const seen = new Set();
  const uniq = all.filter((r) => (seen.has(r.lessonId) ? false : seen.add(r.lessonId)));
  return JSON.stringify({ totalRows: total, totalPages, fetched: all.length, unique: uniq.length, rows: uniq });
})()
