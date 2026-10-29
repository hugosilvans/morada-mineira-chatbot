let cartId = null;
let currentMenu = [];
let currentItemToAdd = null;

let cartPromise = null;

async function ensureCart() {
  if (cartId) return cartId;
  if (!cartPromise) {
    cartPromise = (async () => {
      const resposta = await fetch('/api/create_cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      });
      if (!resposta.ok) throw new Error('Não foi possível criar o carrinho.');
      const dados = await resposta.json();
      cartId = dados.cart_id;
      return cartId;
    })().finally(() => {
      cartPromise = null;
    });
  }
  return cartPromise;
}

function getTimeString() {
  const now = new Date();
  return now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
}

// Mensagens são texto; textContent impede que HTML digitado seja executado.
function appendMessage(cls, text, isBot = true) {
  const chat = document.getElementById('chat');
  const message = document.createElement('div');
  message.className = isBot ? 'bot-msg' : 'user-msg';
  if (isBot) {
    const avatar = document.createElement('img');
    avatar.src = '/static/images/MimoBot.png';
    avatar.alt = 'Bot';
    avatar.className = 'bot-avatar';
    message.appendChild(avatar);
  }
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  const content = document.createElement('div');
  content.className = 'message-text';
  content.style.whiteSpace = 'pre-wrap';
  content.textContent = String(text ?? '');
  const time = document.createElement('div');
  time.className = 'message-time';
  time.textContent = getTimeString();
  bubble.append(content, time);
  message.appendChild(bubble);
  chat.appendChild(message);
  chat.scrollTop = chat.scrollHeight;
}

function escapeHtml(value) {
  return String(value ?? '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );
}

async function sendMessage(text) {
  appendMessage(null, text, false);
  const res = await fetch('/api/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text, cart_id: cartId }),
  });
  const j = await res.json();
  appendMessage(null, j.text || 'OK', true);
  // respond to actions
  if (j.action === 'open_menu') openMenu();
  if (j.action === 'open_best_sellers') openBestSellers();
  if (j.action === 'open_cart') openCartModal();
  if (j.action === 'open_support') window.open('/support', '_blank');
}

async function openMenu() {
  const res = await fetch('/api/categories');
  const j = await res.json();
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'bot-msg';
  div.innerHTML = `
    <img src="/static/images/MimoBot.png" alt="Bot" class="bot-avatar" />
    <div class="message-bubble">
      <div class="message-text"><strong>Selecione uma categoria:</strong></div>
      <div class="message-time">${getTimeString()}</div>
    </div>
  `;
  chat.appendChild(div);

  j.categories.forEach((category) => {
    const categoryBtn = document.createElement('button');
    categoryBtn.style.cssText =
      'margin:6px;padding:10px 14px;background:#FF7800;color:#fff;border:0;border-radius:4px;cursor:pointer;font-weight:bold;flex:1;min-width:100px;';
    categoryBtn.textContent = category;
    categoryBtn.onclick = () => openMenuByCategory(category);
    chat.appendChild(categoryBtn);
  });

  const backDiv = document.createElement('div');
  backDiv.style.cssText = 'display:flex;gap:6px;margin:6px 0;flex-wrap:wrap;';
  chat.appendChild(backDiv);

  chat.scrollTop = chat.scrollHeight;
}

async function openMenuByCategory(category) {
  const res = await fetch(`/api/category/${encodeURIComponent(category)}`);
  const j = await res.json();
  currentMenu = j.items;
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'bot-msg';
  div.innerHTML = `
    <img src="/static/images/MimoBot.png" alt="Bot" class="bot-avatar" />
    <div class="message-bubble">
      <div class="message-text"><strong>${escapeHtml(category)}:</strong></div>
      <div class="message-time">${getTimeString()}</div>
    </div>
  `;
  chat.appendChild(div);

  j.items.forEach((it) => {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'menu-item';
    itemDiv.innerHTML = `
      <img src="${escapeHtml(it.picture_url)}" alt="${escapeHtml(it.name)}" style="width:100%;height:120px;object-fit:cover;border-radius:4px;margin-bottom:8px;" />
      <div class="item-name">${escapeHtml(it.name)}</div>
      <div class="item-price">R$ ${it.base_price.toFixed(2)}</div>
      ${it.description ? `<div class="item-desc">${escapeHtml(it.description)}</div>` : ''}
      <button onclick="openAddModal(${it.id})" style="margin-top:8px;padding:6px 10px;background:#FF7800;color:#fff;border:0;border-radius:4px;cursor:pointer;width:100%;">Adicionar ao Carrinho</button>
    `;
    chat.appendChild(itemDiv);
  });

  const backBtn = document.createElement('button');
  backBtn.style.cssText =
    'margin-top:8px;padding:8px 12px;background:#95a5a6;color:#fff;border:0;border-radius:4px;cursor:pointer;font-weight:bold;width:100%;';
  backBtn.textContent = '← Voltar ao Menu';
  backBtn.onclick = openMenu;
  chat.appendChild(backBtn);

  chat.scrollTop = chat.scrollHeight;
}

async function openBestSellers() {
  const res = await fetch('/api/best_sellers_categories');
  const j = await res.json();
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'bot-msg';
  div.innerHTML = `
    <img src="/static/images/MimoBot.png" alt="Bot" class="bot-avatar" />
    <div class="message-bubble">
      <div class="message-text"><strong>Selecione uma categoria de favoritos:</strong></div>
      <div class="message-time">${getTimeString()}</div>
    </div>
  `;
  chat.appendChild(div);

  j.categories.forEach((category) => {
    const categoryBtn = document.createElement('button');
    categoryBtn.style.cssText =
      'margin:6px;padding:10px 14px;background:#FF7800;color:#fff;border:0;border-radius:4px;cursor:pointer;font-weight:bold;flex:1;min-width:100px;';
    categoryBtn.textContent = category;
    categoryBtn.onclick = () => openBestSellersByCategory(category);
    chat.appendChild(categoryBtn);
  });

  chat.scrollTop = chat.scrollHeight;
}

async function openBestSellersByCategory(category) {
  const res = await fetch(`/api/best_sellers_category/${encodeURIComponent(category)}`);
  const j = await res.json();
  currentMenu = j.items;
  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'bot-msg';
  div.innerHTML = `
    <img src="/static/images/MimoBot.png" alt="Bot" class="bot-avatar" />
    <div class="message-bubble">
      <div class="message-text"><strong>Favoritos - ${escapeHtml(category)}:</strong></div>
      <div class="message-time">${getTimeString()}</div>
    </div>
  `;
  chat.appendChild(div);

  j.items.forEach((b) => {
    const itemDiv = document.createElement('div');
    itemDiv.className = 'menu-item';
    itemDiv.innerHTML = `
      <img src="${escapeHtml(b.picture_url)}" alt="${escapeHtml(b.name)}" style="width:100%;height:120px;object-fit:cover;border-radius:4px;margin-bottom:8px;" />
      <div class="item-name">${escapeHtml(b.name)}</div>
      <div class="item-price">R$ ${b.base_price.toFixed(2)}</div>
      <div class="item-desc">Vendidos: ${b.count}</div>
      <button onclick="openAddModal(${b.id})" style="margin-top:8px;padding:6px 10px;background:#FF7800;color:#fff;border:0;border-radius:4px;cursor:pointer;width:100%;">Adicionar ao Carrinho</button>
    `;
    chat.appendChild(itemDiv);
  });

  const backBtn = document.createElement('button');
  backBtn.style.cssText =
    'margin-top:8px;padding:8px 12px;background:#95a5a6;color:#fff;border:0;border-radius:4px;cursor:pointer;font-weight:bold;width:100%;';
  backBtn.textContent = '← Voltar aos Favoritos';
  backBtn.onclick = openBestSellers;
  chat.appendChild(backBtn);

  chat.scrollTop = chat.scrollHeight;
}

async function openAddModal(itemId) {
  let item = currentMenu.find((i) => i.id === itemId);
  // Sugestões e favoritos podem vir sem opções; consulte o cardápio completo.
  if (!item || !item.options) {
    const resposta = await fetch('/api/menu');
    if (!resposta.ok) return appendMessage(null, 'Não foi possível carregar o produto.');
    const dados = await resposta.json();
    currentMenu = dados.menu;
    item = currentMenu.find((i) => i.id === itemId);
  }
  if (!item) return;

  currentItemToAdd = item;
  document.getElementById('modalTitle').textContent = item.name;
  document.getElementById('modalDesc').textContent = item.description || '';
  document.getElementById('quantityInput').value = '1';

  // Build options UI
  const optContainer = document.getElementById('optionsContainer');
  optContainer.innerHTML = '';

  if (item.options && Object.keys(item.options).length > 0) {
    for (const [groupKey, groupData] of Object.entries(item.options)) {
      const groupDiv = document.createElement('div');
      groupDiv.className = 'option-group';

      const label = document.createElement('label');
      label.textContent = groupKey.charAt(0).toUpperCase() + groupKey.slice(1) + ':';
      groupDiv.appendChild(label);

      const inputType = groupData.type === 'multiple' ? 'checkbox' : 'radio';
      const name = `opt-${groupKey}-${itemId}`;

      groupData.choices.forEach((choice, idx) => {
        const choiceDiv = document.createElement('div');
        choiceDiv.className = 'option-choice';

        const input = document.createElement('input');
        input.type = inputType;
        input.name = name;
        input.value = choice.id;
        input.id = `choice-${name}-${idx}`;

        const lbl = document.createElement('label');
        lbl.htmlFor = input.id;
        lbl.textContent = `${choice.label} (+$${choice.extra.toFixed(2)})`;

        choiceDiv.appendChild(input);
        choiceDiv.appendChild(lbl);
        groupDiv.appendChild(choiceDiv);
      });

      optContainer.appendChild(groupDiv);
    }
  }

  document.getElementById('addModal').style.display = 'block';
}

async function addItemToCart() {
  if (!currentItemToAdd) return;

  // Collect selected options
  const selectedOptions = [];
  for (const [groupKey, groupData] of Object.entries(currentItemToAdd.options || {})) {
    const inputType = groupData.type === 'multiple' ? 'checkbox' : 'radio';
    const name = `opt-${groupKey}-${currentItemToAdd.id}`;
    const checked = Array.from(document.querySelectorAll(`input[name="${name}"]:checked`));
    checked.forEach((c) => selectedOptions.push(parseInt(c.value)));
  }

  const qty = Number(document.getElementById('quantityInput').value);
  if (!Number.isInteger(qty) || qty < 1 || qty > 10000) {
    return appendMessage(null, 'Informe uma quantidade inteira entre 1 e 10000.');
  }
  await ensureCart();

  const res = await fetch('/api/add_to_cart', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      cart_id: cartId,
      menu_item_id: currentItemToAdd.id,
      selected_options: selectedOptions,
      quantity: qty,
    }),
  });

  if (!res.ok) {
    const erro = await res.json();
    return appendMessage(null, erro.error || 'Não foi possível adicionar o item.');
  }
  if (res.ok) {
    appendMessage('bot-msg', `✓ Adicionado ${qty}x ${currentItemToAdd.name} ao carrinho!`);
    document.getElementById('addModal').style.display = 'none';
    currentItemToAdd = null;
  }
}

