// LINENGUARD - Dashboard Chart.js Visualizations

function initDashboardCharts(data) {
  // Chart 1: Status Distribution
  const statusCtx = document.getElementById('statusChart');
  if (statusCtx && data.statusData) {
    const labels = data.statusData.map(d => d.status.replace(/_/g, ' '));
    const counts = data.statusData.map(d => d.count);

    new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: [
            '#0d6efd', '#198754', '#ffc107', '#dc3545',
            '#0dcaf0', '#6f42c1', '#fd7e14', '#20c997'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });
  }

  // Chart 2: Train-wise Unaccounted Linen
  const trainCtx = document.getElementById('trainChart');
  if (trainCtx && data.trainsData) {
    const trainLabels = data.trainsData.map(t => 'Train ' + t.train.train_number);
    const trainUnaccounted = data.trainsData.map(t => t.unaccounted);
    const trainReturned = data.trainsData.map(t => t.returned);

    new Chart(trainCtx, {
      type: 'bar',
      data: {
        labels: trainLabels,
        datasets: [
          {
            label: 'Returned',
            data: trainReturned,
            backgroundColor: '#198754',
            borderRadius: 6
          },
          {
            label: 'Unaccounted',
            data: trainUnaccounted,
            backgroundColor: '#dc3545',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { stacked: true },
          y: { stacked: true, beginAtZero: true }
        },
        plugins: {
          legend: { position: 'top' }
        }
      }
    });
  }

  // Chart 3: Coach Discrepancies Hotspots
  const coachCtx = document.getElementById('coachChart');
  if (coachCtx && data.coachHotspots) {
    const topCoaches = data.coachHotspots.slice(0, 6);
    const coachLabels = topCoaches.map(c => `${c.train.train_number} / ${c.coach.coach_number}`);
    const coachDiscrepancies = topCoaches.map(c => c.unaccounted);

    new Chart(coachCtx, {
      type: 'bar',
      data: {
        labels: coachLabels,
        datasets: [{
          label: 'Unaccounted Count',
          data: coachDiscrepancies,
          backgroundColor: coachDiscrepancies.map(val => val > 3 ? '#dc3545' : (val > 0 ? '#ffc107' : '#198754')),
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { beginAtZero: true, ticks: { stepSize: 1 } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // Chart 4: Linen Type Breakdown
  const typeCtx = document.getElementById('typeChart');
  if (typeCtx && data.typeLoss) {
    const typeLabels = data.typeLoss.map(t => t.type);
    const typeLosses = data.typeLoss.map(t => t.unaccounted);

    new Chart(typeCtx, {
      type: 'bar',
      data: {
        labels: typeLabels,
        datasets: [{
          label: 'Unaccounted Items',
          data: typeLosses,
          backgroundColor: '#fd7e14',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, ticks: { stepSize: 1 } }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}
