(function(){
  // Get csrftoken from cookie (Django default)
  function getCookie(name){
    const v = `; ${document.cookie}`;
    const parts = v.split(`; ${name}=`);
    if(parts.length === 2) return parts.pop().split(';').shift();
  }
  const CSRF = getCookie('csrftoken');
  const sleep = (ms)=>new Promise(r=>setTimeout(r,ms));

  function ajax(url, opts){
    opts = opts || {};
    const headers = opts.headers || {};
    if(!headers['X-Requested-With']) headers['X-Requested-With'] = 'XMLHttpRequest';
    if(!headers['Content-Type'] && opts.method==='POST') headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8';
    if(CSRF && opts.method==='POST') headers['X-CSRFToken'] = CSRF;
    opts.headers = headers;
    return fetch(url, opts).then(r=>r.json().catch(()=>({}))).catch(()=>({}));
  }

  function showBadge(count){
    const badge = document.getElementById('notifications-badge');
    if(!badge) return;
    if(count>0){ badge.style.display='inline-block'; badge.textContent = count; }
    else badge.style.display='none';
  }

  async function updateCount(){
    try{
  const res = await ajax('/notifications/count-unread/');
      if(res && typeof res.unread_count !== 'undefined') showBadge(res.unread_count);
    }catch(e){}
  }

  function buildItem(n){
    const div = document.createElement('div');
    div.className = 'notification-item d-flex gap-2 align-items-start py-2 border-bottom';
    div.dataset.id = n.id;
    const icon = document.createElement('div');
    icon.innerHTML = n.tipo==='follow'? '<i class="bi bi-person-plus-fill text-success"></i>' : (n.tipo==='like'? '<i class="bi bi-heart-fill text-danger"></i>' : '<i class="bi bi-chat-left-text-fill text-primary"></i>');
    icon.style.width='28px';
    const content = document.createElement('div');
    content.style.flex='1';
    const p = document.createElement('div');
    p.className = 'small';
    p.textContent = n.mensaje;
    const meta = document.createElement('div');
    meta.className='text-muted small';
    meta.textContent = n.fecha.replace('T',' ');
    content.appendChild(p); content.appendChild(meta);
    const actions = document.createElement('div');
    actions.innerHTML = '<button class="btn btn-sm btn-link mark-read">✓</button>';
    if(n.leida) div.style.opacity = 0.6;
    div.appendChild(icon); div.appendChild(content); div.appendChild(actions);
    // click mark read
    actions.querySelector('.mark-read').addEventListener('click', async (ev)=>{
      ev.stopPropagation();
  await ajax(`/notifications/mark-read/${n.id}/`, {method:'POST'});
      div.style.opacity = 0.6;
      updateCount();
    });
    return div;
  }

  async function loadList(){
    const list = document.getElementById('notifications-list');
    if(!list) return;
    list.innerHTML = '<div class="text-center p-3">Cargando...</div>';
    try{
  const res = await ajax('/notifications/list/');
      list.innerHTML='';
      if(res.notifications && res.notifications.length){
        res.notifications.forEach(n=> list.appendChild(buildItem(n)));
      } else {
        list.innerHTML = '<div class="text-center p-3 text-muted">No hay notificaciones</div>';
      }
    }catch(e){
      list.innerHTML = '<div class="text-center p-3 text-danger">Error al cargar</div>';
    }
  }

  document.addEventListener('DOMContentLoaded', ()=>{
  const btn = document.getElementById('notificationsDropdown');
  const dropdown = document.getElementById('notifications-dropdown');
    const markAllBtn = document.getElementById('mark-all-read');
    if(!btn) return;

    // toggle dropdown visibility manually
    btn.addEventListener('click', async (e)=>{
      e.preventDefault();
      const dd = dropdown;
      if(!dd) return;
      if(dd.style.display === 'none' || dd.style.display === ''){
        dd.style.display = 'block';
        await loadList();
      } else {
        dd.style.display = 'none';
      }
    });

    // mark all
    if(markAllBtn){
      markAllBtn.addEventListener('click', async (ev)=>{
        ev.preventDefault();
  await ajax('/notifications/mark-all-read/', {method:'POST'});
        await loadList();
        updateCount();
      });
    }

    // polling for unread count
    updateCount();
    setInterval(updateCount, 8000);
  });
})();
