const question = document.querySelector('#question');
const toolArgs = document.querySelector('#toolArgs');
const response = document.querySelector('#response');
const status = document.querySelector('#status');
const route = document.querySelector('#route');

const examples = {
  policy: ['What is model risk?', ''],
  var: ['compute VaR', '{"returns":[-0.1,0.02,0.01],"confidence":0.95,"horizon_days":1}'],
  greeks: ['compute Greeks', '{"S":100,"K":100,"T":1,"r":0.05,"sigma":0.2,"option_type":"call"}'],
  pii: ['Can you assess risk for ABCDE1234F?', '']
};

document.querySelectorAll('[data-example]').forEach(button => {
  button.addEventListener('click', () => {
    [question.value, toolArgs.value] = examples[button.dataset.example];
    question.focus();
  });
});

document.querySelector('#send').addEventListener('click', async () => {
  if (!question.value.trim()) { status.textContent = 'Enter a question.'; return; }
  let args = null;
  if (toolArgs.value.trim()) {
    try { args = JSON.parse(toolArgs.value); }
    catch { status.textContent = 'Tool arguments must be valid JSON.'; return; }
  }
  status.textContent = 'Running…'; route.textContent = '';
  try {
    const result = await fetch('/ask', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question: question.value, tool_args: args}) });
    const data = await result.json();
    response.textContent = JSON.stringify(data, null, 2);
    route.textContent = data.route || '';
    status.textContent = result.ok ? 'Complete' : 'Request failed';
  } catch (error) {
    response.textContent = error.message;
    status.textContent = 'Could not connect';
  }
});
