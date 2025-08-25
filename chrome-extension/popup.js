// popup.js - Extension popup logic
document.addEventListener('DOMContentLoaded', async () => {
  const elements = {
    videoInfo: document.getElementById('videoInfo'),
    videoTitle: document.getElementById('videoTitle'),
    videoUrl: document.getElementById('videoUrl'),
    notOnYoutube: document.getElementById('notOnYoutube'),
    summarizeBtn: document.getElementById('summarizeBtn'),
    transcribeBtn: document.getElementById('transcribeBtn'),
    settingsBtn: document.getElementById('settingsBtn'),
    progressContainer: document.getElementById('progressContainer'),
    progressBar: document.getElementById('progressBar'),
    progressText: document.getElementById('progressText'),
    loadingContainer: document.getElementById('loadingContainer'),
    errorContainer: document.getElementById('errorContainer'),
    errorText: document.getElementById('errorText'),
    summaryContainer: document.getElementById('summaryContainer'),
    summaryText: document.getElementById('summaryText')
  };

  let currentVideoData = null;

  // Initialize popup
  await initializePopup();

  // Event listeners
  elements.summarizeBtn.addEventListener('click', () => processVideo('summarize'));
  elements.transcribeBtn.addEventListener('click', () => processVideo('transcribe'));
  elements.settingsBtn.addEventListener('click', openSettings);

  async function initializePopup() {
    try {
      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab.url.includes('youtube.com/watch')) {
        showNotOnYoutube();
        return;
      }

      // Try to get video data from content script with retry logic
      const response = await getVideoDataWithRetry(tab.id);
      
      if (response && response.success) {
        currentVideoData = response.data;
        showVideoInfo(currentVideoData);
        enableButtons();
      } else {
        // Fallback: extract video data from URL
        const fallbackData = extractVideoDataFromUrl(tab.url);
        if (fallbackData) {
          currentVideoData = fallbackData;
          showVideoInfo(currentVideoData);
          enableButtons();
        } else {
          showError('Unable to detect video information');
        }
      }
    } catch (error) {
      console.error('Error initializing popup:', error);
      // Try fallback method
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const fallbackData = extractVideoDataFromUrl(tab.url);
        if (fallbackData) {
          currentVideoData = fallbackData;
          showVideoInfo(currentVideoData);
          enableButtons();
        } else {
          showError('Failed to initialize extension - content script not available');
        }
      } catch (fallbackError) {
        showError('Failed to initialize extension');
      }
    }
  }

  async function getVideoDataWithRetry(tabId, maxRetries = 3, delay = 500) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await chrome.tabs.sendMessage(tabId, { action: 'getVideoData' });
        if (response && response.success) {
          return response;
        }
      } catch (error) {
        console.log(`Attempt ${i + 1} failed:`, error.message);
        
        // If content script is not available, try to inject it
        if (error.message.includes('Could not establish connection')) {
          try {
            await chrome.scripting.executeScript({
              target: { tabId: tabId },
              files: ['content.js']
            });
            console.log('Content script injected successfully');
            // Wait a bit for the script to initialize
            await new Promise(resolve => setTimeout(resolve, 1000));
          } catch (injectError) {
            console.error('Failed to inject content script:', injectError);
          }
        }
        
        if (i < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }
    return null;
  }

  function extractVideoDataFromUrl(url) {
    try {
      const urlObj = new URL(url);
      const videoId = urlObj.searchParams.get('v');
      
      if (!videoId) {
        return null;
      }

      return {
        url: url,
        videoId: videoId,
        title: 'YouTube Video', // Generic title as fallback
        duration: null,
        channelName: null
      };
    } catch (error) {
      console.error('Error extracting video data from URL:', error);
      return null;
    }
  }

  function showVideoInfo(videoData) {
    // Clean up any existing fallback notes
    const existingNote = elements.videoInfo.querySelector('.fallback-note');
    if (existingNote) {
      existingNote.remove();
    }
    
    elements.videoTitle.textContent = videoData.title || 'YouTube Video';
    elements.videoUrl.textContent = videoData.url;
    elements.videoInfo.classList.remove('hidden');
    elements.notOnYoutube.classList.add('hidden');
    
    // Add a note if using fallback data
    if (videoData.title === 'YouTube Video') {
      const note = document.createElement('div');
      note.className = 'fallback-note';
      note.style.fontSize = '12px';
      note.style.color = '#666';
      note.style.marginTop = '5px';
      note.textContent = 'Note: Using basic video detection';
      elements.videoInfo.appendChild(note);
    }
  }

  function showNotOnYoutube() {
    elements.videoInfo.classList.add('hidden');
    elements.notOnYoutube.classList.remove('hidden');
  }

  function enableButtons() {
    elements.summarizeBtn.disabled = false;
    elements.transcribeBtn.disabled = false;
  }

  function disableButtons() {
    elements.summarizeBtn.disabled = true;
    elements.transcribeBtn.disabled = true;
  }

  async function processVideo(action) {
    if (!currentVideoData) {
      showError('No video data available');
      return;
    }

    disableButtons();
    hideError();
    hideSummary();
    showLoading();

    try {
      // Check if backend is running
      const backendStatus = await checkBackendStatus();
      if (!backendStatus) {
        throw new Error('Backend server is not running. Please start the backend service.');
      }

      // Send request to backend
      const response = await fetch('http://localhost:8002/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: currentVideoData.url,
          action: action,
          videoId: currentVideoData.videoId
        })
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        showSummary(result.data, action);
        
        // Store result in storage
        await chrome.storage.local.set({
          [`${action}_${currentVideoData.videoId}`]: {
            result: result.data,
            timestamp: Date.now(),
            videoTitle: currentVideoData.title
          }
        });
      } else {
        throw new Error(result.error || 'Unknown error occurred');
      }
    } catch (error) {
      console.error('Error processing video:', error);
      showError(error.message);
    } finally {
      hideLoading();
      enableButtons();
    }
  }

  async function checkBackendStatus() {
    try {
      const response = await fetch('http://localhost:8002/health', {
        method: 'GET',
        timeout: 5000
      });
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  function showLoading() {
    elements.loadingContainer.classList.remove('hidden');
    elements.progressContainer.classList.remove('hidden');
    updateProgress(0, 'Initializing...');
  }

  function hideLoading() {
    elements.loadingContainer.classList.add('hidden');
    elements.progressContainer.classList.add('hidden');
  }

  function updateProgress(percentage, text) {
    elements.progressBar.style.width = `${percentage}%`;
    elements.progressText.textContent = text;
  }

  function showError(message) {
    elements.errorText.textContent = message;
    elements.errorContainer.classList.remove('hidden');
  }

  function hideError() {
    elements.errorContainer.classList.add('hidden');
  }

  function showSummary(data, action) {
    const title = action === 'summarize' ? '📋 Summary' : '🎤 Transcription';
    elements.summaryContainer.querySelector('.summary-title').textContent = title;
    elements.summaryText.textContent = data.summary || data.transcription || 'No content available';
    elements.summaryContainer.classList.remove('hidden');
  }

  function hideSummary() {
    elements.summaryContainer.classList.add('hidden');
  }

  function openSettings() {
    // Create settings page
    chrome.tabs.create({
      url: chrome.runtime.getURL('settings.html')
    });
  }

  // Listen for background script messages
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'updateProgress') {
      updateProgress(message.percentage, message.text);
    }
  });
});