async function openCartModal() {
  const res = await fetch(`/api/cart/${cartId}`);
  const j = await res.json();

  const cartItemsDiv = document.getElementById('cartItems');
  cartItemsDiv.innerHTML = '';

  if (j.items.length === 0) {
    cartItemsDiv.innerHTML = '<p style="text-align:center;color:#999;">Seu carrinho está vazio</p>';
  } else {
    j.items.forEach((item) => {
      const itemDiv = document.createElement('div');
      itemDiv.className = 'cart-item';
      itemDiv.innerHTML = `
        <div class="cart-item-info">
          <div class="cart-item-name">${escapeHtml(item.menu_item_name)}</div>
          <div class="cart-item-details">Qtd: ${item.quantity} × R$ ${item.unit_price.toFixed(2)} = R$ ${(item.quantity * item.unit_price).toFixed(2)}</div>
        </div>
        <button onclick="removeFromCart(${item.id})" class="btn-danger">Remover</button>
      `;
      cartItemsDiv.appendChild(itemDiv);
    });
  }

  document.getElementById('cartTotal').textContent = `R$ ${j.total.toFixed(2)}`;
  document.getElementById('cartModal').style.display = 'block';
}

async function removeFromCart(cartItemId) {
  const res = await fetch('/api/remove_item', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cart_item_id: cartItemId, cart_id: cartId }),
  });

  if (res.ok) {
    openCartModal();
    appendMessage('bot-msg', '✓ Item removido do carrinho');
  }
}

