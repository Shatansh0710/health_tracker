const statusElement = document.querySelector('#api-status');

async function checkApi() {
  try {
    const response = await fetch('/api/health');
    if (!response.ok) {
      throw new Error('API request failed');
    }

    const data = await response.json();
    statusElement.textContent = `${data.service} is ready.`;
  } catch (error) {
    statusElement.classList.add('error');
    statusElement.textContent = 'The API is unavailable.';
  }
}

checkApi();
