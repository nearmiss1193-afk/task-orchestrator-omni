
const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, 'data', 'plans.json');
try {
    const data = fs.readFileSync(file, 'utf8');
    const plans = JSON.parse(data);
    const lastPlan = plans[plans.length - 1];
    console.log("Last Plan ID:", lastPlan.id);
    console.log("Status:", lastPlan.status);
    console.log("Steps Status:", lastPlan.steps.map(s => `${s.connectorName}:${s.status}`).join(', '));
} catch (e) {
    console.error(e);
}
