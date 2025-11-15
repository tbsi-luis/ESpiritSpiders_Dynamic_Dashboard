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
  const [isOpen, setIsOpen] = useState(false);
  const [conversation, setConversation] = useState<
    { id: number; sender: "user" | "bot"; message: string }[]
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    console.log("💬 User message:", userMessage);
    
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

  return (
    <div className="relative w-fit h-fit font-Poppins">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-10 right-5 border border-gray-400 flex items-center justify-center rounded-full shadow-lg h-15 w-15 transition-all hover:scale-110 bg-white"
      >
        <BsChatDots className="w-7 h-7 text-gray-700" />
      </button>

      {isOpen && (
        <div className="fixed bottom-20 right-5 w-72 md:w-96 bg-white shadow-[1px_-1px_8px_rgba(128,128,128,0.3)] rounded-lg flex flex-col transition-all duration-300 ease-in-out">
          
          <div className="w-full p-4 flex items-center justify-between bg-emerald-500 rounded-t-lg text-white">
            <h1 className="text-base font-medium">NaveeBot</h1>
            <button
              onClick={() => setIsOpen(false)}
              className="text-lg px-2 rounded-full hover:bg-emerald-600"
            >
              <HiMinusSm />
            </button>
          </div>

          <div
            ref={chatRef}
            className="w-full px-4 pt-4 overflow-y-auto h-[260px] md:h-[360px] text-sm"
          >
            {conversation.length === 0 && (
              <div className="w-full flex flex-col items-center p-4 gap-4 text-center text-gray-500">
                <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                  <BsChatDots className="w-6 h-6 text-gray-600" />
                </div>
                <p className="text-sm">
                  <span className="text-base font-medium">Hi there!</span>
                  <br />
                  I’m NaveeBot. How can I help?
                </p>
              </div>
            )}

            {conversation.map((msg) => (
              <section
                key={msg.id}
                className={`w-full flex mb-1 ${
                  msg.sender === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`w-2/3 max-w-full flex ${
                    msg.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <p
                    className={`px-4 py-2 w-fit wrap-break-word ${
                      msg.sender === "user"
                        ? "bg-emerald-500 text-white rounded-s-xl rounded-br-xl rounded-tr-sm"
                        : "bg-gray-200 text-gray-800 rounded-e-xl rounded-bl-xl rounded-tl-sm"
                    }`}
                  >
                    {msg.message}
                  </p>
                </div>
              </section>
            ))}
          </div>

          <div className="w-full flex flex-col items-center px-3 gap-2 mb-2 relative">
            <div className="flex w-full items-center gap-2 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                className="w-full pl-4 pr-10 py-3 border border-gray-300 rounded-lg text-gray-700 focus:outline-emerald-500 text-sm resize-none"
                placeholder="Message NaveeBot"
                rows={1}
              />

              <button
                onClick={handleSend}
                className="absolute right-3 text-gray-400 hover:text-gray-700"
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
};

export default ChatbotBoard;
