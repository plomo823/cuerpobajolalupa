// Menú móvil
const menuBtn=document.querySelector('.menu-button'),nav=document.querySelector('.navlinks');
menuBtn?.addEventListener('click',()=>{const open=!nav.classList.contains('open');nav.classList.toggle('open',open);menuBtn.setAttribute('aria-expanded',String(open));});

// Desplegables: clic (móvil y teclado); en escritorio también se abren al pasar el ratón
document.querySelectorAll('.drop-toggle').forEach(btn=>{
  btn.addEventListener('click',e=>{
    e.stopPropagation();
    const dd=btn.parentElement,open=!dd.classList.contains('open');
    document.querySelectorAll('.dropdown.open').forEach(d=>{if(d!==dd){d.classList.remove('open');d.querySelector('.drop-toggle').setAttribute('aria-expanded','false');}});
    dd.classList.toggle('open',open);btn.setAttribute('aria-expanded',String(open));
  });
});
document.addEventListener('click',e=>{if(!e.target.closest('.dropdown'))document.querySelectorAll('.dropdown.open').forEach(d=>{d.classList.remove('open');d.querySelector('.drop-toggle').setAttribute('aria-expanded','false');});});
document.addEventListener('keydown',e=>{if(e.key==='Escape')document.querySelectorAll('.dropdown.open').forEach(d=>d.classList.remove('open'));});

// Buscador de la página «Todas las guías»
const q=document.getElementById('q');
if(q){
  const norm=s=>s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
  const cards=[...document.querySelectorAll('.guide-card')],sections=[...document.querySelectorAll('.topic-section')],empty=document.querySelector('.search-empty');
  const filter=()=>{
    const words=norm(q.value.trim()).split(/\s+/).filter(Boolean);let shown=0;
    cards.forEach(c=>{const hay=norm(c.dataset.search||c.textContent);const ok=words.every(w=>hay.includes(w));c.hidden=!ok;if(ok)shown++;});
    sections.forEach(s=>{s.hidden=![...s.querySelectorAll('.guide-card')].some(c=>!c.hidden);});
    if(empty)empty.hidden=shown>0;
  };
  q.addEventListener('input',filter);
  const p=new URLSearchParams(location.search).get('q');
  if(p){q.value=p;filter();}
  if(location.hash==='#buscar')q.focus();
}

// Calculadora de minutos activos (portada)
const sessions=document.getElementById('sessions'),minutes=document.getElementById('minutes'),result=document.getElementById('diag-result');
function calculateActivity(){if(!sessions||!minutes||!result)return;const total=Number(sessions.value)*Number(minutes.value);let title='',desc='';if(total===0){title='0 minutos esta semana';desc='Puedes empezar con una cantidad de actividad adaptada a tu situación, si tu estado de salud lo permite.';}else if(total<150){title=total+' minutos a la semana';desc='Estás por debajo de la referencia general de 150 minutos de actividad moderada para adultos. Cualquier cantidad de movimiento cuenta.';}else if(total<=300){title=total+' minutos a la semana';desc='Tu suma se encuentra en el intervalo general de 150 a 300 minutos semanales de actividad moderada que recomienda la OMS.';}else{title=total+' minutos a la semana';desc='Has superado el intervalo de referencia de 150 a 300 minutos. Más ejercicio no siempre es adecuado para todas las personas.';}result.innerHTML='<strong>'+title+'</strong><p>'+desc+'</p><small>La cuenta no incluye actividad vigorosa ni fuerza. No es una evaluación de salud.</small>';}
sessions?.addEventListener('change',calculateActivity);minutes?.addEventListener('change',calculateActivity);calculateActivity();
