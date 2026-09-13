/**
 * YouTube Hover Lock - Popup Settings Controller
 */

const DEFAULT_SETTINGS = {
  masterEnabled: true,
  autoLockOnHover: true,
  hoverDelay: 700,
  autoLoop: true,
  autoUnmute: false,
  showBadge: true
};

const dom = {
  statusPill: document.getElementById('status-pill'),
  statusText: document.getElementById('status-text'),
  toggleMaster: document.getElementById('toggle-master'),
  toggleAutoLock: document.getElementById('toggle-autolock'),
  sliderDelay: document.getElementById('slider-delay'),
  delayValue: document.getElementById('delay-value'),
  delayContainer: document.getElementById('delay-container'),
  toggleAutoLoop: document.getElementById('toggle-autoloop'),
  toggleAutoUnmute: document.getElementById('toggle-autounmute'),
  toggleShowBadge: document.getElementById('toggle-showbadge')
};

function formatDelay(ms) {
  if (ms >= 1000) {
    return (ms / 1000).toFixed(1) + 's';
  }
  return ms + 'ms';
}

function getSettingsFromUI() {
  return {
    masterEnabled: dom.toggleMaster.checked,
    autoLockOnHover: dom.toggleAutoLock.checked,
    hoverDelay: parseInt(dom.sliderDelay.value, 10) || 700,
    autoLoop: dom.toggleAutoLoop.checked,
    autoUnmute: dom.toggleAutoUnmute.checked,
    showBadge: dom.toggleShowBadge.checked
  };
}

function applySettingsToUI(settings) {
  const s = { ...DEFAULT_SETTINGS, ...settings };
  dom.toggleMaster.checked = s.masterEnabled;
  dom.toggleAutoLock.checked = s.autoLockOnHover;
  dom.sliderDelay.value = s.hoverDelay;
  dom.delayValue.textContent = formatDelay(s.hoverDelay);
  dom.toggleAutoLoop.checked = s.autoLoop;
  dom.toggleAutoUnmute.checked = s.autoUnmute;
  dom.toggleShowBadge.checked = s.showBadge;

  // Dim slider if auto-lock is off
  dom.delayContainer.style.opacity = s.autoLockOnHover ? '1' : '0.4';
  dom.sliderDelay.disabled = !s.autoLockOnHover;
}

function broadcastSettings(settings) {
  // Save to Chrome sync or local storage
  const storage = (chrome.storage && (chrome.storage.sync || chrome.storage.local));
  if (storage) {
    storage.set({ yt_hover_lock_settings: settings });
  }

  // Push to active tab's page context in world: "MAIN"
  if (chrome.tabs && chrome.scripting) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const activeTab = tabs && tabs[0];
      if (activeTab && activeTab.id && activeTab.url && activeTab.url.includes("youtube.com")) {
        chrome.scripting.executeScript({
          target: { tabId: activeTab.id },
          world: "MAIN",
          func: (cfg) => {
            window.postMessage({ type: "YT_HOVER_LOCK_UPDATE_CONFIG", config: cfg }, "*");
            try {
              localStorage.setItem("yt_hover_lock_config", JSON.stringify(cfg));
            } catch (_) {}
          },
          args: [settings]
        }).catch(() => {});
      }
    });
  }
}

function checkActiveTabStatus() {
  if (!chrome.tabs) return;
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const activeTab = tabs && tabs[0];
    const isYouTube = activeTab && activeTab.url && activeTab.url.includes("youtube.com");
    if (isYouTube) {
      dom.statusPill.className = 'status-pill active';
      dom.statusText.textContent = 'Active on YouTube';
    } else {
      dom.statusPill.className = 'status-pill inactive';
      dom.statusText.textContent = 'Standby';
    }
  });
}

function init() {
  checkActiveTabStatus();

  // Load saved settings
  const storage = (chrome.storage && (chrome.storage.sync || chrome.storage.local));
  if (storage) {
    storage.get('yt_hover_lock_settings', (data) => {
      if (data && data.yt_hover_lock_settings) {
        applySettingsToUI(data.yt_hover_lock_settings);
      } else {
        applySettingsToUI(DEFAULT_SETTINGS);
      }
    });
  } else {
    applySettingsToUI(DEFAULT_SETTINGS);
  }

  // Event Listeners
  const onChange = () => {
    const settings = getSettingsFromUI();
    dom.delayContainer.style.opacity = settings.autoLockOnHover ? '1' : '0.4';
    dom.sliderDelay.disabled = !settings.autoLockOnHover;
    broadcastSettings(settings);
  };

  dom.toggleMaster.addEventListener('change', onChange);
  dom.toggleAutoLock.addEventListener('change', onChange);
  dom.toggleAutoLoop.addEventListener('change', onChange);
  dom.toggleAutoUnmute.addEventListener('change', onChange);
  dom.toggleShowBadge.addEventListener('change', onChange);

  dom.sliderDelay.addEventListener('input', () => {
    const val = parseInt(dom.sliderDelay.value, 10);
    dom.delayValue.textContent = formatDelay(val);
  });

  dom.sliderDelay.addEventListener('change', onChange);
}

document.addEventListener('DOMContentLoaded', init);
