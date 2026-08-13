/* 动效配方 live 演示定义 — 代码逐字来自 craft/snippets/*.md
   由 index.html 的 Tab 引擎懒加载渲染。helpers 见 snippets/README.md。 */

function springKeyframes(stiffness, damping, build, n = 70) {
  let x = 0, v = 0; const dt = 1 / 60, out = [];
  for (let i = 0; i < n; i++) {
    const a = -stiffness * (x - 1) - damping * v;
    v += a * dt; x += v * dt; out.push(build(x));
  }
  out[n - 1] = build(1);
  return out;
}
const SPRING = { snap:[1218,70], ui:[305,33], gentle:[110,20], lively:[622,17], ambient:[43,13] };
const sKF = (p, b) => springKeyframes(SPRING[p][0], SPRING[p][1], b);
function prng(seed) { return () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 2 ** 32; }
const anticipation = t => t < 0.2 ? -0.3*(t/0.2)*(t/0.2)
  : (a => -0.012 + 1.012*a*a*(3-2*a))((t-0.2)/0.8);
const T0 = 0, HOLD = 1.6, SCENE_DUR = 4;
const spans = s => [...s].map(c => `<span>${c}</span>`).join('');

window.MOTION_DEMOS = [
/* ===== A · 文字入场 ===== */
{ g:'文字入场', id:'percharrise', name:'逐字 Spring 升入', en:'per-char rise',
  meta:'spring 190/15 · y 44px→0 · 错峰 60ms · opacity 前 40% 完成 · 通用 hero 标题',
  html:`<div class="hero-title">${spans('山谷里的一餐')}</div>`,
  css:`%% .hero-title{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
       %% .hero-title span{display:inline-block;font-size:40px;font-weight:800;color:#fff;margin:0 2px;opacity:0}`,
  build(r,tl){ r.querySelectorAll('.hero-title span').forEach((el,i)=>{
    tl.to(el,{keyframes:springKeyframes(190,15,p=>({y:(1-p)*44,opacity:Math.min(1,p*2.2)})),
      duration:0.8,ease:'none'}, T0+i*0.06); }); } },

{ g:'文字入场', id:'scatter', name:'四散汇聚', en:'scatter-converge',
  meta:'±140px 种子随机起点+旋转 · gentle · blur 10→0 · stagger tight · 重磅标题（≤1/场景）',
  html:`<div class="hero-title">${spans('山谷里的一餐')}</div>`,
  css:`%% .hero-title{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
       %% .hero-title span{display:inline-block;font-size:40px;font-weight:900;color:#fff;margin:0 2px;opacity:0}`,
  build(r,tl){ const rd=prng(42);
    r.querySelectorAll('.hero-title span').forEach((el,i)=>{
      const x0=(rd()-0.5)*280,y0=(rd()-0.5)*180,r0=(rd()-0.5)*50;
      tl.to(el,{keyframes:sKF('gentle',p=>({x:x0*(1-p),y:y0*(1-p),rotate:r0*(1-p),
        filter:`blur(${Math.max(0,10*(1-p))}px)`,opacity:Math.min(1,p*1.8)})),
        duration:1.1,ease:'none'}, T0+i*0.04); }); } },

{ g:'文字入场', id:'linemask', name:'行遮罩揭示', en:'line-mask reveal',
  meta:'行框内 y 110%→0 · expo.out 0.7s · 行错峰 120ms · 退场 expo.in · 高级感默认之选',
  html:`<div class="rv"><div class="mask"><div class="line k">EPISODE 02 · BOHOL</div></div>
    <div class="mask"><div class="line t">山谷里的一餐</div></div>
    <div class="mask"><div class="line s">巧克力山下的第一顿本地菜</div></div></div>`,
  css:`%% .rv{position:absolute;left:10%;top:50%;transform:translateY(-60%)}
       %% .mask{overflow:hidden} %% .line{transform:translateY(110%)}
       %% .k{color:#ffd76a;font-size:13px;letter-spacing:4px}
       %% .t{color:#fff;font-size:36px;font-weight:800;margin-top:6px}
       %% .s{color:#9a9aa5;font-size:13px;margin-top:8px}`,
  build(r,tl){ r.querySelectorAll('.line').forEach((el,i)=>{
    tl.fromTo(el,{yPercent:110},{yPercent:0,duration:0.7,ease:'expo.out'}, T0+i*0.12);
    tl.to(el,{yPercent:-110,duration:0.45,ease:'expo.in'}, T0+HOLD+i*0.08); }); } },

{ g:'文字入场', id:'scramble', name:'乱码落定', en:'scramble settle',
  meta:'每字 8×45ms 翻滚 · 中心向外 90ms×距离 落定 · 科技 / 悬念揭示',
  html:`<div class="hero-title">${spans('山谷里的一餐')}</div>`,
  css:`%% .hero-title{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
       %% .hero-title span{display:inline-block;font-size:34px;font-weight:700;font-family:ui-monospace,monospace;min-width:1.05em;text-align:center}`,
  build(r,tl){ const G='アイウエオ0123456789XYZ#*';
    const cs=[...r.querySelectorAll('.hero-title span')], mid=(cs.length-1)/2, rd=prng(7);
    cs.forEach((el,i)=>{ const tgt=el.textContent;
      const seq=Array.from({length:8},()=>G[(rd()*G.length)|0]); const px={k:0};
      el.textContent=seq[0]; el.style.color='#ffd76a';
      tl.to(px,{k:8,duration:8*0.045,ease:'none',onUpdate(){
        const s=Math.min(8,px.k|0);
        if(s>=8){el.textContent=tgt;el.style.color='#fff';}
        else {el.textContent=seq[s];el.style.color='#ffd76a';}
      }}, T0+Math.abs(i-mid)*0.09); }); } },

{ g:'文字入场', id:'typewriter', name:'自然打字机', en:'natural typewriter',
  meta:'字间 40-140ms 种子随机 · 标点后 +220ms · 闪烁 caret · 旁白感 / vlog 独白',
  html:`<div class="tw">${spans('今天想带你去一个地方……')}<span class="caret"></span></div>`,
  css:`%% .tw{position:absolute;left:10%;top:46%;font-size:24px;color:#fff;font-weight:600}
       %% .tw span{display:none}
       %% .tw .caret{display:inline-block;width:3px;height:1.1em;background:#ffd76a;vertical-align:-0.15em;margin-left:2px}`,
  build(r,tl){ const cs=[...r.querySelectorAll('.tw span:not(.caret)')], rd=prng(11); let t=T0;
    cs.forEach(el=>{ tl.set(el,{display:'inline-block'},t);
      t += '，。……'.includes(el.textContent) ? 0.22 : 0.04+rd()*0.10; });
    const bl=Math.ceil((t-T0+1)/0.8);
    tl.to(r.querySelector('.caret'),{opacity:0,duration:0.4,ease:'steps(1)',repeat:bl*2,yoyo:true},T0); } },

/* ===== B · Hero 编排 ===== */
{ g:'Hero 编排', id:'editorial', name:'编辑部 Hero 三层错峰', en:'editorial hero stagger',
  meta:'行遮罩标题(expo.out 80ms) + 浮动卡片(lively y24) + 背景巨字(5%白 ambient 漂移) · 开场天花板',
  html:`<div class="eh"><div class="bw">BOHOL</div>
    <div class="hl"><div class="mask"><div class="line k">EPISODE 02 — TRAVEL DIARY</div></div>
    <div class="mask"><div class="line h1x">山谷里，</div></div>
    <div class="mask"><div class="line h1x">一餐<em>慢</em>下来。</div></div></div>
    <div class="fc fa"></div><div class="fc fb"></div></div>`,
  css:`%% .eh{position:absolute;inset:0}
       %% .bw{position:absolute;right:-4%;bottom:-6%;font-size:96px;font-weight:900;color:rgba(255,255,255,.045);letter-spacing:-4px;white-space:nowrap}
       %% .hl{position:absolute;left:8%;top:20%} %% .mask{overflow:hidden} %% .line{transform:translateY(110%)}
       %% .k{color:#ffd76a;font-size:11px;letter-spacing:4px}
       %% .h1x{color:#fff;font-size:38px;font-weight:900;line-height:1.05} %% .h1x em{color:#d94f2b;font-style:italic}
       %% .fc{position:absolute;opacity:0;box-shadow:0 16px 40px rgba(0,0,0,.5)}
       %% .fa{right:12%;top:16%;width:104px;height:66px;border-radius:10px;background:linear-gradient(135deg,#2a2a33,#3c3c48);border:1px solid rgba(255,215,106,.35)}
       %% .fb{right:26%;top:52%;width:76px;height:76px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#d94f2b,#7a2413)}`,
  build(r,tl){ tl.fromTo(r.querySelector('.bw'),{x:0},{x:-30,duration:6,ease:'none'},T0);
    r.querySelectorAll('.line').forEach((el,i)=>tl.fromTo(el,{yPercent:110},{yPercent:0,duration:0.75,ease:'expo.out'},T0+i*0.08));
    r.querySelectorAll('.fc').forEach((el,i)=>{
      tl.to(el,{keyframes:sKF('lively',p=>({y:(1-p)*24,scale:0.9+0.1*p,opacity:Math.min(1,p*2.2)})),
        duration:0.85,ease:'none'},T0+0.4+i*0.08);
      const ld=2.6+i*0.4;
      tl.to(el,{y:i?8:-8,duration:ld/2,ease:'sine.inOut',repeat:Math.ceil(4/ld)*2,yoyo:true},T0+1.3); }); } },

{ g:'Hero 编排', id:'coverflow', name:'3D Coverflow 展开', en:'coverflow spread',
  meta:'perspective 900px · 每级 x92/rotY21°/z-90/scale-0.06 · lively · 中心错峰 · 多素材预览',
  html:`<div class="cfw">${[-2,-1,0,1,2].map(o=>`<div class="cf" data-o="${o}" style="background:linear-gradient(160deg,${['#d94f2b','#efe7d8','#ffd76a','#3c6e8f','#2b2b31'][o+2]},#14141a)"></div>`).join('')}</div>`,
  css:`%% .cfw{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;perspective:900px}
       %% .cf{position:absolute;width:104px;height:140px;border-radius:12px;opacity:0;border:1px solid rgba(255,255,255,.12);box-shadow:0 20px 50px rgba(0,0,0,.55)}`,
  build(r,tl){ r.querySelectorAll('.cf').forEach(el=>{ const o=+el.dataset.o, a=Math.abs(o);
    tl.to(el,{keyframes:sKF('lively',p=>({x:o*84*p,z:-a*90*p,rotationY:-o*21*p,
      scale:1-a*0.06*p,opacity:Math.min(1,p*2+0.1)})),duration:0.9,ease:'none'},T0+a*0.08); }); } },

{ g:'Hero 编排', id:'cardstack', name:'卡片堆叠洗牌', en:'card-stack shuffle',
  meta:'顶卡甩出 expo.in 0.4s +rot14° · 下卡 ui spring 上位(y12/scale0.06 每级) · 照片墙/语录轮换',
  html:`<div class="stk">${['#efe7d8','#ffd76a','#d94f2b'].map((c,i)=>`<div class="sc" data-lv="${i}" style="background:linear-gradient(150deg,${c},#1a1a21 160%)"></div>`).join('')}</div>`,
  css:`%% .stk{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
       %% .sc{position:absolute;width:160px;height:106px;border-radius:14px;box-shadow:0 18px 44px rgba(0,0,0,.5)}`,
  build(r,tl){ let ord=[...r.querySelectorAll('.sc')];
    ord.forEach(el=>gsap.set(el,{y:+el.dataset.lv*12,scale:1-+el.dataset.lv*0.06,zIndex:3-+el.dataset.lv,rotation:0}));
    for(let k=0;k<3;k++){ const t=T0+k*1.5, top=ord[0];
      tl.to(top,{x:170,y:-30,rotation:14,opacity:0,duration:0.4,ease:'expo.in'},t);
      ord.slice(1).forEach((el,i)=>{
        tl.to(el,{keyframes:sKF('ui',p=>{const lv=(i+1)-p;return{y:12*lv,scale:1-0.06*lv};}),
          duration:0.6,ease:'none'},t+0.1);
        tl.set(el,{zIndex:3-i},t+0.1); });
      tl.set(top,{zIndex:1,x:-150,y:24,scale:0.88,rotation:-10},t+0.45);
      tl.to(top,{keyframes:sKF('ui',p=>({x:-150*(1-p),y:24-12*p,scale:0.88+0.06*p,
        rotation:-10*(1-p),opacity:Math.min(1,p*2)})),duration:0.65,ease:'none'},t+0.5);
      ord=[...ord.slice(1),top]; } } },

/* ===== C · 数据 & 点缀 ===== */
{ g:'数据 & 点缀', id:'countup', name:'数字滚动 Count-up', en:'count-up',
  meta:'整数 expo 减速 ~0.9s · 单位 chip lively 后入 · 简单数据时刻',
  html:`<div class="stw"><div class="st"><span class="num">0</span><span class="unit">家店</span></div></div>`,
  css:`%% .stw{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
       %% .st{display:flex;align-items:baseline}
       %% .num{color:#fff;font-size:56px;font-weight:800;font-variant-numeric:tabular-nums}
       %% .unit{color:#ffd76a;font-size:20px;font-weight:700;margin-left:6px;opacity:0}`,
  build(r,tl){ const n=r.querySelector('.num'), px={v:0};
    tl.to(px,{v:127,duration:0.9,ease:'expo.out',onUpdate:()=>n.textContent=Math.round(px.v)},T0);
    tl.to(r.querySelector('.unit'),{keyframes:sKF('lively',p=>({scale:0.4+0.6*p,opacity:Math.min(1,p*2.5)})),
      duration:0.6,ease:'none'},T0+0.9); } },

{ g:'数据 & 点缀', id:'odometer', name:'数字轮盘 Odometer', en:'odometer wheels',
  meta:'每位竖直轮盘 ui spring · 右→左 80ms 错峰 · tabular-nums · hero 数字首选',
  html:`<div class="odw"><div class="odo">${[2,3,8,0].map(d=>`<div class="dg" data-d="${d}"></div>`).join('')}<span class="unit">km 骑行</span></div></div>`,
  css:`%% .odw{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
       %% .odo{display:flex;align-items:baseline}
       %% .dg{height:56px;overflow:hidden} %% .dg .wh{display:flex;flex-direction:column}
       %% .dg .wh span{color:#fff;font-size:48px;font-weight:800;height:56px;line-height:56px;font-variant-numeric:tabular-nums;text-align:center;min-width:.62em}
       %% .unit{color:#ffd76a;font-size:18px;font-weight:700;margin-left:8px;opacity:0}`,
  build(r,tl){ const H=56, dg=[...r.querySelectorAll('.dg')];
    dg.forEach(d=>d.innerHTML=`<div class="wh">${Array.from({length:10},(_,k)=>`<span>${k}</span>`).join('')}</div>`);
    dg.forEach((d,i)=>{ const t=+d.dataset.d;
      tl.to(d.querySelector('.wh'),{keyframes:sKF('ui',p=>({y:-t*H*p})),
        duration:1.1,ease:'none'},T0+(dg.length-1-i)*0.08); });
    tl.to(r.querySelector('.unit'),{keyframes:sKF('lively',p=>({scale:0.5+0.5*p,opacity:Math.min(1,p*2.5)})),
      duration:0.6,ease:'none'},T0+1.2); } },

{ g:'数据 & 点缀', id:'badge', name:'徽章 Spring 落入', en:'badge drop',
  meta:'spring 170/16 · y -90px→0 · opacity 前 30% · 地点 pin / 标签',
  html:`<div class="bdg">📍 巧克力山 · 打卡</div>`,
  css:`%% .bdg{position:absolute;left:50%;top:40%;transform:translateX(-50%);background:#d94f2b;color:#fff;border-radius:999px;padding:9px 22px;font-size:15px;font-weight:800;box-shadow:0 10px 30px rgba(217,79,43,.35);opacity:0;white-space:nowrap}`,
  build(r,tl){ tl.to(r.querySelector('.bdg'),{keyframes:springKeyframes(170,16,p=>({y:(1-p)*-90,opacity:Math.min(1,p*3)})),
    duration:0.9,ease:'none'},T0); } },

{ g:'数据 & 点缀', id:'skeleton', name:'骨架流光 → 内容', en:'skeleton→content',
  meta:'shimmer 2×700ms → 内容 ui spring 顶入 90ms 错峰 · 信息卡 / 菜单价格',
  html:`<div class="ic"><div class="skel"><div class="sk" style="width:40%"><i></i></div>
    <div class="sk" style="width:80%;height:20px"><i></i></div><div class="sk" style="width:60%"><i></i></div></div>
    <div class="cnt"><div class="rw k2">TODAY'S PICK</div><div class="rw t2">辣油拌面 · ¥18</div>
    <div class="rw s3">本地人从小吃到大的味道</div></div></div>`,
  css:`%% .ic{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:60%;background:#1d1d25;border-radius:14px;padding:14px;overflow:hidden;min-height:100px}
       %% .sk{height:12px;border-radius:6px;background:#26262e;margin-top:10px;position:relative;overflow:hidden}
       %% .sk:first-child{margin-top:0}
       %% .sk i{position:absolute;inset:0;transform:translateX(-100%);background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,.14) 50%,transparent 70%)}
       %% .cnt{position:absolute;inset:14px;opacity:0}
       %% .k2{color:#ffd76a;font-size:11px;letter-spacing:2px}
       %% .t2{color:#fff;font-size:20px;font-weight:800;margin-top:6px}
       %% .s3{color:#9a9aa5;font-size:12px;margin-top:6px} %% .cnt .rw{opacity:0}`,
  build(r,tl){ for(let k=0;k<2;k++) tl.fromTo(r.querySelectorAll('.sk i'),{xPercent:-100},
      {xPercent:100,duration:0.7,ease:'sine.inOut'},T0+k*0.7);
    tl.set(r.querySelector('.skel'),{autoAlpha:0},T0+1.4);
    tl.set(r.querySelector('.cnt'),{opacity:1},T0+1.4);
    r.querySelectorAll('.cnt .rw').forEach((el,i)=>
      tl.to(el,{keyframes:sKF('ui',p=>({y:(1-p)*18,opacity:Math.min(1,p*2.5)})),
        duration:0.65,ease:'none'},T0+1.4+i*0.09)); } },

{ g:'数据 & 点缀', id:'borderbeam', name:'Border Beam 光弧', en:'border beam',
  meta:'conic 高光沿圆角边框 2.2s/圈 · 2px 边带 · 高亮当前卡/PiP · ≤1 并发',
  html:`<div class="bmw"><div class="bmc"><div class="bm"></div>
    <div class="bmi"><div class="bik">FEATURED</div><div class="bit">本店招牌 · 辣油拌面</div></div></div></div>`,
  css:`%% .bmw{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
       %% .bmc{position:relative;width:240px;height:130px;border-radius:16px;padding:2px;overflow:hidden;opacity:0}
       %% .bm{position:absolute;left:50%;top:50%;width:600px;height:600px;margin:-300px 0 0 -300px;background:conic-gradient(transparent 0deg,transparent 300deg,#ffd76a 340deg,#fff 350deg,transparent 360deg)}
       %% .bmi{position:absolute;inset:2px;border-radius:14px;background:#15151b;display:flex;flex-direction:column;align-items:center;justify-content:center}
       %% .bik{color:#ffd76a;font-size:10px;letter-spacing:3px} %% .bit{color:#fff;font-size:18px;font-weight:800;margin-top:6px}`,
  build(r,tl){ tl.to(r.querySelector('.bmc'),{keyframes:sKF('ui',p=>({opacity:Math.min(1,p*2),scale:0.94+0.06*p})),
      duration:0.6,ease:'none'},T0);
    tl.to(r.querySelector('.bm'),{rotation:360,duration:2.2,ease:'none',repeat:Math.ceil(SCENE_DUR/2.2)},T0); } },

{ g:'数据 & 点缀', id:'aiglow', name:'呼吸光晕边框', en:'breathing glow',
  meta:'conic 彩虹 · blur 26px · 边带 mask · 6s 旋转 + 2.4s 呼吸 · 仅 AI/魔法时刻，需 contract 声明',
  html:`<div class="glw"></div><div class="glb">✨ AI 正在为你回忆这一天</div>`,
  css:`%% .glw{position:absolute;inset:-12%;opacity:0;background:conic-gradient(from 0deg,#ff5f6d,#ffc371,#4facfe,#a18cd1,#ff5f6d);filter:blur(26px) saturate(1.4);-webkit-mask-image:radial-gradient(ellipse 68% 62% at 50% 50%,transparent 58%,#000 78%);mask-image:radial-gradient(ellipse 68% 62% at 50% 50%,transparent 58%,#000 78%)}
       %% .glb{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;font-size:19px;font-weight:700;opacity:0}`,
  build(r,tl){ const g=r.querySelector('.glw');
    tl.to(g,{opacity:0.45,duration:0.5,ease:'none'},T0);
    tl.to(g,{rotation:360,duration:6,ease:'none',repeat:Math.ceil(SCENE_DUR/6)},T0);
    tl.to(g,{opacity:0.9,duration:1.2,ease:'sine.inOut',repeat:Math.ceil(SCENE_DUR/2.4)*2,yoyo:true},T0+0.5);
    tl.to(r.querySelector('.glb'),{keyframes:sKF('gentle',p=>({opacity:Math.min(1,p*1.6),scale:0.96+0.04*p})),
      duration:0.8,ease:'none'},T0+0.3); } },

{ g:'数据 & 点缀', id:'ticker', name:'双向 Ticker', en:'dual ticker',
  meta:'两行反向 linear ~26s/loop · 实心字混 1.5px 描边字 · 片尾字幕 / 关键词墙 / 品牌带',
  html:(()=>{ const w=['BOHOL','巧克力山','辣油拌面','眼镜猴','日落','TIM','海风','菲律宾'];
    const row=o=>w.concat(w).map((x,i)=>`<span class="${(i%2===0)^o?'sol':'out'}">${x}</span>`).join('');
    return `<div class="tk"><div class="tr ta">${row(false)}</div><div class="tr tb">${row(true)}</div></div>`;})(),
  css:`%% .tk{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;gap:16px}
       %% .tr{display:flex;width:max-content}
       %% .tr span{font-size:26px;font-weight:900;margin:0 16px;white-space:nowrap}
       %% .tr .sol{color:#fff} %% .tr .out{color:transparent;-webkit-text-stroke:1.5px rgba(255,255,255,.55)}`,
  build(r,tl){ tl.fromTo(r.querySelector('.ta'),{xPercent:0},{xPercent:-50,duration:26,ease:'none'},T0);
    tl.fromTo(r.querySelector('.tb'),{xPercent:-50},{xPercent:0,duration:26,ease:'none'},T0);
    tl.to({},{duration:0},6); } },

/* ===== D · 社媒 Overlay ===== */
{ g:'社媒 Overlay', id:'bubbles', name:'弹幕评论气泡', en:'live comment bubbles',
  meta:'依次 ui spring 弹入(y26) · 旧泡上滑让位 · ≤3 存活 · 仅 casual/vlog register',
  html:`<div class="cms"><div class="cb"><span>🍜</span>这碗面我可以!</div>
    <div class="cb"><span>👀</span>蹲一个地址</div><div class="cb"><span>🔥</span>老板加辣谢谢</div></div>`,
  css:`%% .cms{position:absolute;left:5%;bottom:8%;display:flex;flex-direction:column-reverse;gap:8px}
       %% .cb{background:rgba(20,20,26,.82);border:1px solid rgba(255,255,255,.14);color:#fff;font-size:12px;border-radius:999px;padding:7px 13px;width:max-content;opacity:0}
       %% .cb span{margin-right:6px}`,
  build(r,tl){ r.querySelectorAll('.cb').forEach((el,i)=>
    tl.to(el,{keyframes:sKF('ui',p=>({y:(1-p)*26,scale:0.86+0.14*p,opacity:Math.min(1,p*2.2)})),
      duration:0.6,ease:'none'},T0+i*0.65)); } },

{ g:'社媒 Overlay', id:'story', name:'Story 章节进度条', en:'story progress',
  meta:'分段 linear 1.1s/段 · 头像 chip spring 入 · 多段叙事导航感',
  html:`<div class="sbar"><div class="seg"><i></i></div><div class="seg"><i></i></div><div class="seg"><i></i></div></div>
    <div class="swho"><div class="ava"></div><span>tim.eats · 第2章</span></div>`,
  css:`%% .sbar{position:absolute;top:8%;left:5%;right:5%;display:flex;gap:6px}
       %% .seg{flex:1;height:4px;border-radius:4px;background:rgba(255,255,255,.18);overflow:hidden}
       %% .seg i{display:block;height:100%;width:100%;background:#ffd76a;transform:scaleX(0);transform-origin:left}
       %% .swho{position:absolute;top:16%;left:5%;display:flex;align-items:center;gap:8px;opacity:0}
       %% .ava{width:28px;height:28px;border-radius:50%;border:2px solid #ffd76a;background:radial-gradient(circle at 35% 30%,#ff9a5f,#d94f2b)}
       %% .swho span{color:#fff;font-size:12px;font-weight:600}`,
  build(r,tl){ tl.to(r.querySelector('.swho'),{keyframes:sKF('ui',p=>({opacity:Math.min(1,p*2),y:(1-p)*10})),
      duration:0.5,ease:'none'},T0);
    r.querySelectorAll('.seg i').forEach((el,i)=>tl.to(el,{scaleX:1,duration:1.1,ease:'none'},T0+i*1.1)); } },

{ g:'社媒 Overlay', id:'arrow', name:'手绘箭头戳戳', en:'arrow poke',
  meta:'path 描画 0.4s expo.out · 朝目标戳 ×3 @0.7s · 视线引导之王 · 配小标签 chip',
  html:`<svg class="arw" viewBox="0 0 640 360"><g class="arg">
    <path class="shf" d="M 470 90 C 420 100, 380 140, 360 190"/>
    <path class="hd" d="M 344 162 L 360 194 L 385 172"/></g></svg>
    <div class="alb">看这里 👇</div>`,
  css:`%% .arw{position:absolute;inset:0;width:100%;height:100%}
       %% .arw path{fill:none;stroke:#ffd76a;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}
       %% .alb{position:absolute;left:42%;top:62%;color:#fff;font-size:14px;font-weight:700;background:rgba(217,79,43,.9);border-radius:999px;padding:6px 14px;opacity:0}`,
  build(r,tl){ r.querySelectorAll('.arw path').forEach(p=>{ const L=p.getTotalLength();
      p.style.strokeDasharray=L; p.style.strokeDashoffset=L; });
    tl.to(r.querySelector('.shf'),{strokeDashoffset:0,duration:0.4,ease:'expo.out'},T0);
    tl.to(r.querySelector('.hd'),{strokeDashoffset:0,duration:0.18,ease:'expo.out'},T0+0.4);
    tl.to(r.querySelector('.alb'),{keyframes:sKF('lively',p=>({opacity:Math.min(1,p*2.5),scale:0.6+0.4*p})),
      duration:0.5,ease:'none'},T0+0.5);
    tl.to(r.querySelector('.arg'),{x:-9,y:12,duration:0.35,ease:'sine.inOut',repeat:5,yoyo:true},T0+0.6); } },

{ g:'社媒 Overlay', id:'speedlines', name:'漫画集中线爆点', en:'comic speedlines',
  meta:'conic 线束闪 ≤0.9s 两帧节奏 · 中心词 lively 撞入+描边 · 戏剧强调 ≤1/片',
  html:`<div class="spl"></div><div class="spw">哇!!</div>`,
  css:`%% .spl{position:absolute;inset:-20%;opacity:0;background:repeating-conic-gradient(from 0deg at 50% 50%,rgba(255,255,255,.9) 0deg 1.6deg,transparent 1.6deg 7deg);-webkit-mask-image:radial-gradient(circle at 50% 50%,transparent 26%,#000 48%);mask-image:radial-gradient(circle at 50% 50%,transparent 26%,#000 48%)}
       %% .spw{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:900;color:#ffd76a;-webkit-text-stroke:2px #1f1f26;opacity:0}`,
  build(r,tl){ tl.to(r.querySelector('.spl'),{keyframes:[{opacity:0},{opacity:1},{opacity:0.55},{opacity:1},{opacity:0}],
      duration:0.9,ease:'steps(1)'},T0);
    tl.to(r.querySelector('.spw'),{keyframes:sKF('lively',p=>({scale:0.2+0.8*p,rotation:-8*(1-p),opacity:Math.min(1,p*3)})),
      duration:0.6,ease:'none'},T0+0.08); } },

{ g:'社媒 Overlay', id:'polaroid', name:'拍立得甩入', en:'polaroid toss-in',
  meta:'ui spring · rotate 18°→-3° 微过冲 · 白框+胶带角+手写日期 · 回忆 / recap',
  html:`<div class="pol"><div class="pho"></div><div class="tap"></div><div class="cap">07.26 · 山谷</div></div>`,
  css:`%% .pol{position:absolute;left:50%;top:50%;width:160px;padding:9px 9px 26px;background:#f5f2ea;border-radius:4px;box-shadow:0 18px 44px rgba(0,0,0,.5);opacity:0;transform:translate(-50%,-50%)}
       %% .pho{height:96px;border-radius:2px;background:linear-gradient(140deg,#3c6e8f,#1d3346)}
       %% .tap{position:absolute;top:-8px;left:50%;width:52px;height:17px;transform:translateX(-50%) rotate(-3deg);background:rgba(255,215,106,.75);border-radius:2px}
       %% .cap{text-align:center;color:#4a453a;font-size:11px;margin-top:7px;font-weight:600}`,
  build(r,tl){ tl.to(r.querySelector('.pol'),{keyframes:sKF('ui',p=>({y:(1-p)*-190,rotation:18-21*p,
    scale:0.8+0.2*p,opacity:Math.min(1,p*2.5)})),duration:0.85,ease:'none'},T0); } },
];