async function checkout() {
  const res = await fetch('/api/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cart_id: cartId }),
  });

  if (!res.ok) return appendMessage(null, 'Não foi possível finalizar o carrinho.');
  if (res.ok) {
    const j = await res.json();
    appendMessage(null, `Resumo do Pedido:\n${j.resumo}`, true);
    const chat = document.getElementById('chat');
    const buttonDiv = document.createElement('div');
    buttonDiv.style.display = 'flex';
    buttonDiv.style.justifyContent = 'center';
    buttonDiv.style.marginTop = '8px';
    const btn = document.createElement('a');
    btn.href = j.whatsapp_link;
    btn.target = '_blank';
    btn.rel = 'noopener noreferrer';
    btn.textContent = 'Enviar via WhatsApp';
    btn.style.cssText =
      'background:#25D366;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;cursor:pointer;';
    btn.onmouseover = () => (btn.style.background = '#20BA58');
    btn.onmouseout = () => (btn.style.background = '#25D366');
    buttonDiv.appendChild(btn);
    chat.appendChild(buttonDiv);
    chat.scrollTop = chat.scrollHeight;
    document.getElementById('cartModal').style.display = 'none';
    // Reset cart
    cartId = null;
    await ensureCart();
  }
}

async function askSuggestions() {
  appendMessage(
    'bot-msg',
    'Por favor, digite três valores separados por vírgulas: quantidade de pessoas, tipo de evento, local (ex: "60, casamento, São Paulo")',
  );
}

