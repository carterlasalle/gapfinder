let currentData = [];
let sortOrder = {column: 6, ascending: false};
let lastRefreshTime = new Date();
let gapMode = 'min_sell';
let favorites = [];
let lastChangeTimes = {
  '204': null, // Hunter
  '200': null, // Shadow
  '202': null  // Anchor
};
let previousData = {
  '204': null,
  '200': null,
  '202': null
};
let isNewUI = true;

function setGapMode(mode) {
  gapMode = mode;
  refreshData();
}

function showLoading() {
  document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
  document.getElementById('loading').style.display = 'none';
}

function calculateProfit(buyPrice, sellPrice, taxRate) {
  const revenue = sellPrice * (1 - taxRate / 100);
  return Math.floor(revenue - buyPrice);
}

async function toggleFavorite(playerName, section) {
  try {
    const response = await fetch('/favorites', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ player_name: playerName, section: section }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to toggle favorite');
    }
    console.log('Favorite toggled successfully:', data);
    await refreshFavorites();
    updateFavoriteUI(playerName, section, data.action === 'added');
  } catch (error) {
    console.error('Error toggling favorite:', error);
    alert(`Failed to toggle favorite: ${error.message}`);
  }
}

function updateFavoriteUI(playerName, section, isFavorite) {
  const rows = document.querySelectorAll('#data_table tr');
  rows.forEach(row => {
    const nameCell = row.cells[0];
    if (nameCell && nameCell.textContent === playerName) {
      const favoriteSpan = row.querySelector('.favorite');
      if (favoriteSpan) {
        favoriteSpan.textContent = isFavorite ? '★' : '☆';
        favoriteSpan.style.color = isFavorite ? 'gold' : 'inherit';
      }
    }
  });
}

async function deleteFavorite(favoriteId) {
  try {
    const response = await fetch(`/favorites?id=${favoriteId}`, {
      method: 'DELETE',
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to delete favorite');
    }
    console.log('Favorite deleted successfully');
    await refreshFavorites();
  } catch (error) {
    console.error('Error deleting favorite:', error);
    alert(`Failed to delete favorite: ${error.message}`);
  }
}

async function refreshFavorites() {
  try {
    const response = await fetch('/favorites');
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch favorites');
    }
    favorites = data;
    updateFavoritesList();
  } catch (error) {
    console.error('Error fetching favorites:', error);
    alert(`Failed to fetch favorites: ${error.message}`);
  }
}

function updateFavoritesList() {
  const favoritesDiv = document.getElementById('favorites');
  favoritesDiv.innerHTML = '<h3>Favorites:</h3>';
  favorites.forEach(favorite => {
    const favoriteItem = document.createElement('span');
    favoriteItem.className = 'favorite-item';
    favoriteItem.innerHTML = `
      <span onclick="selectFavorite('${favorite.player_name}', '${favorite.section}')">${favorite.player_name} (${favorite.section})</span>
      <span class="delete-favorite" onclick="deleteFavorite(${favorite.id})">🗑️</span>
    `;
    favoritesDiv.appendChild(favoriteItem);
  });
}

function selectFavorite(playerName, section) {
  document.getElementById('url_select').value = getSectionValue(section);
  document.getElementById('search').value = playerName;
  refreshData();
}

function getSectionValue(section) {
  switch (section.toLowerCase()) {
    case 'hunter': return '204';
    case 'shadow': return '200';
    case 'anchor': return '202';
    default: return '204';
  }
}

function populateTable(data) {
  currentData = data;
  const table = document.getElementById('data_table');
  table.innerHTML = `<tr>
    <th onclick="sortTable(1)">Player${getSortArrow(1)}</th>
    <th onclick="sortTable(2)">Max Buy${getSortArrow(2)}</th>
    <th onclick="sortTable(3)">Min Sell${getSortArrow(3)}</th>
    <th onclick="sortTable(4)">Current Price${getSortArrow(4)}</th>
    <th onclick="sortTable(5)">Avg Price${getSortArrow(5)}</th>
    <th onclick="sortTable(6)">Gap${getSortArrow(6)}</th>
    <th>Potential Profit</th>
    <th>Favorite</th>
  </tr>`;
  applySearch();
}

