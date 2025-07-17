const puppeteer = require("puppeteer");
require("dotenv").config();

(async () => {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  await page.goto("https://bunq.com/login", { waitUntil: "networkidle2" });

  await page.type('input[type="email"]', process.env.BUNQ_EMAIL);
  await page.click('button[type="submit"]');

  console.log("📱 Completa la verifica via email o app mobile.");
  console.log("🛠 Vai su App Mobile > Impostazioni > Developer > API Key.");

  await browser.close();
})();
