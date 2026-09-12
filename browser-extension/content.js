/**
 * YouTube Hover Lock - Content Script
 * Keeps inline thumbnail video previews actively playing when moving
 * mouse away, switching to another monitor, or working in another app.
 */

(function () {
  'use strict';

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

  // 1. Track currently hovered video card
  document.addEventListener(
    'pointerover',
    (e) => {
      const card = findParentVideoCard(e.target);
      if (card) {
        hoveredCard = card;
      }
    },
    true
  );

  document.addEventListener(
    'mouseover',
    (e) => {
      const card = findParentVideoCard(e.target);
      if (card) {
        hoveredCard = card;
      }
    },
    true
  );

  // 2. Intercept mouse/pointer leave events when a card is locked
  function handleLeaveEvent(e) {
    if (!lockedCard) return;

    // If the leave event is originating from or targeting the locked card or video preview
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

  // 3. Keep video playing if YouTube attempts to pause on blur / mouseleave
  function ensureVideoPlaying() {
    if (!lockedCard) return;

    // Check preview player inside document or within locked card
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

  // 4. Lock / Unlock management
  function lockPreview(card) {
    unlockPreview(); // Clear any previously locked card

    if (!card) return;
    lockedCard = card;
    lockedCard.classList.add('yt-hover-locked-card');

    // Create and attach visual lock badge
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

    // Keep active preview alive
    if (videoResumeInterval) clearInterval(videoResumeInterval);
    videoResumeInterval = setInterval(ensureVideoPlaying, 500);

    console.log('[YouTube Hover Lock] Preview locked successfully.');
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
      if (target) {
        lockPreview(target);
      }
    }
  }

  // 5. Global Hotkey: Alt + P
  window.addEventListener(
    'keydown',
    (e) => {
      // Check for Alt + P (code: KeyP)
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

  console.log('[YouTube Hover Lock] Ready. Hover over a video and press Alt+P to lock preview.');
})();
