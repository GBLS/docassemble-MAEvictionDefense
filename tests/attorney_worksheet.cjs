// Local DOM regression checks. Run with Node.js and Playwright available.
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  try {
    const page = await browser.newPage();
    const form = `
      <form>
        <style>#worksheet-tenant, #worksheet-menu { scroll-margin-top: 96px; }</style>
        <nav id="worksheet-menu" tabindex="-1">
          <a href="#worksheet-tenant">Tenant</a>
          <a href='javascript:daGoToAnchor("#worksheet-tenant");'><span>Rendered Tenant</span></a>
        </nav>
        <div style="height:1200px"></div>
        <h2 id="worksheet-tenant" tabindex="-1">Tenant</h2>
        <a href="javascript:daGoToAnchor('#worksheet-menu');"><span>Back to sections</span></a>
        <input id="unsaved-name">
        <div class="worksheet-saved-none-container">
          <input id="saved-choice" type="checkbox" class="danon-nota-checkbox">
          <input id="saved-none" type="checkbox" class="danota-checkbox">
        </div>
        <div class="worksheet-saved-none-container">
          <input id="edited-choice" type="checkbox" class="danon-nota-checkbox" checked>
          <input id="edited-none" type="checkbox" class="danota-checkbox">
        </div>
        <div>
          <input id="new-choice" type="checkbox" class="danon-nota-checkbox">
          <input id="new-none" type="checkbox" class="danota-checkbox">
        </div>
        <div style="height:1600px"></div>
      </form>`;
    await page.setContent(form);
    // Bridge the jQuery APIs used by this script to real DOM events. This
    // checks our handler; live docassemble validation remains a separate check.
    await page.evaluate(() => {
      window.changes = 0;
      window.submits = 0;
      window.defaultJumps = 0;
      window.daGoToAnchor = () => { window.defaultJumps += 1; };
      document.addEventListener('change', () => { window.changes += 1; });
      document.addEventListener('submit', event => { event.preventDefault(); window.submits += 1; });
      window.jQuery = element => ({
        on(name, listener) { element.addEventListener(name, listener); return this; },
        prop(name, value) { element[name] = value; return this; },
        trigger(name) { element.dispatchEvent(new Event(name, { bubbles: true })); return this; }
      });
    });
    await page.addScriptTag({ path: 'docassemble/MAEvictionDefense/data/static/attorney_worksheet.js' });
    await page.addScriptTag({ path: 'docassemble/MAEvictionDefense/data/static/attorney_worksheet.js' });
    await page.evaluate(() => document.dispatchEvent(new Event('daPageLoad')));
    assert.equal(await page.locator('#saved-none').isChecked(), true);
    assert.equal(await page.locator('#edited-choice').isChecked(), true);
    assert.equal(await page.locator('#edited-none').isChecked(), false);
    assert.equal(await page.locator('#new-none').isChecked(), false);
    assert.equal(await page.evaluate(() => window.changes), 1);
    await page.evaluate(() => document.dispatchEvent(new Event('daPageLoad')));
    assert.equal(await page.evaluate(() => window.changes), 1);
    console.log('PASS: restores saved None, preserves new/substantive answers, and sends one change event');

    await page.locator('#unsaved-name').fill('Unsaved fictional tenant');
    await page.getByRole('link', { name: 'Tenant', exact: true }).click();
    assert.equal(await page.evaluate(() => document.activeElement.id), 'worksheet-tenant');
    assert.equal(await page.locator('#unsaved-name').inputValue(), 'Unsaved fictional tenant');
    assert.equal(await page.evaluate(() => window.submits), 0);
    console.log('PASS: section jumps preserve unsaved input without submission');

    await page.getByRole('link', { name: 'Back to sections', exact: true }).click();
    assert.equal(await page.evaluate(() => document.activeElement.id), 'worksheet-menu');
    await page.getByRole('link', { name: 'Rendered Tenant', exact: true }).click();
    assert.equal(await page.evaluate(() => document.activeElement.id), 'worksheet-tenant');
    const headingTop = await page.locator('#worksheet-tenant').evaluate(el => el.getBoundingClientRect().top);
    assert.ok(headingTop >= 90 && headingTop <= 102, `heading must scroll below header, got ${headingTop}`);
    assert.equal(await page.locator('#unsaved-name').inputValue(), 'Unsaved fictional tenant');
    assert.equal(await page.evaluate(() => window.submits), 0);
    assert.equal(await page.evaluate(() => window.defaultJumps), 0);
    console.log('PASS: docassemble-rendered links scroll and focus both directions without running their default handler');

    // Docassemble replaces its form between screens while retaining listeners.
    await page.evaluate(html => { document.body.innerHTML = html; }, form);
    await page.evaluate(() => document.dispatchEvent(new Event('daPageLoad')));
    assert.equal(await page.locator('#saved-none').isChecked(), true);
    await page.evaluate(() => { document.getElementById('worksheet-menu').remove(); });
    await page.locator('#saved-none').uncheck();
    await page.evaluate(() => document.dispatchEvent(new Event('daPageLoad')));
    assert.equal(await page.locator('#saved-none').isChecked(), false);
    console.log('PASS: survives form replacement and leaves other interview screens alone');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