function getSortArrow(columnIndex) {
  if (sortOrder.column === columnIndex) {
    return sortOrder.ascending ? ' ↑' : ' ↓';
  }
  return '';
}

function applySearch() {
  const table = document.getElementById('data_table');
  const searchValue = document.getElementById('search').value.toLowerCase();
  const maxBuyFilter = document.getElementById('max_buy_filter').checked;
  const currentPriceMin = parseFloat(document.getElementById('current_price_min').value) || -Infinity;
  const currentPriceMax = parseFloat(document.getElementById('current_price_max').value) || Infinity;
  const avgPriceMin = parseFloat(document.getElementById('avg_price_min').value) || -Infinity;
  const avgPriceMax = parseFloat(document.getElementById('avg_price_max').value) || Infinity;
  const taxRate = parseFloat(document.getElementById('tax_rate').value) || 5;
  const article_number = document.getElementById('url_select').value;

  let filteredData = currentData.filter(row => {
    const currentPrice = row[3];
    const avgPrice = row[4];
    return (
      row.some(cell => cell.toString().toLowerCase().includes(searchValue)) &&
      (!maxBuyFilter || row[1] > row[3]) &&
      currentPrice >= currentPriceMin && currentPrice <= currentPriceMax &&
      (avgPrice === null || (avgPrice >= avgPriceMin && avgPrice <= avgPriceMax))
    );
  });

  table.innerHTML = table.querySelector('tr').outerHTML;
  filteredData.forEach(row => {
    const tr = document.createElement('tr');
    row.forEach(cell => {
      const td = document.createElement('td');
      td.textContent = cell ?? 'N/A';
      tr.appendChild(td);
    });
    
    // Add potential profit column
    const profitTd = document.createElement('td');
    const profit = calculateProfit(row[3], row[2], taxRate);
    profitTd.textContent = profit;
    tr.appendChild(profitTd);

    // Update favorite column
    const favoriteTd = document.createElement('td');
    const favoriteSpan = document.createElement('span');
    const isFavorite = favorites.some(fav => fav.player_name === row[0] && fav.section === getSectionName(article_number));
    favoriteSpan.textContent = isFavorite ? '★' : '☆';
    favoriteSpan.className = 'favorite';
    favoriteSpan.style.color = isFavorite ? 'gold' : 'inherit';
    favoriteSpan.onclick = () => toggleFavorite(row[0], getSectionName(article_number));
    favoriteTd.appendChild(favoriteSpan);
    tr.appendChild(favoriteTd);

    table.appendChild(tr);
  });
}

function getSectionName(articleNumber) {
  switch (articleNumber) {
    case '204': return 'Hunter';
    case '200': return 'Shadow';
    case '202': return 'Anchor';
    default: return 'Unknown';
  }
}

function sortTable(columnIndex) {
  if (sortOrder.column === columnIndex) {
    sortOrder.ascending = !sortOrder.ascending;
  } else {
    sortOrder = {column: columnIndex, ascending: true};
  }
  
  currentData.sort((a, b) => {
    const valA = a[columnIndex - 1];
    const valB = b[columnIndex - 1];
    let comparison = 0;
    if (valA === null && valB === null) {
      comparison = 0;
    } else if (valA === null) {
      comparison = 1;
    } else if (valB === null) {
      comparison = -1;
    } else if (valA > valB) {
      comparison = 1;
    } else if (valA < valB) {
      comparison = -1;
    }
    return sortOrder.ascending ? comparison : -comparison;
  });
  
  populateTable(currentData);
}

function updateLastChangeTime(articleNumber, newData) {
  if (JSON.stringify(newData) !== JSON.stringify(previousData[articleNumber])) {
    lastChangeTimes[articleNumber] = new Date();
    previousData[articleNumber] = newData;
  }
  updateLastChangeTimesDisplay();
}

