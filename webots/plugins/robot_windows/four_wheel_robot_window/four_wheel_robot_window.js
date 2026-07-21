import RobotWindow from 'https://cyberbotics.com/wwi/R2025a/RobotWindow.js';

const format = value => Number.isFinite(Number(value)) ? Number(value).toFixed(3) : '—';

function setText(id, value) {
  const element = document.getElementById(id);
  if (element)
    element.textContent = format(value);
}

function renderVector(id, values) {
  const element = document.getElementById(id);
  if (!element)
    return;
  const labels = ['X', 'Y', 'Z'];
  element.innerHTML = values.map((value, index) =>
    `<span>${labels[index]} <strong>${format(value)}</strong></span>`
  ).join('');
}

function render(data) {
  Object.entries(data.distance).forEach(([name, value]) => setText(name, value));
  data.motors.forEach((value, index) => setText(`motor-${index}`, value));
  renderVector('accelerometer', data.accelerometer);
  renderVector('gyro', data.gyro);
  renderVector('gps', data.gps);
  renderVector('compass', data.compass);
  setText('simulation-time', data.time);

  document.getElementById('connection-dot').classList.add('online');
  document.getElementById('connection-text').textContent = 'Recebendo telemetria';

  const button = document.getElementById('motor-toggle');
  button.dataset.stopped = data.stopped ? 'true' : 'false';
  button.textContent = data.stopped ? 'Liberar motores' : 'Parar motores';
  button.classList.toggle('stopped', data.stopped);
}

window.onload = () => {
  window.robotWindow = new RobotWindow();
  window.robotWindow.setTitle('Four Wheel Robot · Telemetria');
  window.robotWindow.receive = message => {
    try {
      const data = JSON.parse(message);
      if (data.type === 'telemetry')
        render(data);
    } catch (error) {
      console.error('Mensagem de telemetria inválida:', message, error);
    }
  };

  document.getElementById('motor-toggle').addEventListener('click', event => {
    const stopped = event.currentTarget.dataset.stopped === 'true';
    window.robotWindow.send(stopped ? 'release motors' : 'stop motors');
  });
};
