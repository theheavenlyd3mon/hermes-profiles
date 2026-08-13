/* 转场 live 演示 — 参数来自 craft/transitions.md（2026-07-28 preview review）
   A/B 两"镜头"用色块模拟；把真实素材丢进 assets/clips/ 后可换成 <video>。
   实现路由仍归 hyperframes catalog / FFmpeg，本页只演示选型手感。 */

const SHOT_A = `<div class="sa"><span>A</span><em>SHOT A</em></div>`;
const SHOT_B = `<div class="sb"><span>B</span><em>SHOT B</em></div>`;
const SHOT_CSS = `
  %% .stagewrap{position:absolute;inset:0;overflow:hidden}
  %% .sa,%% .sb{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center}
  %% .sa{background:linear-gradient(135deg,#2E4A5C,#16232C)}
  %% .sb{background:linear-gradient(135deg,#5C3A2E,#2C1A16)}
  %% .sa span,%% .sb span{font-size:52px;font-weight:900;color:rgba(255,255,255,.9)}
  %% .sa em,%% .sb em{font-style:normal;font-size:11px;letter-spacing:4px;color:rgba(255,255,255,.5);margin-top:4px}`;

window.TRANSITION_DEMOS = [
{ id:'hardcut', name:'硬切 Hard cut', keep:1, feel:'全片的默认脊柱',
  meta:'0 帧 · 入场语法走 pacing-rhythm §4（accent 预算、禁 opacity pop）· 不适用：无（万能）· 路由：plain cut',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}</div>`, css:SHOT_CSS,
  build(r,tl){ const b=r.querySelector('.sb'); gsap.set(b,{autoAlpha:0});
    tl.to({},{duration:0},0.9);
    tl.set(b,{autoAlpha:1},0.9);           // 0 帧硬切
    tl.to({},{duration:0},2.2); } },

{ id:'jlcut', name:'J/L-cut 声音先行', keep:1, feel:'隐形、专业——音频扛住接缝',
  meta:'音频领先/拖后画面 0.3–1.0s · 不适用：无（通用）· 路由：FFmpeg 偏移 trim / HF data-start 偏移',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}
    <div class="atrk"><div class="abar aa">A 音轨</div><div class="abar ab">B 音轨（提前 0.6s 进）</div>
    <div class="pl"></div></div></div>`,
  css:SHOT_CSS + `
    %% .atrk{position:absolute;left:6%;right:6%;bottom:8%;height:44px}
    %% .abar{position:absolute;height:18px;border-radius:4px;font-size:9px;color:#0b0b0f;display:flex;align-items:center;padding:0 6px;font-weight:700}
    %% .aa{top:0;left:0;width:56%;background:#7fb3d3}
    %% .ab{top:24px;left:38%;right:0;background:#d39b7f}
    %% .pl{position:absolute;top:-4px;bottom:-4px;left:0;width:2px;background:#ffd76a}`,
  build(r,tl){ const b=r.querySelector('.sb'); gsap.set(b,{autoAlpha:0});
    tl.fromTo(r.querySelector('.pl'),{left:'0%'},{left:'100%',duration:3,ease:'none'},0);
    tl.set(b,{autoAlpha:1},1.7);            // 画面比 B 音轨晚 0.6s
    tl.to({},{duration:0},3); } },

{ id:'slide', name:'丝滑定向滑动', keep:1, feel:'premium、平静能量 — workspace 签名',
  meta:'入 expo.out / 出 expo.in · 0.5–0.7s · 全片同一个轴 · 不适用：混乱快剪蒙太奇 · 路由：HF catalog § Push/Slide',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}</div>`, css:SHOT_CSS,
  build(r,tl){ const a=r.querySelector('.sa'), b=r.querySelector('.sb');
    gsap.set(b,{xPercent:100});
    tl.to({},{duration:0},0.8);
    tl.to(a,{xPercent:-100,duration:0.6,ease:'expo.in'},0.8);
    tl.to(b,{xPercent:0,duration:0.6,ease:'expo.out'},0.8);
    tl.to({},{duration:0},2.4); } },

{ id:'dissolve', name:'交叉溶解 + 微缩放', keep:1, feel:'电影感、情绪、怀旧',
  meta:'~0.6s 交叠 · 入 1.045→1 / 出 →0.985 · 场景 ≥3s · 落回精确 1.0（[no-zoom-drift]）· 不适用：快剪（杀节奏）',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}</div>`, css:SHOT_CSS,
  build(r,tl){ const a=r.querySelector('.sa'), b=r.querySelector('.sb');
    gsap.set(b,{autoAlpha:0,scale:1.045});
    tl.to({},{duration:0},0.9);
    tl.to(a,{autoAlpha:0,scale:0.985,duration:0.6,ease:'power1.inOut'},0.9);
    tl.to(b,{autoAlpha:1,scale:1,duration:0.6,ease:'power1.inOut'},0.9);
    tl.to({},{duration:0},2.5); } },

