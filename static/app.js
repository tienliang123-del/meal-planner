const $ = id => document.getElementById(id);
function show(id) { $(id).classList.remove('hidden'); }
function hide(id) { $(id).classList.add('hidden'); }

/* ── Weather ── */
function renderWeather(w) {
  const rainText = w.rain_prob > 0 ? `降雨機率 ${w.rain_prob}%` : '不易下雨';
  $('weather-card').innerHTML = `
    <div class="weather-main">
      <div class="weather-icon">${w.icon}</div>
      <div>
        <div class="weather-temp">${w.temp}°C</div>
        <div class="weather-desc">${w.description}</div>
      </div>
    </div>
    <div class="weather-details">
      <div class="weather-detail"><strong>${w.temp_max}°C</strong>最高</div>
      <div class="weather-detail"><strong>${w.temp_min}°C</strong>最低</div>
      <div class="weather-detail"><strong>${w.humidity}%</strong>濕度</div>
      <div class="weather-detail"><strong>${rainText}</strong></div>
    </div>
    <div class="weather-mood">
      <div class="weather-mood-label">今天適合</div>
      <div class="weather-mood-val">${w.mood}</div>
      <div class="weather-styles">
        ${(w.cooking_styles || []).slice(0, 4).map(s => `<span class="style-tag">${s}</span>`).join('')}
      </div>
    </div>
  `;
}

/* ── Vegetables ── */
function renderVegetables(vegs) {
  $('veg-grid').innerHTML = vegs.map((v, i) => `
    <div class="veg-card ${i < 3 ? 'highlight' : ''}">
      <div class="veg-name">${v.name}</div>
      <div class="veg-price">${v.price}</div>
      <div class="veg-unit">${v.unit}</div>
      <div class="veg-level">${v.level}</div>
      <div class="veg-cat">${v.category}</div>
    </div>
  `).join('');
}

/* ── Recipe cards ── */
const COMP_COLORS = {
  '菜': { border: '#4caf50', bg: '#f0fff4', label: '#388e3c' },
  '肉': { border: '#e8714a', bg: '#fff8f5', label: '#c0392b' },
  '湯': { border: '#2196f3', bg: '#f0f8ff', label: '#1565c0' },
  '蛋': { border: '#ff9800', bg: '#fffdf0', label: '#e65100' },
};

function recipeCard(recipe) {
  return `
    <a class="recipe-link" href="${recipe.url}" target="_blank" rel="noopener">
      <span class="recipe-link-title">${recipe.title}</span>
      <span class="recipe-link-arrow">→</span>
    </a>
  `;
}

function componentBlock(comp) {
  const c = COMP_COLORS[comp.type] || COMP_COLORS['菜'];
  const priceTag = comp.badge_info && comp.badge_info.price
    ? `<span class="comp-price">${comp.badge_info.price} ${comp.badge_info.unit}</span>`
    : '';
  const recipes = comp.recipes || [];
  return `
    <div class="comp-block" style="border-top: 3px solid ${c.border}">
      <div class="comp-header">
        <span class="comp-icon">${comp.icon}</span>
        <span class="comp-label" style="color:${c.label}">${comp.label}</span>
        <span class="comp-ingredient">${comp.ingredient}</span>
        ${priceTag}
      </div>
      <div class="comp-recipes">
        ${recipes.length
          ? recipes.map(r => recipeCard(r)).join('')
          : `<a class="recipe-link fallback" href="https://icook.tw/search/recipe?q=${encodeURIComponent(comp.ingredient)}" target="_blank" rel="noopener">
               <span class="recipe-link-title">搜尋「${comp.ingredient}」食譜</span>
               <span class="recipe-link-arrow">→</span>
             </a>`
        }
      </div>
    </div>
  `;
}

/* ── Menu ── */
function renderMenu(menu) {
  $('menu-grid').innerHTML = menu.map(meal => {
    const isFullMeal = meal.components.length > 1;
    return `
      <div class="meal-block ${isFullMeal ? 'full-meal' : ''}">
        <div class="meal-header">
          <span class="meal-icon-big">${meal.meal_icon}</span>
          <span class="meal-type-label">${meal.meal_type}</span>
          ${isFullMeal ? '<span class="full-meal-badge">肉 ＋ 湯 ＋ 菜 ＋ 蛋</span>' : ''}
        </div>
        <div class="components-grid">
          ${meal.components.map(comp => componentBlock(comp)).join('')}
        </div>
      </div>
    `;
  }).join('');
}

/* ── Load ── */
async function loadMenu() {
  const city = $('city-select').value;
  const btn  = $('refresh-btn');
  btn.disabled = true;
  $('btn-icon').textContent = '⏳';
  hide('main-content');
  hide('error-msg');
  show('loading');

  try {
    const res  = await fetch(`/api/menu?city=${encodeURIComponent(city)}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderWeather(data.weather);
    renderVegetables(data.cheap_vegetables);
    renderMenu(data.menu);
    hide('loading');
    show('main-content');
  } catch (err) {
    hide('loading');
    $('error-msg').textContent = `載入失敗：${err.message}`;
    show('error-msg');
  } finally {
    btn.disabled = false;
    $('btn-icon').textContent = '🔄';
  }
}

$('city-select').addEventListener('change', loadMenu);
loadMenu();
