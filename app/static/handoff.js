const mp = {
  _data(platform) {
    const el = document.querySelector(`script[data-handoff="${platform}"]`);
    return JSON.parse(el.textContent);
  },
  async openTab(platform) {
    const d = this._data(platform);
    window.open(d.url, "_blank");
  },
  async copyText(platform) {
    const d = this._data(platform);
    await navigator.clipboard.writeText(d.text);
  },
  async copyImage(platform) {
    const d = this._data(platform);
    if (!d.has_image) return;
    const blob = await (await fetch("data:image/png;base64," + d.image_b64)).blob();
    await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
  },
};
window.mp = mp;