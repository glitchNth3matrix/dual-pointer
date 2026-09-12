// ==UserScript==
// @name         YouTube Hover Lock
// @namespace    https://github.com/dualpointer/youtube-hover-lock
// @version      1.0.0
// @description  Keeps YouTube thumbnail video previews actively playing when moving mouse away or switching monitors.
// @author       DualPointer
// @match        *://*.youtube.com/*
// @grant        none
// @run-at       document-idle
// ==/UserScript==

(function () {
  'use strict';

  // Inject Styles
  const style = document.createElement('style');
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
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(56, 189, 248, 0.6);
      border-radius: 6px;
      backdrop-filter: blur(8px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
      pointer-events: auto;
      cursor: pointer;
      transition: all 0.2s ease;
      user-select: none;
    }
    .yt-hover-lock-badge:hover {
      background: rgba(220, 38, 38, 0.9);
      border-color: rgba(252, 165, 165, 0.8);
    }
    .yt-hover-lock-icon {
      display: inline-block;
      width: 8px;
      height: 8px;
      background-color: #38bdf8;
      border-radius: 50%;
      box-shadow: 0 0 8px #38bdf8;
      animation: yt-pulse 1.8s infinite;
    }
    @keyframes yt-pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.5; transform: scale(0.85); }
    }
    .yt-hover-locked-card {
      outline: 2px solid rgba(56, 189, 248, 0.7) !important;
      outline-offset: -2px;
    }
  `;
  document.head.appendChild(style);

  let hoveredCard = null;
  let lockedCard = null;
  let lockBadge = null;
  let videoResumeInterval = null;

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

  document.addEventListener('pointerover', (e) => {
    const card = findParentVideoCard(e.target);
    if (card) hoveredCard = card;
  }, true);

  document.addEventListener('mouseover', (e) => {
    const card = findParentVideoCard(e.target);
    if (card) hoveredCard = card;
  }, true);

  function handleLeaveEvent(e) {
    if (!lockedCard) return;
    if (
      lockedCard.contains(e.target) ||
      e.target === lockedCard ||
      e.target.closest('#video-preview') ||
      e.target.closest('ytd-video-preview')
    ) {
      e.stopImmediatePropagation();
      e.stopPropagation();
      e.preventDefault();
    }
  }

  window.addEventListener('mouseleave', handleLeaveEvent, true);
  window.addEventListener('mouseout', handleLeaveEvent, true);
  window.addEventListener('pointerleave', handleLeaveEvent, true);
  window.addEventListener('pointerout', handleLeaveEvent, true);

  function ensureVideoPlaying() {
    if (!lockedCard) return;
    const previewContainer =
      document.querySelector('#video-preview') ||
      document.querySelector('ytd-video-preview') ||
      lockedCard.querySelector('ytd-video-preview');

    if (previewContainer) {
      const video = previewContainer.querySelector('video');
      if (video && video.paused && !video.ended) {
        video.play().catch(() => {});
      }
    }
  }

  function lockPreview(card) {
    unlockPreview();
    if (!card) return;
    lockedCard = card;
    lockedCard.classList.add('yt-hover-locked-card');

    lockBadge = document.createElement('div');
    lockBadge.className = 'yt-hover-lock-badge';
    lockBadge.innerHTML = `
      <span class="yt-hover-lock-icon"></span>
      <span>Locked (Alt+P to unlock)</span>
    `;
    lockBadge.title = 'Click to release preview lock';
    lockBadge.addEventListener('click', (e) => {
      e.stopPropagation();
      unlockPreview();
    });

    const thumbnailContainer =
      lockedCard.querySelector('#thumbnail') ||
      lockedCard.querySelector('ytd-thumbnail') ||
      lockedCard;

    if (thumbnailContainer) {
      thumbnailContainer.style.position = 'relative';
      thumbnailContainer.appendChild(lockBadge);
    }

    if (videoResumeInterval) clearInterval(videoResumeInterval);
    videoResumeInterval = setInterval(ensureVideoPlaying, 500);
  }

  function unlockPreview() {
    if (videoResumeInterval) {
      clearInterval(videoResumeInterval);
      videoResumeInterval = null;
    }
    if (lockBadge) {
      lockBadge.remove();
      lockBadge = null;
    }
    if (lockedCard) {
      lockedCard.classList.remove('yt-hover-locked-card');
      lockedCard = null;
    }
  }

  function toggleLock() {
    if (lockedCard) {
      unlockPreview();
    } else {
      const target = hoveredCard || findParentVideoCard(document.querySelector(':hover'));
      if (target) lockPreview(target);
    }
  }

  window.addEventListener(
    'keydown',
    (e) => {
      if (e.altKey && !e.ctrlKey && !e.shiftKey && (e.code === 'KeyP' || e.key === 'p' || e.key === 'P')) {
        e.preventDefault();
        e.stopPropagation();
        toggleLock();
      } else if (e.key === 'Escape' && lockedCard) {
        unlockPreview();
      }
    },
    true
  );

  console.log('[YouTube Hover Lock] Userscript loaded. Press Alt+P over video to lock preview.');
})();