function updateLastChangeTimesDisplay() {
  const lastChangeTimesDiv = document.getElementById('last_change_times');
  const now = new Date();
  let html = '<strong>Time since last data change:</strong><br>';
  for (const [articleNumber, lastChangeTime] of Object.entries(lastChangeTimes)) {
    const chemStyle = articleNumber === '204' ? 'Hunter' : articleNumber === '200' ? 'Shadow' : 'Anchor';
    if (lastChangeTime) {
      const diffInSeconds = Math.floor((now - lastChangeTime) / 1000);
      html += `${chemStyle}: ${diffInSeconds} seconds ago<br>`;
    } else {
      html += `${chemStyle}: No changes recorded yet<br>`;
    }
  }
  lastChangeTimesDiv.innerHTML = html;
}

function fetchWithAuth(url, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.append('Authorization', `Bearer ${localStorage.getItem('access_token')}`);
  return fetch(url, { ...options, headers });
}

function refreshData() {
  showLoading();
  const article_number = document.getElementById('url_select').value;
  const show_all = document.getElementById('show_all').checked;
  const use_avg = document.getElementById('use_avg').checked;
  const formData = new URLSearchParams();
  formData.append('article_number', article_number);
  formData.append('show_all', show_all);
  formData.append('gap_mode', gapMode);
  formData.append('use_avg', use_avg);
  fetchWithAuth('/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(`Error: ${data.error}`);
    } else {
      updateLastChangeTime(article_number, data.data);
      populateTable(data.data);
      lastRefreshTime = new Date();
    }
    hideLoading();
  })
  .catch(error => {
    console.error('Error:', error);
    alert(`An error occurred: ${error}`);
    hideLoading();
  });
}

// Modify the toggleUI function
function toggleUI() {
  isNewUI = !isNewUI;
  document.body.classList.toggle('old-ui', !isNewUI);
  localStorage.setItem('isNewUI', isNewUI.toString());
  console.log('UI toggled. isNewUI:', isNewUI); // Debug log
  applyUIStyles();
}

// Modify the applyUIStyles function
function applyUIStyles() {
  console.log('Applying UI styles. isNewUI:', isNewUI); // Debug log
  const elements = document.querySelectorAll('.controls, .filters, .search, .info, table, th, tr:nth-child(even)');
  elements.forEach(el => {
    el.style.transition = 'all 0.3s';
  });
  // Force a repaint to ensure styles are applied
  document.body.style.display = 'none';
  document.body.offsetHeight; // Trigger a reflow
  document.body.style.display = '';
}

window.onload = () => {
  fetchWithAuth('/favorites')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    favorites = data;
    updateFavoritesList();
    refreshData(); // Move refreshData() here to ensure favorites are loaded before populating the table
  })
  .catch(error => {
    console.error('Error fetching favorites:', error);
    alert('Failed to fetch favorites. Please try logging in again.');
  });

  setInterval(refreshData, 5 * 60 * 1000);
  setInterval(() => {
    const now = new Date();
    const diffInSeconds = Math.floor((now - lastRefreshTime) / 1000);
    document.getElementById('time_since_last_refresh').textContent = `Last refreshed: ${diffInSeconds} seconds ago`;
    updateLastChangeTimesDisplay();
  }, 1000);

  // Add UI toggle functionality
  const uiSwitch = document.getElementById('ui-switch');
  if (!uiSwitch) {
    console.error('UI switch element not found!');
    return;
  }
  
  isNewUI = localStorage.getItem('isNewUI') !== 'false';
  uiSwitch.checked = isNewUI;
  document.body.classList.toggle('old-ui', !isNewUI);
  
  uiSwitch.addEventListener('change', () => {
    toggleUI();
    console.log('Switch changed. isNewUI:', isNewUI); // Debug log
  });
  
  applyUIStyles();

  console.log('Initial UI state. isNewUI:', isNewUI); // Debug log

};