{ id:'comicwipe', name:'色块 / 漫画擦除', keep:1, feel:'俏皮、可爱、喜剧',
  meta:'斜向色块扫 0.3–0.5s · 用画面配色（非纯白）· 配贴纸/拼贴 look · 不适用：premium、纪录片 · 路由：HF § Cover',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}<div class="wp"></div></div>`,
  css:SHOT_CSS + `
    %% .wp{position:absolute;inset:-20% -30%;background:#ffd76a;transform:translateX(-130%) rotate(-8deg)}`,
  build(r,tl){ const b=r.querySelector('.sb'), w=r.querySelector('.wp');
    gsap.set(b,{autoAlpha:0});
    tl.to({},{duration:0},0.8);
    tl.to(w,{x:0,xPercent:0,duration:0.24,ease:'power2.in'},0.8);
    tl.set(b,{autoAlpha:1},1.04);                       // 色块盖住时切换
    tl.to(w,{xPercent:130,duration:0.26,ease:'power2.out'},1.04);
    tl.to({},{duration:0},2.4); } },

{ id:'matchcut', name:'匹配剪辑 / 色彩押韵', keep:1, feel:'隐形手艺，最高级的接缝',
  meta:'选片时规划：动作连续 或 A尾-B头 主色/构图押韵 · 纯剪无特效 · 需素材支撑 · 路由：EDL 里规划',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}<div class="rhy"></div>
    <div class="mch">主色押韵：A 尾 → B 头</div></div>`,
  css:SHOT_CSS.replace('#5C3A2E,#2C1A16','#2E5C4A,#162C22') + `
    %% .rhy{position:absolute;left:50%;top:50%;width:74px;height:74px;margin:-37px 0 0 -37px;border-radius:50%;background:#ffd76a;opacity:.92}
    %% .mch{position:absolute;bottom:8%;left:0;right:0;text-align:center;color:rgba(255,255,255,.75);font-size:11px;letter-spacing:1px}`,
  build(r,tl){ const b=r.querySelector('.sb'); gsap.set(b,{autoAlpha:0});
    // 圆形元素在两镜同位置 → 硬切时视觉连续
    tl.to({},{duration:0},1.1);
    tl.set(b,{autoAlpha:1},1.1);
    tl.set(r.querySelector('.rhy'),{background:'#7fd3b3'},1.1);
    tl.to({},{duration:0},2.6); } },

{ id:'looknative', name:'Look 原生接缝', keep:1, feel:'定义整片的',
  meta:'胶片走带 / 画廊涟漪 / 大数字砸场——look 卡的接缝就是转场家族 · 不适用：混用其他家族 · 路由：所属 looks/ 卡',
  html:`<div class="stagewrap"><div class="reel">
    ${['#2E4A5C','#5C3A2E','#2E5C4A','#4A2E5C'].map((c,i)=>
      `<div class="fr" style="background:linear-gradient(135deg,${c},#16181C)"><span>${i+1}</span></div>`).join('')}
    </div><div class="perf"></div><div class="lkn">film-reel-carousel：走带即转场</div></div>`,
  css:SHOT_CSS + `
    %% .reel{position:absolute;top:50%;left:0;height:64%;transform:translateY(-50%);display:flex;gap:8px;padding-left:8%}
    %% .fr{width:150px;border-radius:6px;display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.85);font-size:24px;font-weight:900;flex:none}
    %% .perf{position:absolute;top:6%;left:0;right:0;height:8px;background:repeating-linear-gradient(90deg,rgba(255,255,255,.18) 0 10px,transparent 10px 24px)}
    %% .lkn{position:absolute;bottom:7%;left:0;right:0;text-align:center;color:rgba(255,255,255,.6);font-size:11px}`,
  build(r,tl){ tl.fromTo(r.querySelector('.reel'),{x:0},{x:-316,duration:2.4,ease:'power2.inOut'},0.5);
    tl.to({},{duration:0},3.2); } },

/* ===== 冷板凳（实审弃用，仅用户点名） ===== */
{ id:'whippan', name:'甩镜 Whip pan', keep:0, feel:'冷板凳',
  meta:'如被点名：0.25–0.4s · 全片一个轴 · blur 方向与运动一致',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}</div>`, css:SHOT_CSS,
  build(r,tl){ const a=r.querySelector('.sa'), b=r.querySelector('.sb');
    gsap.set(b,{xPercent:100});
    tl.to({},{duration:0},0.7);
    tl.to(a,{xPercent:-100,filter:'blur(14px)',duration:0.16,ease:'power2.in'},0.7);
    tl.fromTo(b,{filter:'blur(14px)'},{xPercent:0,filter:'blur(0px)',duration:0.18,ease:'power2.out'},0.86);
    tl.to({},{duration:0},2.1); } },

