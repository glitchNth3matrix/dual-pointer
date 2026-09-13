// ==UserScript==
// @name         YouTube Hover Lock
// @namespace    https://github.com/dualpointer/youtube-hover-lock
// @version      1.3.0
// @description  Keeps YouTube thumbnail video previews actively playing when moving mouse away, switching monitors, or clicking elsewhere. Includes Auto-Loop and 1-click sound toggle.
// @author       DualPointer
// @match        *://*.youtube.com/*
// @grant        none
// @run-at       document-start
// ==/UserScript==

(function () {
  'use strict';

  window.__YT_HOVER_LOCK_LOCKED__ = false;

  let hoveredCard = null;
  let lockedCard = null;
  let lockedPreviewElement = null;
  let lockBadge = null;
  let autoLockTimer = null;
  let heartbeatTimer = null;
  let domObserver = null;

  function injectStyles() {
    if (document.getElementById('yt-hover-lock-css')) return;
    const style = document.createElement('style');
    style.id = 'yt-hover-lock-css';
    style.textContent = `
      .yt-hover-lock-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        z-index: 2200;
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        font-family: Roboto, Arial, sans-serif;
        font-size: 11px;
        font-weight: 500;
        color: #ffffff;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.7);
        border-radius: 6px;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        pointer-events: auto;
        cursor: pointer;
        transition: all 0.2s ease;
        user-select: none;
      }
      .yt-hover-lock-badge:hover {
        background: rgba(220, 38, 38, 0.9);
        border-color: rgba(252, 165, 165, 0.9);
      }
      .yt-hover-lock-icon {
        display: inline-block;
        width: 8px;
        height: 8px;
        background-color: #38bdf8;
        border-radius: 50%;
        box-shadow: 0 0 8px #38bdf8;
        animation: yt-pulse-glow 1.5s infinite;
      }
      @keyframes yt-pulse-glow {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.8); }
      }
      .yt-hover-locked-card {
        outline: 2px solid rgba(56, 189, 248, 0.8) !important;
        outline-offset: -2px;
      }
      .yt-hover-audio-btn {
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.35);
        border-radius: 4px;
        color: #fff;
        cursor: pointer;
        padding: 2px 6px;
        font-size: 11px;
        margin-left: 4px;
        line-height: 1;
        transition: all 0.2s ease;
      }
      .yt-hover-audio-btn:hover {
        background: rgba(56, 189, 248, 0.5);
        border-color: rgba(56, 189, 248, 0.9);
      }
      ytd-video-preview.yt-hover-locked-active,
      ytd-video-preview.yt-hover-locked-active #inline-preview-player,
      ytd-video-preview.yt-hover-locked-active #player-container {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
      }
    `;
    (document.head || document.documentElement).appendChild(style);
  }

  // Hook HTMLMediaElement.prototype.pause
  const originalPause = HTMLMediaElement.prototype.pause;
  HTMLMediaElement.prototype.pause = function () {
    if (window.__YT_HOVER_LOCK_LOCKED__) {
      const isPreview =
        this.closest('ytd-video-preview') ||
        this.closest('#video-preview') ||
        this.closest('#mouseover-overlay') ||
        (lockedCard && lockedCard.contains(this));

      if (isPreview) {
        return;
      }
    }
    return originalPause.apply(this, arguments);
  };

  function suppressIfLocked(e) {
    if (window.__YT_HOVER_LOCK_LOCKED__) {
      e.stopImmediatePropagation();
    }
  }

  window.addEventListener('blur', suppressIfLocked, true);
  window.addEventListener('focusout', (e) => {
    if (window.__YT_HOVER_LOCK_LOCKED__ && !e.relatedTarget) {
      suppressIfLocked(e);
    }
  }, true);
  document.addEventListener('visibilitychange', suppressIfLocked, true);

  function handleLeaveEvents(e) {
    if (!window.__YT_HOVER_LOCK_LOCKED__) return;
    e.stopImmediatePropagation();
    e.stopPropagation();
  }

  window.addEventListener('mouseleave', handleLeaveEvents, true);
  window.addEventListener('mouseout', handleLeaveEvents, true);
  window.addEventListener('pointerleave', handleLeaveEvents, true);
  window.addEventListener('pointerout', handleLeaveEvents, true);

  const CARD_SELECTORS = [
    'ytd-rich-item-renderer',
    'ytd-compact-video-renderer',
    'ytd-grid-video-renderer',
    'ytd-video-renderer',
    '#mouseover-overlay',
    'ytd-video-preview'
  ];

  function findParentVideoCard(target) {
    if (!target || !(target instanceof Element)) return null;
    return target.closest(CARD_SELECTORS.join(', '));
  }

  function onPointerEnter(e) {
    const card = findParentVideoCard(e.target);
    if (card && card !== hoveredCard) {
      hoveredCard = card;

      if (autoLockTimer) clearTimeout(autoLockTimer);
      autoLockTimer = setTimeout(() => {
        if (hoveredCard === card && lockedCard !== card) {
          lockPreview(card);
        }
      }, 700);
    }
  }

  document.addEventListener('pointerover', onPointerEnter, true);
  document.addEventListener('mouseover', onPointerEnter, true);

  function lockPreview(card) {
    if (!card) return;
    injectStyles();

    if (lockedCard && lockedCard !== card) {
      unlockPreview();
    }

    window.__YT_HOVER_LOCK_LOCKED__ = true;
    lockedCard = card;
    lockedCard.classList.add('yt-hover-locked-card');

    lockedPreviewElement =
      document.querySelector('#video-preview') ||
      document.querySelector('ytd-video-preview') ||
      lockedCard.querySelector('ytd-video-preview');

    if (lockedPreviewElement) {
      lockedPreviewElement.classList.add('yt-hover-locked-active');
    }

    if (!lockBadge) {
      lockBadge = document.createElement('div');
      lockBadge.className = 'yt-hover-lock-badge';
      lockBadge.innerHTML = `
        <span class="yt-hover-lock-icon"></span>
        <span id="yt-hover-lock-text">Locked</span>
        <button class="yt-hover-audio-btn" id="yt-hover-audio-toggle" title="Toggle audio (Mute/Unmute)">🔇</button>
      `;
      lockBadge.title = 'Preview is locked! Playing continuously across monitors. Click text to unlock, or button for sound.';
      lockBadge.addEventListener('click', (e) => {
        if (e.target.closest('#yt-hover-audio-toggle')) {
          e.stopPropagation();
          const preview =
            lockedPreviewElement ||
            document.querySelector('#video-preview') ||
            document.querySelector('ytd-video-preview');
          if (preview) {
            const video = preview.querySelector('video');
            if (video) {
              video.muted = !video.muted;
              video.volume = 1.0;
              const btn = lockBadge.querySelector('#yt-hover-audio-toggle');
              if (btn) btn.textContent = video.muted ? '🔇' : '🔊';
            }
          }
          return;
        }
        e.stopPropagation();
        unlockPreview();
      });
    }

    const thumbnailContainer =
      lockedCard.querySelector('#thumbnail') ||
      lockedCard.querySelector('ytd-thumbnail') ||
      lockedCard;

    if (thumbnailContainer) {
      thumbnailContainer.style.position = 'relative';
      thumbnailContainer.appendChild(lockBadge);
    }

    if (domObserver) domObserver.disconnect();
    domObserver = new MutationObserver(() => {
      if (!window.__YT_HOVER_LOCK_LOCKED__) return;

      const preview =
        document.querySelector('#video-preview') ||
        document.querySelector('ytd-video-preview');

      if (preview) {
        if (preview.hasAttribute('hidden')) {
          preview.removeAttribute('hidden');
        }
        if (preview.style.display === 'none') {
          preview.style.display = 'block';
        }
        const video = preview.querySelector('video');
        if (video) {
          if (video.ended || (video.duration > 0 && video.currentTime >= video.duration - 0.4)) {
            video.currentTime = 0;
            video.play().catch(() => {});
          } else if (video.paused) {
            video.play().catch(() => {});
          }
        }
      }
    });

    domObserver.observe(document.body, {
      attributes: true,
      subtree: true,
      attributeFilter: ['hidden', 'style', 'class']
    });

    if (heartbeatTimer) clearInterval(heartbeatTimer);
    heartbeatTimer = setInterval(() => {
      if (!window.__YT_HOVER_LOCK_LOCKED__) return;

      const preview =
        lockedPreviewElement ||
        document.querySelector('#video-preview') ||
        document.querySelector('ytd-video-preview');

      if (preview) {
        const video = preview.querySelector('video');
        if (video) {
          if (video.ended || (video.duration > 0 && video.currentTime >= video.duration - 0.4)) {
            video.currentTime = 0;
            video.play().catch(() => {});
          } else if (video.paused) {
            video.play().catch(() => {});
          }

          const btn = lockBadge && lockBadge.querySelector('#yt-hover-audio-toggle');
          if (btn) {
            btn.textContent = video.muted ? '🔇' : '🔊';
          }
        }
      }
    }, 250);
  }

  function unlockPreview() {
    window.__YT_HOVER_LOCK_LOCKED__ = false;

    if (autoLockTimer) {
      clearTimeout(autoLockTimer);
      autoLockTimer = null;
    }

    if (heartbeatTimer) {
      clearInterval(heartbeatTimer);
      heartbeatTimer = null;
    }

    if (domObserver) {
      domObserver.disconnect();
      domObserver = null;
    }

    if (lockBadge) {
      lockBadge.remove();
      lockBadge = null;
    }

    if (lockedPreviewElement) {
      lockedPreviewElement.classList.remove('yt-hover-locked-active');
      lockedPreviewElement = null;
    }

    if (lockedCard) {
      lockedCard.classList.remove('yt-hover-locked-card');
      lockedCard = null;
    }
  }

  function toggleLock() {
    if (window.__YT_HOVER_LOCK_LOCKED__) {
      unlockPreview();
    } else {
      const target = hoveredCard || findParentVideoCard(document.querySelector(':hover'));
      if (target) {
        lockPreview(target);
      }
    }
  }

  window.addEventListener(
    'keydown',
    (e) => {
      if (e.altKey && !e.ctrlKey && !e.shiftKey && (e.code === 'KeyP' || e.key === 'p' || e.key === 'P')) {
        e.preventDefault();
        e.stopPropagation();
        toggleLock();
      } else if (e.key === 'Escape' && window.__YT_HOVER_LOCK_LOCKED__) {
        unlockPreview();
      }
    },
    true
  );

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectStyles);
  } else {
    injectStyles();
  }
})();
