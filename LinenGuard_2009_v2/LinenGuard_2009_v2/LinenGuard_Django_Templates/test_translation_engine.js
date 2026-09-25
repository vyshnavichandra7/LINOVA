// Test script to verify static/js/translations.js logic in Node.js
const fs = require('fs');
const path = require('path');

// Mock browser environment
const localStorageData = {};
global.localStorage = {
  getItem: (k) => localStorageData[k] || null,
  setItem: (k, v) => { localStorageData[k] = v; }
};
const vm = require('vm');

const sandbox = {
  localStorage: global.localStorage,
  document: global.document,
  window: {},
  console: console
};
sandbox.window = sandbox;

// Load and run translations.js code in sandbox
const code = fs.readFileSync(path.join(__dirname, 'static', 'js', 'translations.js'), 'utf8');
vm.runInNewContext(code, sandbox);

const LinenDict = sandbox.LinenDict;
const translateString = sandbox.translateString;
const setLanguage = sandbox.setLanguage;

console.log("Translations JS evaluated successfully.");
console.log("Total Hindi phrases in LinenDict.hi:", Object.keys(LinenDict.hi).length);
console.log("Total Telugu phrases in LinenDict.te:", Object.keys(LinenDict.te).length);

// Test translation of sample strings
const samplePhrases = [
  "Select Access Role",
  "Attendant",
  "Laundry",
  "Supervisor",
  "Employee ID / Badge",
  "Password",
  "Sign in",
  "Coach Assignment",
  "Confirm & start shift",
  "Issue Linen",
  "Collect Item",
  "Give linen to a boarding passenger",
  "Take linen back from a deboarding passenger",
  "Manufacturer Linen Intake",
  "Depot Intake Hub",
  "Scan Manufacturer Tag",
  "Item Category",
  "Bedsheet",
  "Blanket",
  "Towel",
  "Pillow Cover",
  "Zone Attendant Roster & Coach Allocation",
  "Assign & Hand Off",
  "Missing Linen & Settlement",
  "Audit Log",
  "Train 12723",
  "Coach B2",
  "Berth 25",
  "120 bedsheets"
];

console.log("\n--- Testing Translation to Hindi (hi) ---");
let hiSuccess = true;
for (const phrase of samplePhrases) {
  const tr = translateString(phrase, 'hi');
  if (tr === phrase && !phrase.startsWith("Train") && !phrase.startsWith("Coach")) {
    console.error(`FAIL: '${phrase}' did not translate to Hindi!`);
    hiSuccess = false;
  } else {
    console.log(`[HI] "${phrase}" -> "${tr}"`);
  }
}

console.log("\n--- Testing Translation to Telugu (te) ---");
let teSuccess = true;
for (const phrase of samplePhrases) {
  const tr = translateString(phrase, 'te');
  if (tr === phrase && !phrase.startsWith("Train") && !phrase.startsWith("Coach")) {
    console.error(`FAIL: '${phrase}' did not translate to Telugu!`);
    teSuccess = false;
  } else {
    console.log(`[TE] "${phrase}" -> "${tr}"`);
  }
}

console.log("\n--- Testing Translation Reversibility to English (en) ---");
setLanguage('hi');
if (sandbox.getCurrentLanguage() !== 'hi') throw new Error("currentLanguage failed to update to 'hi'");
setLanguage('te');
if (sandbox.getCurrentLanguage() !== 'te') throw new Error("currentLanguage failed to update to 'te'");
setLanguage('en');
if (sandbox.getCurrentLanguage() !== 'en') throw new Error("currentLanguage failed to update to 'en'");
console.log("[PASS] State toggle en <-> hi <-> te works smoothly.");

if (hiSuccess && teSuccess) {
  console.log("\n=== ALL TRANSLATION TESTS PASSED PERFECTLY ===");
} else {
  process.exit(1);
}