{ id:'zoompunch', name:'Zoom 穿越 punch-through', keep:0, feel:'冷板凳',
  meta:'如被点名：≤2/片 · 0.3–0.45s · 只给最大的拍点 · 绝不连用',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}</div>`, css:SHOT_CSS,
  build(r,tl){ const a=r.querySelector('.sa'), b=r.querySelector('.sb');
    gsap.set(b,{autoAlpha:0,scale:0.6});
    tl.to({},{duration:0},0.8);
    tl.to(a,{scale:2.4,autoAlpha:0,duration:0.36,ease:'power2.in'},0.8);
    tl.to(b,{scale:1,autoAlpha:1,duration:0.4,ease:'power2.out'},1.1);
    tl.to({},{duration:0},2.4); } },

{ id:'flash', name:'光闪 Light flash', keep:0, feel:'冷板凳',
  meta:'如被点名：2–3 帧 · ≤2/片 · 用配色不用纯白',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}<div class="fl"></div></div>`,
  css:SHOT_CSS + `%% .fl{position:absolute;inset:0;background:#ffd76a;opacity:0}`,
  build(r,tl){ const b=r.querySelector('.sb'), f=r.querySelector('.fl');
    gsap.set(b,{autoAlpha:0});
    tl.to({},{duration:0},0.9);
    tl.to(f,{opacity:0.9,duration:0.05,ease:'none'},0.9);
    tl.set(b,{autoAlpha:1},0.95);
    tl.to(f,{opacity:0,duration:0.1,ease:'none'},0.95);
    tl.to({},{duration:0},2.3); } },

{ id:'speedramp', name:'变速接缝 Speed-ramp', keep:0, feel:'冷板凳',
  meta:'如被点名：A 尾 1→3x 加速切入 · B 正常速 · 音频保持连续 · 对话中禁用',
  html:`<div class="stagewrap">${SHOT_A}${SHOT_B}
    <div class="strip"><div class="tick"></div></div></div>`,
  css:SHOT_CSS + `
    %% .strip{position:absolute;left:8%;right:8%;bottom:12%;height:6px;background:rgba(255,255,255,.15);border-radius:3px;overflow:hidden}
    %% .tick{position:absolute;top:0;bottom:0;left:0;width:20%;background:#ffd76a}`,
  build(r,tl){ const b=r.querySelector('.sb'), tk=r.querySelector('.tick');
    gsap.set(b,{autoAlpha:0});
    tl.fromTo(tk,{width:'6%'},{width:'62%',duration:1.1,ease:'power3.in'},0);   // 1→3x 加速
    tl.set(b,{autoAlpha:1},1.1);
    tl.fromTo(tk,{width:'62%'},{width:'100%',duration:1.1,ease:'none'},1.1);    // B 恒速
    tl.to({},{duration:0},2.4); } },
];
