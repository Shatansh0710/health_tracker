const statusElement = document.querySelector('#api-status');
const form = document.querySelector('#meal-form');
const formMessage = document.querySelector('#form-message');
const warningModal = document.querySelector('#warning-modal');
const customNutritionFields = ['calories', 'protein', 'carbs', 'fat'];

async function request(path, options = {}) {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...options });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed');
  return data;
}

function setText(id, value) {
  document.querySelector(`#${id}`).textContent = value;
}

function renderProgress(id, value, isOverBudget = false) {
  const element = document.querySelector(`#${id}`);
  element.style.width = `${Math.min(value, 100)}%`;
  element.classList.toggle('over-budget', isOverBudget);
}

function renderState(state) {
  setText('calories-total', state.totals.calories);
  setText('calories-target', state.targets.calories);
  setText('budget-note', state.isOverBudget ? 'Over your calorie budget' : `${Math.max(state.targets.calories - state.totals.calories, 0)} kcal remaining today`);
  renderProgress('calories-progress', state.progress.calories, state.isOverBudget);

  ['protein', 'carbs', 'fat'].forEach((nutrient) => {
    setText(`${nutrient}-total`, state.totals[nutrient]);
    setText(`${nutrient}-target`, state.targets[nutrient]);
    renderProgress(`${nutrient}-progress`, state.progress[nutrient]);
  });

  document.querySelectorAll('.goal-button').forEach((button) => button.classList.toggle('active', button.dataset.goal === state.goal.id));
  setText('meal-count', `${state.meals.length} meal${state.meals.length === 1 ? '' : 's'}`);
  document.querySelector('#history-list').innerHTML = state.meals.length ? state.meals.map((meal) => `
    <article class="history-item"><div class="meal-symbol">${meal.food.slice(0, 1)}</div><div class="meal-info"><strong>${meal.food}</strong><span>${meal.grams}g</span></div><div class="meal-macros"><strong>${meal.calories} kcal</strong><span>${meal.protein}g protein · ${meal.carbs}g carbs · ${meal.fat}g fat</span></div><button class="delete-button" data-meal-id="${meal.id}" type="button" aria-label="Delete ${meal.food}">×</button></article>
  `).join('') : '<p class="empty-state">No meals logged yet.</p>';
  document.querySelectorAll('.delete-button').forEach((button) => button.addEventListener('click', () => deleteMeal(button.dataset.mealId)));
  if (state.isOverBudget && !warningModal.open) warningModal.showModal();
}

async function refreshState() {
  const state = await request('/api/state');
  renderState(state);
}

async function deleteMeal(mealId) {
  try {
    await request(`/api/log-meal/${mealId}`, { method: 'DELETE' });
    await refreshState();
  } catch (error) { formMessage.textContent = error.message; }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  formMessage.textContent = '';
  try {
    const nutrition = Object.fromEntries(customNutritionFields.map((nutrient) => [nutrient, document.querySelector(`#custom-${nutrient}`).value]));
    const hasCustomNutrition = Object.values(nutrition).some((value) => value !== '');
    await request('/api/log-meal', { method: 'POST', body: JSON.stringify({ food: document.querySelector('#food-input').value, grams: document.querySelector('#grams-input').value, nutrition: hasCustomNutrition ? nutrition : undefined }) });
    form.reset();
    await refreshState();
  } catch (error) { formMessage.textContent = error.message; }
});

document.querySelectorAll('.goal-button').forEach((button) => button.addEventListener('click', async () => {
  try { const state = await request('/api/fitness-goal', { method: 'PUT', body: JSON.stringify({ goal: button.dataset.goal }) }); renderState(state); }
  catch (error) { formMessage.textContent = error.message; }
}));

document.querySelector('#scan-button').addEventListener('click', async () => {
  try { const scan = await request('/api/mock-scan'); document.querySelector('#food-input').value = scan.food; document.querySelector('#grams-input').value = scan.grams; formMessage.textContent = 'Mock scan ready to review.'; }
  catch (error) { formMessage.textContent = error.message; }
});

document.querySelector('#close-modal').addEventListener('click', () => warningModal.close());

refreshState().then(() => { statusElement.textContent = 'API connected'; }).catch(() => { statusElement.textContent = 'API unavailable'; statusElement.classList.add('error'); });
