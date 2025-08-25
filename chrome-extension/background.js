// background.js - Background service worker
chrome.runtime.onInstalled.addListener(() => {
  console.log('YouTube Summarizer extension installed');
  
  // Set default settings
  chrome.storage.local.set({
    settings: {
      backendUrl: 'http://localhost:8002',
      autoSummarize: false,
      summaryLength: 'medium',
      enableNotifications: true
    }
  });

  // Setup cleanup alarm
  setupCleanupAlarm();
});

// Handle messages from popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.action) {
    case 'openPopup':
      // This is called from content script when floating button is clicked
      // We can't programmatically open popup, but we can store the request
      chrome.storage.local.set({
        popupRequested: {
          timestamp: Date.now(),
          tabId: sender.tab.id
        }
      });
      break;
      
    case 'processVideo':
      handleVideoProcessing(message.data, sender, sendResponse);
      return true; // Will respond asynchronously
      
    case 'getStoredSummary':
      getStoredSummary(message.videoId, sendResponse);
      return true;
      
    case 'checkBackendStatus':
      checkBackendStatus(sendResponse);
      return true;
  }
});

async function handleVideoProcessing(data, sender, sendResponse) {
  try {
    // Notify content script that processing started
    chrome.tabs.sendMessage(sender.tab.id, {
      action: 'highlightButton',
      state: 'processing'
    });

    // Send request to backend
    const response = await fetch(`${data.backendUrl}/process-video`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: data.videoUrl,
        action: data.action,
        videoId: data.videoId
      })
    });

    const result = await response.json();

    if (result.success) {
      // Store result
      const storageKey = `${data.action}_${data.videoId}`;
      await chrome.storage.local.set({
        [storageKey]: {
          result: result.data,
          timestamp: Date.now(),
          videoTitle: data.videoTitle
        }
      });

      // Notify content script
      chrome.tabs.sendMessage(sender.tab.id, {
        action: 'highlightButton',
        state: 'completed'
      });

      // Show notification if enabled
      const settings = await getSettings();
      if (settings.enableNotifications) {
        showNotification('Summary Complete', `Successfully processed: ${data.videoTitle}`);
      }

      sendResponse({ success: true, data: result.data });
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('Background processing error:', error);
    
    // Notify content script of error
    chrome.tabs.sendMessage(sender.tab.id, {
      action: 'highlightButton',
      state: 'error'
    });

    sendResponse({ success: false, error: error.message });
  }
}

async function getStoredSummary(videoId, sendResponse) {
  try {
    const summaryKey = `summarize_${videoId}`;
    const transcribeKey = `transcribe_${videoId}`;
    
    const result = await chrome.storage.local.get([summaryKey, transcribeKey]);
    
    sendResponse({
      success: true,
      summary: result[summaryKey] || null,
      transcription: result[transcribeKey] || null
    });
  } catch (error) {
    sendResponse({ success: false, error: error.message });
  }
}

async function checkBackendStatus(sendResponse) {
  try {
    const settings = await getSettings();
    const response = await fetch(`${settings.backendUrl}/health`, {
      method: 'GET'
    });
    
    sendResponse({ 
      success: true, 
      status: response.ok ? 'running' : 'error',
      url: settings.backendUrl
    });
  } catch (error) {
    sendResponse({ 
      success: false, 
      status: 'offline',
      error: error.message 
    });
  }
}

async function getSettings() {
  const result = await chrome.storage.local.get('settings');
  return result.settings || {
    backendUrl: 'http://localhost:8002',
    autoSummarize: false,
    summaryLength: 'medium',
    enableNotifications: true
  };
}

function showNotification(title, message) {
  if (chrome.notifications) {
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: title,
      message: message
    });
  } else {
    console.log('Notifications API not available:', title, message);
  }
}

// Handle tab updates to detect YouTube navigation
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url && tab.url.includes('youtube.com/watch')) {
    // Check if auto-summarize is enabled
    getSettings().then(settings => {
      if (settings.autoSummarize) {
        // Wait a bit for the page to fully load
        setTimeout(() => {
          chrome.tabs.sendMessage(tabId, { action: 'autoSummarize' });
        }, 2000);
      }
    });
  }
});

// Set up cleanup alarm when extension is installed/started
chrome.runtime.onStartup.addListener(() => {
  setupCleanupAlarm();
});

function setupCleanupAlarm() {
  if (chrome.alarms) {
    // Clear existing alarm first
    chrome.alarms.clear('cleanupStorage', () => {
      // Create new alarm for cleaning up old stored summaries (older than 7 days)
      chrome.alarms.create('cleanupStorage', { 
        delayInMinutes: 60, // Run every hour
        periodInMinutes: 60 
      });
    });
  } else {
    console.log('Alarms API not available');
  }
}

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'cleanupStorage') {
    cleanupOldSummaries();
  }
});

async function cleanupOldSummaries() {
  const WEEK_IN_MS = 7 * 24 * 60 * 60 * 1000;
  const cutoffTime = Date.now() - WEEK_IN_MS;
  
  const allData = await chrome.storage.local.get();
  const keysToRemove = [];
  
  for (const [key, value] of Object.entries(allData)) {
    if ((key.startsWith('summarize_') || key.startsWith('transcribe_')) && 
        value.timestamp && value.timestamp < cutoffTime) {
      keysToRemove.push(key);
    }
  }
  
  if (keysToRemove.length > 0) {
    await chrome.storage.local.remove(keysToRemove);
    console.log(`Cleaned up ${keysToRemove.length} old summaries`);
  }
}