/* ===== E · 过程感 & 运镜（huashu-design 系，2026-07-28 实审） ===== */
window.MOTION_DEMOS.push(
{ g:'过程感 & 运镜', id:'fiveact', name:'五段骨架', en:'Slow-Fast-Boom-Stop',
  meta:'labels @ 15/15/40/20/10% · S1 单动作+留白 → S2 一个惊艳点 → S3 密度最高 → S4 镜头级 → S5 硬停 hold（禁 fade out）',
  html:`<div class="fst"><div class="ftm">$ huashu generate --style=cinematic</div>
    <div class="fpn"><div class="fph">RESULT</div><div class="frw">候选方案 A · 激进</div>
    <div class="frw">候选方案 B · 平衡</div><div class="frw">候选方案 C · 保守</div>
    <div class="frw">评分 · 9.2 / 8.7 / 8.1</div></div><div class="flg">花</div></div>`,
  css:`%% .fst{position:absolute;inset:0;transform-origin:50% 50%}
       %% .ftm{position:absolute;left:8%;top:11%;background:#0d0d13;border:1px solid #33333d;border-radius:8px;padding:9px 12px;color:#4ade80;font-family:ui-monospace,monospace;font-size:11px;opacity:0;white-space:nowrap}
       %% .fpn{position:absolute;left:8%;top:32%;width:58%;background:#26221B;border:1px solid rgba(255,215,106,.3);border-radius:12px;padding:11px 13px;opacity:0}
       %% .fph{color:#ffd76a;font-size:9px;letter-spacing:3px}
       %% .frw{color:#e8e8ec;font-size:11px;margin-top:6px;opacity:0}
       %% .flg{position:absolute;right:12%;top:38%;width:56px;height:56px;border-radius:14px;background:#d94f2b;color:#fff;display:flex;align-items:center;justify-content:center;font-size:26px;font-weight:900;opacity:0}`,
  build(r,tl){ const D=8, at=p=>D*p;
    tl.fromTo(r.querySelector('.ftm'),{y:48,autoAlpha:0},{y:0,autoAlpha:1,duration:0.8,ease:'expo.out'},at(0)+0.1);
    tl.fromTo(r.querySelector('.fpn'),{scale:0.92,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.7,ease:'expo.out'},at(0.15));
    tl.fromTo(r.querySelectorAll('.frw'),{y:10,autoAlpha:0},{y:0,autoAlpha:1,duration:0.4,ease:'expo.out',stagger:0.03},at(0.30));
    tl.to(r.querySelector('.fst'),{scale:0.82,rotationX:8,duration:1.2,ease:'expo.inOut'},at(0.70));
    tl.fromTo(r.querySelector('.flg'),{scale:0.1,autoAlpha:0},{scale:1,autoAlpha:1,duration:0.6,ease:'back.out'},at(0.90)-0.3);
    tl.to({},{duration:0},D); } },

{ g:'过程感 & 运镜', id:'chunk', name:'Chunk Reveal 流式输出', en:'chunk reveal',
  meta:'标点切块 · 40-120ms 种子随机 · proxy onUpdate 每帧重算全文（回拖正确）· 结果前 0.5s 礼让悬停',
  html:`<div class="ckp"><div class="ckt">AI GENERATING…</div><div class="cks"></div>
    <div class="ckr">→ 方案 A 已应用</div></div>`,
  css:`%% .ckp{position:absolute;left:10%;top:24%;width:78%;background:#26221B;border:1px solid rgba(255,215,106,.25);border-radius:12px;padding:13px 15px}
       %% .ckt{color:#ffd76a;font-size:9px;letter-spacing:3px}
       %% .cks{color:#e8e8ec;font-size:14px;line-height:1.7;margin-top:8px;min-height:48px}
       %% .ckr{color:#4ade80;font-size:12px;font-weight:700;margin-top:8px;opacity:0}`,
  build(r,tl){ const rd=prng(42), text='为你生成了三个候选方案，第一个最激进。';
    const ch=text.split(/(?=[，。、；])|(?<=[，。、；])/), times=[]; let acc=0;
    ch.forEach(()=>{acc+=0.04+rd()*0.08;times.push(acc);});
    const el=r.querySelector('.cks'), tw={t:0};
    tl.to(tw,{t:acc,duration:acc,ease:'none',onUpdate(){let n=0;
      while(n<times.length&&times[n]<=tw.t)n++; el.textContent=ch.slice(0,n).join('');}},0.3);
    tl.fromTo(r.querySelector('.ckr'),{scale:0.94,autoAlpha:0},
      {scale:1,autoAlpha:1,duration:0.7,ease:'expo.out'},0.3+acc+0.5); } },

{ g:'过程感 & 运镜', id:'mousearc', name:'鼠标弧线 · 手抖 · 点击', en:'mouse arc', light:true,
  meta:'二次贝塞尔（控制点偏离中点）· 双正弦不可通约手抖 ±2px 近目标收敛 · 点击 0.08s 缩 → back.out 回弹 + 按钮 lit',
  html:`<div class="mab">Generate ✦</div><div class="mac"></div>`,
  css:`%% .mab{position:absolute;right:16%;bottom:24%;background:#1E1B16;color:#F4EFE6;border-radius:10px;padding:11px 22px;font-size:13px;font-weight:700}
       %% .mac{position:absolute;left:0;top:0;width:13px;height:13px;border-radius:50%;background:#d94f2b;box-shadow:0 2px 8px rgba(0,0,0,.35)}`,
  build(r,tl){ const cur=r.querySelector('.mac'), btn=r.querySelector('.mab');
    const W=r.clientWidth||420, H=r.clientHeight||236;
    const P0=[W*0.12,H*0.18], P2=[W*0.74,H*0.68], P1=[P2[0]-W*0.3,P2[1]+H*0.2];
    const m={p:0};
    tl.to(m,{p:1,duration:1.1,ease:'power1.inOut',onUpdate(){const t=m.p;
      let x=(1-t)*(1-t)*P0[0]+2*(1-t)*t*P1[0]+t*t*P2[0];
      let y=(1-t)*(1-t)*P0[1]+2*(1-t)*t*P1[1]+t*t*P2[1];
      x+=Math.sin(t*47.13)*2*(1-t); y+=Math.sin(t*33.7+1.3)*2*(1-t);
      gsap.set(cur,{x,y});}},0.4);
    tl.to(cur,{scale:0.85,duration:0.08,ease:'power1.in'},'>');
    tl.to(cur,{scale:1,duration:0.25,ease:'back.out'},'>');
    tl.to(btn,{scale:1.06,duration:0.3,ease:'expo.out'},'<');
    tl.to(btn,{scale:1,duration:0.3,ease:'expo.out'},'>+0.6');
    gsap.set(cur,{x:P0[0],y:P0[1]}); } },

{ g:'过程感 & 运镜', id:'focus3', name:'焦点切换三件套 + Flash', en:'focus switch trio',
  meta:'非焦点 brightness+saturate+blur 单变量一次 tween（只降 opacity 仍锐利）· 0.15s flash 引导 · 释放必归零',
  html:`<div class="fcg"><div class="fct">方案 A</div><div class="fct ftg">方案 B ★</div>
    <div class="fct">方案 C</div><div class="fct">方案 D</div></div><div class="fcf"></div>`,
  css:`%% .fcg{position:absolute;inset:14% 12%;display:grid;grid-template-columns:1fr 1fr;gap:10px}
       %% .fct{--f:0;filter:brightness(calc(1 - 0.5*var(--f))) saturate(calc(1 - 0.3*var(--f))) blur(calc(var(--f)*4px));will-change:filter;background:#26221B;border:1px solid rgba(255,215,106,.25);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#e8e8ec;font-size:14px;font-weight:700}
       %% .fcf{position:absolute;inset:14% 12%;border-radius:12px;background:rgba(255,255,255,0);pointer-events:none}`,
  build(r,tl){ tl.to(r.querySelectorAll('.fct:not(.ftg)'),{'--f':1,opacity:0.4,duration:0.5,ease:'expo.out'},0.6);
    tl.fromTo(r.querySelector('.fcf'),{backgroundColor:'rgba(255,255,255,0.3)'},
      {backgroundColor:'rgba(255,255,255,0)',duration:0.15,ease:'power1.out'},1.1);
    tl.to(r.querySelectorAll('.fct'),{'--f':0,opacity:1,duration:0.5,ease:'power2.inOut'},3.1); } },

{ g:'过程感 & 运镜', id:'flip', name:'FLIP 按钮 → 输入框', en:'shared element', light:true,
  meta:'同一元素两状态过渡（非两元素 cross-fade）· 终态布局 + 起态纯 transform · 禁 tween width/height · 内文延后入场',
  html:`<div class="flb"><span class="flp">描述你想要的视频…</span></div>
    <div class="flh">同一个元素的两种状态，不是两个元素 cross-fade</div>`,
  css:`%% .flb{position:absolute;left:12%;top:42%;width:58%;height:44px;background:#1E1B16;border-radius:12px;display:flex;align-items:center;padding:0 15px}
       %% .flp{color:#9a9aa5;font-size:12px;opacity:0}
       %% .flh{position:absolute;bottom:12%;left:0;right:0;text-align:center;color:#8a8377;font-size:10px}`,
  build(r,tl){ const b=r.querySelector('.flb'), W=b.clientWidth||235;
    tl.fromTo(b,{x:W*0.4,scaleX:120/W,scaleY:44/48,transformOrigin:'left top'},
      {x:0,scaleX:1,scaleY:1,duration:0.6,ease:'expo.out'},0.4);
    tl.fromTo(r.querySelector('.flp'),{autoAlpha:0},{autoAlpha:1,duration:0.3},0.8); } },

{ g:'过程感 & 运镜', id:'breathe', name:'呼吸式展开', en:'breathing expand',
  meta:'scaleX 0→1 (0.4L) → 0.3L 处 scaleY 撑起 (0.7L) → 内容 0.75L 注水（藏住 scale 期变形）',
  html:`<div class="brp"><div class="brc"><div class="brk">SUMMARY</div>
    <div class="brt">今日拍摄 · 47 段素材</div><div class="brs">高光 12 · 弃用 20 · 待定 15</div></div></div>`,
  css:`%% .brp{position:absolute;left:14%;top:26%;width:54%;background:#26221B;border-radius:14px;padding:13px 15px;min-height:88px}
       %% .brc{opacity:0} %% .brk{color:#ffd76a;font-size:9px;letter-spacing:3px}
       %% .brt{color:#e8e8ec;font-size:16px;font-weight:800;margin-top:6px}
       %% .brs{color:#9a9aa5;font-size:11px;margin-top:5px}`,
  build(r,tl){ const L=0.9, p=r.querySelector('.brp');
    tl.fromTo(p,{scaleX:0,scaleY:0.12,transformOrigin:'left top'},{scaleX:1,duration:0.4*L,ease:'expo.out'},0.3);
    tl.to(p,{scaleY:1,duration:0.7*L,ease:'expo.out'},0.3+0.3*L);
    tl.fromTo(r.querySelector('.brc'),{autoAlpha:0,y:8},{autoAlpha:1,y:0,duration:0.35},0.3+0.75*L); } },

{ g:'过程感 & 运镜', id:'anticip', name:'Anticipation 预备缓动', en:'anticipation', light:true,
  meta:'⟲ 2026-07-28 重新过审 · 左：函数 ease 先下探 -0.3（仅 transform）· 右：三段 预备 power1.in / 主动 expo.out / 回弹 elastic',
  html:`<div class="aca">单段 · 函数 ease</div><div class="acb">三段 · 预备/主动/回弹</div>`,
  css:`%% .aca,%% .acb{position:absolute;top:42%;background:#1E1B16;color:#F4EFE6;border-radius:12px;padding:11px 18px;font-size:14px;font-weight:700}
       %% .aca{left:6%} %% .acb{right:6%}`,
  build(r,tl){ tl.fromTo(r.querySelector('.aca'),{y:40},{y:0,duration:0.7,ease:anticipation},0.2);
    const b=r.querySelector('.acb');
    tl.to(b,{scale:0.95,duration:0.12,ease:'power1.in'},0.2);
    tl.to(b,{scale:1.05,duration:0.30,ease:'expo.out'},0.32);
    tl.to(b,{scale:1.00,duration:0.35,ease:'elastic.out(1,0.3)'},0.62); } },

{ g:'过程感 & 运镜', id:'diagpan', name:'斜向 Pan 双频漂移', en:'diagonal drift',
  meta:'X 4.6s / Y 2.9s 周期不可通约 → 路径不闭合 = 手持镜头感 · repeat 有限 Math.ceil(D/dur)',
  html:`<div class="dpw"><div class="dpc" style="left:12%;top:18%;width:110px;height:72px;background:#26221B"></div>
    <div class="dpc" style="left:48%;top:40%;width:132px;height:86px;background:#2E2820"></div>
    <div class="dpc" style="left:24%;top:64%;width:92px;height:58px;background:#3A322a"></div>
    <div class="dpl">手持镜头感 · X 4.6s / Y 2.9s</div></div>`,
  css:`%% .dpw{position:absolute;inset:-12%}
       %% .dpc{position:absolute;border-radius:12px;border:1px solid rgba(255,215,106,.2)}
       %% .dpl{position:absolute;left:50%;top:48%;transform:translate(-50%,-50%);color:#e8e8ec;font-size:14px;font-weight:700;white-space:nowrap}`,
  build(r,tl){ const D=6, w=r.querySelector('.dpw');
    tl.to(w,{x:40,duration:4.6,ease:'sine.inOut',yoyo:true,repeat:Math.ceil(D/4.6)},0);
    tl.to(w,{y:30,duration:2.9,ease:'sine.inOut',yoyo:true,repeat:Math.ceil(D/2.9)},0); } },

{ g:'过程感 & 运镜', id:'persp3d', name:'3D 黄金视角', en:'golden angle + translateZ',
  meta:'perspective 2400px · 卡片按 3n/5n/7n translateZ 分层（静态）· 入场立到 rotateX 8° / rotateY -4°',
  html:`<div class="p3w"><div class="p3g">${['素材','转场','调色','字幕','BGM','特效','评审','渲染','交付']
    .map(t=>`<div class="p3c">${t}</div>`).join('')}</div></div>`,
  css:`%% .p3w{position:absolute;inset:0;perspective:2400px;perspective-origin:50% 30%;display:flex;align-items:center;justify-content:center}
       %% .p3g{transform-style:preserve-3d;display:grid;grid-template-columns:repeat(3,96px);gap:9px}
       %% .p3c{height:56px;background:#26221B;border:1px solid rgba(255,215,106,.25);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#e8e8ec;font-size:12px;font-weight:700}
       %% .p3c:nth-child(3n){transform:translateZ(30px)}
       %% .p3c:nth-child(5n){transform:translateZ(-20px)}
       %% .p3c:nth-child(7n){transform:translateZ(60px)}`,
  build(r,tl){ tl.fromTo(r.querySelector('.p3g'),{rotationX:0,rotationY:0},
    {rotationX:8,rotationY:-4,duration:1.4,ease:'expo.out'},0.3); } },

{ g:'过程感 & 运镜', id:'camrig', name:'Camera Rig 四段运镜', en:'camera rig',
  meta:'cam proxy 驱动（运镜与元素动画不抢 transform）· zoomDur 对数时长 · 定场微推 → 推近 hold → followEase 平移 → 谢幕拉出 + hold',
  html:`<div class="crv"><div class="crw">
    <div class="crb" style="left:8%;top:14%">开场板</div>
    <div class="crb crh" style="left:58%;top:20%">特写目标</div>
    <div class="crb" style="left:30%;top:58%">次要面板</div></div></div>
    <div class="crh2">HUD 恒定（#hud 不跟镜头）</div>`,
  css:`%% .crv{position:absolute;inset:0;overflow:hidden}
       %% .crw{position:absolute;inset:-10%;transform-origin:0 0;will-change:transform}
       %% .crb{position:absolute;width:30%;height:26%;background:#26221B;border:1px solid rgba(255,215,106,.25);border-radius:12px;display:flex;align-items:center;justify-content:center;color:#e8e8ec;font-size:12px;font-weight:700}
       %% .crh{border-color:#d94f2b;color:#ffd76a}
       %% .crh2{position:absolute;right:3%;bottom:4%;color:#9a9aa5;font-size:10px;letter-spacing:1px}`,
  build(r,tl){ const world=r.querySelector('.crw');
    const W=r.clientWidth||420, H=r.clientHeight||236;
    const cam={cx:W/2,cy:H/2,zoom:1};
    const applyCam=()=>{world.style.transform=
      `translate(${W/2-cam.cx*cam.zoom}px, ${H/2-cam.cy*cam.zoom}px) scale(${cam.zoom})`;};
    const zoomDur=(z1,z2)=>gsap.utils.clamp(0.30,0.94,0.55*Math.abs(Math.log(z2/z1))/Math.LN2);
    tl.fromTo(cam,{zoom:1.06},{zoom:1,duration:1.2,ease:'power2.out',onUpdate:applyCam},0);
    tl.to(cam,{cx:W*0.73,cy:H*0.33,zoom:1.8,duration:zoomDur(1,1.8),ease:'power3.inOut',onUpdate:applyCam},1.4);
    tl.to(cam,{cx:W*0.45,cy:H*0.71,duration:0.7,ease:gsap.parseEase('0.33,0,0.15,1'),onUpdate:applyCam},3.1);
    tl.to(cam,{cx:W/2,cy:H/2,zoom:1,duration:0.55,ease:'power3.inOut',onUpdate:applyCam},4.4);
    tl.to({},{duration:0},5.8);
    applyCam(); } },
);
