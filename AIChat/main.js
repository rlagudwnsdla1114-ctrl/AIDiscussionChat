(function () {
  function getApiBaseUrl() {
    if (window.location.protocol === "file:") {
      return "http://127.0.0.1:8000";
    }
    return window.location.origin;
  }

  function getPageConfig() {
    const pathname = window.location.pathname;
    if (pathname.endsWith("anime-chat.html")) {
      return {
        storageKey: "debateMind:anime-chats",
        sendEventName: "debateMind:anime-send",
        receiveEventName: "debateMind:anime-receive",
        endpoint: "/api/anime/chat",
        fallback:
          "지금은 응답을 불러오지 못했어요. 애니 작품, 캐릭터, 전개, 결말 중 어떤 이야기를 하고 싶은지 한 번 더 말해주면 이어서 도와드릴게요.",
      };
    }

    if (pathname.endsWith("drama-chat.html")) {
      return {
        storageKey: "debateMind:drama-chats",
        sendEventName: "debateMind:drama-send",
        receiveEventName: "debateMind:drama-receive",
        endpoint: "/api/drama/chat",
        fallback:
          "지금은 응답을 불러오지 못했어요. 드라마 작품, 인물, 전개, 결말 중 어떤 이야기를 하고 싶은지 한 번 더 말해주면 이어서 도와드릴게요.",
      };
    }

    return null;
  }

  function getActiveConversationHistory(storageKey) {
    try {
      const raw = localStorage.getItem(storageKey);
      const parsed = raw ? JSON.parse(raw) : null;
      if (!parsed || !Array.isArray(parsed.conversations)) {
        return [];
      }

      const activeConversation = parsed.conversations.find(
        (conversation) => conversation.id === parsed.activeId
      );

      if (!activeConversation || !Array.isArray(activeConversation.messages)) {
        return [];
      }

      return activeConversation.messages.map((message) => ({
        role: message.role,
        content: message.text,
      }));
    } catch (error) {
      return [];
    }
  }

  async function requestChatAnswer(config, message, mode) {
    const response = await fetch(`${getApiBaseUrl()}${config.endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        mode,
        history: getActiveConversationHistory(config.storageKey),
      }),
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    return response.json();
  }

  function dispatchAssistantMessage(eventName, answer) {
    document.dispatchEvent(
      new CustomEvent(eventName, {
        detail: { text: answer },
      })
    );
  }

  document.addEventListener("DOMContentLoaded", function () {
    const config = getPageConfig();
    if (!config) {
      return;
    }

    document.addEventListener(config.sendEventName, async function (event) {
      const message = event.detail && event.detail.text ? event.detail.text.trim() : "";
      const mode =
        event.detail && (event.detail.mode === "discussion" || event.detail.mode === "normal")
          ? event.detail.mode
          : "normal";
      if (!message) {
        return;
      }

      try {
        const payload = await requestChatAnswer(config, message, mode);
        dispatchAssistantMessage(config.receiveEventName, payload.answer || config.fallback);
      } catch (error) {
        dispatchAssistantMessage(config.receiveEventName, config.fallback);
      }
    });
  });
})();
