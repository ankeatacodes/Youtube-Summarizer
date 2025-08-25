// content.js - Content script for YouTube pages
(function() {
  'use strict';

  let videoData = null;

  // Initialize content script
  function init() {
    extractVideoData();
    observeVideoChanges();
    createSummarizerButton();
  }

  // Extract video data from YouTube page
  function extractVideoData() {
    const url = window.location.href;
    const videoId = extractVideoId(url);
    const title = document.querySelector('h1.ytd-video-primary-info-renderer') || 
                  document.querySelector('h1.title') ||
                  document.querySelector('[class*="title"]');

    videoData = {
      url: url,
      videoId: videoId,
      title: title ? title.textContent.trim() : 'Unknown Title',
      duration: getDuration(),
      channelName: getChannelName()
    };

    console.log('Video data extracted:', videoData);
  }

  function extractVideoId(url) {
    const match = url.match(/[?&]v=([^&]+)/);
    return match ? match[1] : null;
  }

  function getDuration() {
    const durationElement = document.querySelector('.ytp-time-duration');
    return durationElement ? durationElement.textContent : null;
  }

  function getChannelName() {
    const channelElement = document.querySelector('#channel-name a') ||
                          document.querySelector('.ytd-channel-name a') ||
                          document.querySelector('[class*="channel-name"]');
    return channelElement ? channelElement.textContent.trim() : 'Unknown Channel';
  }

  // Observe video changes for SPA navigation
  function observeVideoChanges() {
    let lastUrl = location.href;
    
    // Use MutationObserver to detect URL changes
    new MutationObserver(() => {
      const url = location.href;
      if (url !== lastUrl) {
        lastUrl = url;
        if (url.includes('/watch')) {
          setTimeout(() => {
            extractVideoData();
            createSummarizerButton();
          }, 1000);
        }
      }
    }).observe(document, { subtree: true, childList: true });
  }

  // Create floating summarizer button
  function createSummarizerButton() {
    // Remove existing button if any
    const existingButton = document.getElementById('yt-summarizer-btn');
    if (existingButton) {
      existingButton.remove();
    }

    // Only show on watch pages
    if (!window.location.href.includes('/watch')) {
      return;
    }

    const button = document.createElement('div');
    button.id = 'yt-summarizer-btn';
    button.innerHTML = `
      <div class="summarizer-btn-content">
        <span class="btn-icon">🎥</span>
        <span class="btn-text">Summarize</span>
      </div>
    `;

    // Add styles
    button.style.cssText = `
      position: fixed;
      top: 100px;
      right: 20px;
      z-index: 9999;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      border: none;
      border-radius: 25px;
      padding: 12px 20px;
      cursor: pointer;
      font-family: 'Segoe UI', sans-serif;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      transition: all 0.3s ease;
      backdrop-filter: blur(10px);
      user-select: none;
      display: flex;
      align-items: center;
      gap: 8px;
    `;

    const style = document.createElement('style');
    style.textContent = `
      #yt-summarizer-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0,0,0,0.4);
      }
      
      #yt-summarizer-btn:active {
        transform: translateY(0px);
      }
      
      .summarizer-btn-content {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .btn-icon {
        font-size: 16px;
      }
      
      .btn-text {
        font-weight: 500;
      }
      
      @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
      }
      
      .processing {
        animation: pulse 2s infinite;
        background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%) !important;
      }
    `;
    document.head.appendChild(style);

    // Add click handler
    button.addEventListener('click', openExtensionPopup);

    document.body.appendChild(button);
  }

  function openExtensionPopup() {
    // This will open the extension popup programmatically
    // Note: This is a simplified approach - in practice, you might want to 
    // communicate with the background script or show an inline summary
    chrome.runtime.sendMessage({ action: 'openPopup' });
  }

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'getVideoData') {
      sendResponse({
        success: true,
        data: videoData
      });
    } else if (message.action === 'highlightButton') {
      highlightSummarizerButton(message.state);
    }
    return true;
  });

  function highlightSummarizerButton(state) {
    const button = document.getElementById('yt-summarizer-btn');
    if (button) {
      if (state === 'processing') {
        button.classList.add('processing');
        button.querySelector('.btn-text').textContent = 'Processing...';
      } else if (state === 'completed') {
        button.classList.remove('processing');
        button.querySelector('.btn-text').textContent = 'View Summary';
        setTimeout(() => {
          button.querySelector('.btn-text').textContent = 'Summarize';
        }, 3000);
      } else {
        button.classList.remove('processing');
        button.querySelector('.btn-text').textContent = 'Summarize';
      }
    }
  }

  // Inject summary overlay when requested
  function showSummaryOverlay(summaryData) {
    // Remove existing overlay
    const existingOverlay = document.getElementById('yt-summary-overlay');
    if (existingOverlay) {
      existingOverlay.remove();
    }

    const overlay = document.createElement('div');
    overlay.id = 'yt-summary-overlay';
    overlay.innerHTML = `
      <div class="summary-modal">
        <div class="summary-header">
          <h3>📋 Video Summary</h3>
          <button class="close-btn">&times;</button>
        </div>
        <div class="summary-content">
          <div class="video-info">
            <h4>${videoData.title}</h4>
            <p>Channel: ${videoData.channelName}</p>
            ${videoData.duration ? `<p>Duration: ${videoData.duration}</p>` : ''}
          </div>
          <div class="summary-text">
            ${summaryData.summary || summaryData.transcription || 'No content available'}
          </div>
        </div>
      </div>
    `;

    overlay.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.8);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
      backdrop-filter: blur(5px);
    `;

    const modalStyle = document.createElement('style');
    modalStyle.textContent = `
      .summary-modal {
        background: white;
        border-radius: 15px;
        max-width: 600px;
        max-height: 80vh;
        width: 90%;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
      }
      
      .summary-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .summary-header h3 {
        margin: 0;
        font-size: 18px;
      }
      
      .close-btn {
        background: none;
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        padding: 0;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .close-btn:hover {
        background: rgba(255,255,255,0.2);
      }
      
      .summary-content {
        padding: 20px;
        max-height: 60vh;
        overflow-y: auto;
      }
      
      .video-info {
        margin-bottom: 20px;
        padding-bottom: 15px;
        border-bottom: 1px solid #eee;
      }
      
      .video-info h4 {
        margin: 0 0 10px 0;
        color: #333;
        font-size: 16px;
      }
      
      .video-info p {
        margin: 5px 0;
        color: #666;
        font-size: 14px;
      }
      
      .summary-text {
        line-height: 1.6;
        color: #333;
        font-size: 14px;
      }
    `;
    document.head.appendChild(modalStyle);

    // Add close functionality
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        overlay.remove();
      }
    });

    overlay.querySelector('.close-btn').addEventListener('click', () => {
      overlay.remove();
    });

    document.body.appendChild(overlay);
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