async function doSuggestions(input) {
  const parts = input.split(',').map((p) => p.trim());
  if (parts.length < 3)
    return appendMessage(null, 'Formato inválido. Forneça: quantidade, tipo, local', true);
  const payload = {
    quantidade_de_pessoas: parts[0],
    tipo_de_festa: parts[1],
    localização: parts[2],
  };

  const res = await fetch('/api/suggestions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const j = await res.json();

  if (!res.ok) return appendMessage(null, j.error || 'Não foi possível obter sugestões.');
  if (!j.sugestões || j.sugestões.length === 0)
    return appendMessage(null, 'Nenhuma sugestão disponível.', true);

  const chat = document.getElementById('chat');
  const div = document.createElement('div');
  div.className = 'bot-msg';
  div.innerHTML = `
    <img src="/static/images/MimoBot.png" alt="Bot" class="bot-avatar" />
    <div class="message-bubble">
      <div class="message-text"><strong>Sugestões para ${j.quantidade_de_pessoas} pessoas (Desconto: ${(j.desconto * 100).toFixed(0)}%):</strong></div>
      <div class="message-time">${getTimeString()}</div>
    </div>
  `;
  chat.appendChild(div);

  j.sugestões.forEach((s) => {
    const suggDiv = document.createElement('div');
    suggDiv.className = 'menu-item';
    suggDiv.innerHTML = `
      <img src="${escapeHtml(s.picture_url || '/static/images/PlaceHolder.jpg')}" alt="${escapeHtml(s.name)}" style="width:100%;height:120px;object-fit:cover;border-radius:4px;margin-bottom:8px;" />
      <div class="item-name">${escapeHtml(s.name)}</div>
      <div class="item-price">Estimado: R$ ${s.estimate}</div>
      <div class="item-desc">${escapeHtml(s.category)}${s.discount_applied ? ' (desconto em volume aplicado)' : ''}</div>
      <button onclick="openAddModal(${s.id})" style="margin-top:8px;padding:6px 10px;background:#FF7800;color:#fff;border:0;border-radius:4px;cursor:pointer;width:100%;">Adicionar ao Carrinho</button>
    `;
    chat.appendChild(suggDiv);
  });
  chat.scrollTop = chat.scrollHeight;
}

// Modal close handlers
document.querySelectorAll('.modal-close').forEach((el) => {
  el.addEventListener('click', function () {
    this.closest('.modal').style.display = 'none';
  });
});

window.addEventListener('click', (e) => {
  if (e.target.id === 'addModal') document.getElementById('addModal').style.display = 'none';
  if (e.target.id === 'cartModal') document.getElementById('cartModal').style.display = 'none';
});

// Main button listeners
document.getElementById('send').addEventListener('click', async () => {
  const input = document.getElementById('user-input');
  const text = input.value.trim();
  if (!text) return;
  const lastBot = Array.from(document.getElementsByClassName('bot-msg')).slice(-1)[0];
  if (
    lastBot &&
    lastBot.textContent &&
    (lastBot.textContent.toLowerCase().includes('por favor') ||
      lastBot.textContent.toLowerCase().includes('três valores'))
  ) {
    await doSuggestions(text);
  } else {
    await ensureCart();
    await sendMessage(text);
  }
  input.value = '';
});

document.getElementById('btn-menu').addEventListener('click', () => {
  sendMessage('menu');
});
document.getElementById('btn-best').addEventListener('click', () => {
  sendMessage('mais vendidos');
});
document.getElementById('btn-cart').addEventListener('click', async () => {
  await ensureCart();
  await openCartModal();
});
document.getElementById('btn-support').addEventListener('click', () => {
  window.open('/support', '_blank');
});
document.getElementById('btn-suggest').addEventListener('click', async () => {
  await askSuggestions();
});

document.getElementById('addToCartBtn').addEventListener('click', addItemToCart);
document.getElementById('cancelBtn').addEventListener('click', () => {
  document.getElementById('addModal').style.display = 'none';
});
document.getElementById('checkoutBtn').addEventListener('click', checkout);
document.getElementById('closecartBtn').addEventListener('click', () => {
  document.getElementById('cartModal').style.display = 'none';
});

// Initialize cart on load
ensureCart();

window.addEventListener('unhandledrejection', (event) => {
  event.preventDefault();
  appendMessage(null, 'Não foi possível comunicar com o servidor. Tente novamente.');
});
