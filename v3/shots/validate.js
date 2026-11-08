const S=require('../shots.json');
const fs=require('fs'),path=require('path');
const CH=new Set(['marcel','gaston','s1','s2','s3']),SETS=new Set(['camp','insert','night','tent']);
const POSE=new Set('idle walk point stab kick smash_down throw sit recoil shock sigh chew bite peer eyes_closed smug march'.split(' '));
const FACE=new Set('neutral hungry determined pain smug shock betrayed chewing eyes_shut'.split(' '));
const PROP=new Set('can lid crate label_card chisel hammer opener_1858 knife boot rock pan'.split(' '));
const EXTRA=new Set(['scale','food']); // optional props requested from SETS
const ANCH=new Set('marcel_spot gaston_spot crate tree fire table'.split(' '));
const FXT=new Set('puff speedlines sparkle godrays'.split(' ')),TR=new Set(['travel','whip','dissolve','cut']); // 'cut' = hard cut (the 60 s example uses it)
const SIZES=new Set('XW WIDE MED CU MACRO EWS WS FS MS MCU INS'.split(' '));
const warn=[];
const e=[];let prev=0;
const ck=(c,m)=>{if(!c)e.push(m)};
const anc=v=>!v||Array.isArray(v)||v==='night'||ANCH.has(v.anchor||v);
for(const s of S){
 ck(s.f_in===prev,`${s.id} gap/overlap at ${s.f_in}`);prev=s.f_out;
 ck(s.f_in<s.f_out,s.id+' f_in>=f_out');ck(SETS.has(s.set),s.id+' set');ck(TR.has(s.transition_in),s.id+' transition');
 ck(s.camera.length>=2&&s.camera[0].f===s.f_in&&s.camera.at(-1).f===s.f_out,s.id+' cam span');
 ck(s.camera.every((c,i)=>!i||c.f-s.camera[i-1].f>=20),s.id+' cam ease<20f');
 ck(s.camera.every(c=>Math.abs(c.roll_deg||0)<=12&&anc(c.pos)&&anc(c.target)),s.id+' cam roll/anchor');
 ck(s.camera.every(c=>!c.size||SIZES.has(c.size)),s.id+' camera key size');
 ck(s.camera.slice(1,-1).every(c=>c.pos||c.subj||s.subj),s.id+' middle camera key needs pos or subj (else it falls back to the first key\'s pose)');   // optional per-key size: the camera changes framing inside the shot
 for(const a of s.actions){ck(a.f>=s.f_in&&a.f<=s.f_out,`${s.id} action f ${a.f}`);ck(CH.has(a.char),s.id+' char '+a.char);
  if(a.act==='pose')ck(POSE.has(a.args.name),s.id+' pose '+a.args.name);
  if(a.act==='face')ck(FACE.has(a.args.name),s.id+' face '+a.args.name);
  if(a.act==='hold')ck(PROP.has(a.args.prop),s.id+' hold '+a.args.prop);
  if(a.act==='place')ck(anc(a.args.loc),s.id+' place anchor');}
 for(const p of s.props)ck((PROP.has(p.prop)||EXTRA.has(p.prop))&&p.f>=s.f_in&&p.f<=s.f_out,`${s.id} prop ${p.prop}@${p.f}`);
 for(const x of s.fx)ck(FXT.has(x.type)&&x.f>=s.f_in&&x.f<=s.f_out&&anc(x.at),`${s.id} fx ${x.type}@${x.f}`);
}
// length: must cover the narration (voice-timing.json), not a fixed 1815 frames
const TF=path.join(__dirname,'..','voice','voice-timing.json');
if(fs.existsSync(TF)){const T=JSON.parse(fs.readFileSync(TF,'utf8').replace(/^\uFEFF/,''));ck(prev>=Math.round(T.duration*30),`ends at ${prev} before the narration ends (${Math.round(T.duration*30)})`);}
for(let i=1;i<S.length;i++)if(S[i].size===S[i-1].size&&S[i].set===S[i-1].set)warn.push(`${S[i].id} repeats size ${S[i].size} in the same set`);
// pacing against references/reference-style.md (warnings: a reason from the story can override them)
const pic=S.slice(1).filter(s=>s.transition_in!=='travel'),cuts=pic.map(s=>s.f_in),segs=[0,...cuts,prev].slice(1).map((f,i)=>(f-[0,...cuts][i])/30);
const asl=segs.reduce((a,b)=>a+b,0)/segs.length,longest=Math.max(...segs),dis=pic.filter(s=>s.transition_in==='dissolve').length/Math.max(1,pic.length);
if(asl<3.1||asl>5.1)warn.push(`average shot ${asl.toFixed(2)} s (reference 4.3 s, 3.1-5.1): shots change by camera moves, not cuts`);
if(longest>8.6)warn.push(`longest shot ${longest.toFixed(1)} s (reference never over 8.6 s)`);
if(dis<0.79)warn.push(`dissolves are ${Math.round(dis*100)}% of transitions (reference 95%, 79-100%)`);
const nw=pic.filter(s=>s.transition_in==='whip').length;if(nw)warn.push(`${nw} whip transitions (reference: none)`);
const cnt=k=>S.reduce((m,s)=>(m[s[k]]=(m[s[k]]||0)+1,m),{});
if(warn.length)console.log('WARN\n'+warn.join('\n'));
console.log(e.length?'FAIL\n'+e.join('\n'):'OK',S.length,'shots',`${pic.length+1} picture shots, average ${asl.toFixed(2)} s`,JSON.stringify(cnt('size')),JSON.stringify(cnt('transition_in')),'dutch',S.filter(s=>/dutch/.test(s.angle)||s.camera.some(c=>Math.abs(c.roll_deg)>=5)).length);
