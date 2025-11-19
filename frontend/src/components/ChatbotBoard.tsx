import React, { useState, useRef, useEffect } from "react";
import { HiMinusSm } from "react-icons/hi";
import { MdSend } from "react-icons/md";
import { BsChatDots } from "react-icons/bs";
import type { DashboardResponse } from "../services/apiClient";
import { apiClient } from "../services/apiClient";

interface ChatbotBoardProps {
  onDashboardGenerated?: (data: DashboardResponse) => void;
}

const ChatbotBoard: React.FC<ChatbotBoardProps> = ({ onDashboardGenerated }) => {
  const [hasStarted, setHasStarted] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [conversation, setConversation] = useState<
    { id: number; sender: "user" | "bot"; message: string }[]
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    console.log("💬 User message:", userMessage);
    
    setHasStarted(true);
    setConversation((prev) => [
      ...prev,
      { id: Date.now(), sender: "user", message: userMessage },
    ]);

    setInput("");
    setIsLoading(true);

    try {
      console.log("📤 Sending message to API...");
      const response = await apiClient.sendChatMessage(userMessage);
      console.log("✅ API Response received:", response);

      setConversation((prev) => [
        ...prev,
        { id: Date.now() + 1, sender: "bot", message: response.message },
      ]);

      if (response.html) {
        console.log("🎨 HTML content received, length:", response.html.length);
        if (onDashboardGenerated) {
          console.log("📊 Calling onDashboardGenerated callback");
          onDashboardGenerated(response);
        }
      } else {
        console.log("⚠️ No HTML content in response");
      }
    } catch (error) {
      console.error("❌ Error sending message:", error);
      setConversation((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: "bot",
          message: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [conversation]);

  useEffect(() => {
    if (textareaRef.current && !hasStarted) {
      textareaRef.current.focus();
    }
  }, [hasStarted]);

  // If conversation has started, show floating chatbot
  if (hasStarted) {
    return (
      <div className="fixed bottom-10 right-5 font-Poppins z-40">
        {isMinimized ? (
          <button
            onClick={() => setIsMinimized(false)}
            className="border border-gray-400 flex items-center justify-center rounded-full shadow-lg h-15 w-15 transition-all hover:scale-110 bg-white"
            aria-label="Open chat"
          >
            <BsChatDots className="w-7 h-7 text-gray-700" />
          </button>
        ) : (
          <div className="w-72 md:w-96 bg-white shadow-[1px_-1px_8px_rgba(128,128,128,0.3)] rounded-lg flex flex-col transition-all duration-300 ease-in-out overflow-hidden">
            
            {/* Header */}
            <div className="w-full p-4 flex items-center justify-between bg-emerald-500 rounded-t-lg text-white">
              <h1 className="text-base font-medium">NaveeBot</h1>
              <button
                onClick={() => setIsMinimized(true)}
                className="text-lg px-2 rounded-full hover:bg-emerald-600 transition-colors"
                aria-label="Minimize chat"
              >
                <HiMinusSm />
              </button>
            </div>

            {/* Chat Messages */}
            <div
              ref={chatRef}
              className="w-full px-4 pt-4 overflow-y-auto h-[260px] md:h-[360px] text-sm"
            >
              {conversation.map((msg) => (
                <section
                  key={msg.id}
                  className={`w-full flex mb-3 ${
                    msg.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`w-2/3 max-w-full flex ${
                      msg.sender === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <p
                      className={`px-4 py-2 w-fit wrap-break-words ${
                        msg.sender === "user"
                          ? "bg-emerald-500 text-white rounded-3xl"
                          : "bg-gray-200 text-gray-800 rounded-3xl"
                      }`}
                    >
                      {msg.message}
                    </p>
                  </div>
                </section>
              ))}

              {isLoading && (
                <section className="w-full flex mb-3 justify-start">
                  <div className="w-2/3 max-w-full flex justify-start">
                    <p className="px-4 py-2 w-fit bg-gray-200 text-gray-800 rounded-3xl">
                      <span className="flex gap-0.5">
                        <span>Navee thinking </span>
                        <span className="animate-bounce" style={{ animationDelay: "0s" }}>.</span>
                        <span className="animate-bounce" style={{ animationDelay: "0.15s" }}>.</span>
                        <span className="animate-bounce" style={{ animationDelay: "0.3s" }}>.</span>
                      </span>
                    </p>
                  </div>
                </section>
              )}
            </div>

            {/* Input Area */}
            <div className="w-full flex flex-col items-center px-3 gap-2 mb-2 relative">
              <div className="flex w-full items-center gap-2 relative">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  className="w-full pl-4 pr-10 py-3 border border-gray-300 rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 text-sm resize-none"
                  placeholder="Message NaveeBot"
                  rows={1}
                  disabled={isLoading}
                />

                <button
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  className="absolute right-3 text-gray-400 hover:text-emerald-600 disabled:opacity-50 transition-colors"
                  aria-label="Send message"
                >
                  <MdSend className="w-6 h-6" />
                </button>
              </div>

              <p className="text-xs font-light text-gray-400">
                AI may produce inaccurate information
              </p>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Initial centered input view (before first message)
  return (
    <div className="fixed inset-0 flex items-center justify-center font-Poppins z-40 pointer-events-none bg-white">
      <div className="pointer-events-auto w-full max-w-2xl px-4">
        <div className="flex flex-col items-center gap-8">
          {/* Title */}
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-2">
              NaveeBot
            </h1>
            <p className="text-lg text-gray-600">
              Ask me anything to generate your dashboard
            </p>
          </div>

          {/* Large Input Field */}
          <div className="w-full relative">
            <div className="relative flex items-end gap-2">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                className="w-full pl-6 pr-14 py-4 md:py-5 border-2 border-gray-300 rounded-2xl text-gray-700 focus:outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 text-base resize-none shadow-md transition-all"
                placeholder="Describe the dashboard you want to create..."
                rows={3}
                disabled={isLoading}
              />

              <button
                onClick={handleSend}
                disabled={isLoading || !input.trim()}
                className="absolute right-4 bottom-4 p-2.5 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-400 text-white rounded-full transition-all hover:scale-110 disabled:scale-100"
                aria-label="Send message"
              >
                <MdSend className="w-6 h-6" />
              </button>
            </div>

            <p className="text-sm text-gray-500 mt-4 text-center">
              Press Shift + Enter for new line, or Enter to send
            </p>
          </div>

          {/* Example Prompts */}
          <div className="w-full mt-8">
            <p className="text-sm text-gray-600 text-center mb-4">Examples:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {[
                "Create a sales dashboard with monthly revenue",
                "Build an analytics dashboard with user metrics",
                "Design a project tracking dashboard",
                "Make a financial performance dashboard",
              ].map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setInput(prompt);
                    // Focus textarea for immediate sending
                    setTimeout(() => textareaRef.current?.focus(), 0);
                  }}
                  className="p-3 text-sm text-left text-gray-700 border border-gray-300 rounded-lg hover:border-emerald-500 hover:bg-emerald-50 transition-all"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatbotBoard;
