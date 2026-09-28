import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { getConversations, getMessages, sendMessage, createConversation, getFriends, addToGroup, renameGroup } from "../api/client";

export default function ChatPage() {
  const { convId } = useParams();
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [friends, setFriends] = useState([]);
  const [showNewChat, setShowNewChat] = useState(false);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(true);
  const messagesEndRef = useRef(null);
  const pollingRef = useRef(null);

  useEffect(() => {
    loadData();
  }, [convId]);

  useEffect(() => {
    if (convId) {
      loadMessages(convId);
    }
  }, [convId]);

  // Poll for new messages every 3 seconds (works without WebSockets)
  useEffect(() => {
    if (!convId || !polling) {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
      return;
    }

    pollingRef.current = setInterval(async () => {
      try {
        const { data } = await getMessages(convId);
        setMessages(data);
      } catch (err) {
        // Silently fail on polling errors
      }
    }, 3000);

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [convId, polling]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [convsRes, friendsRes] = await Promise.all([
        getConversations(),
        getFriends(),
      ]);
      setConversations(convsRes.data);
      setFriends(friendsRes.data);
      if (convId) {
        const conv = convsRes.data.find(c => c.id === convId);
        setActiveConv(conv || null);
      }
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (cid) => {
    try {
      const { data } = await getMessages(cid);
      setMessages(data);
    } catch (err) {
      console.error("Failed to load messages:", err);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !convId) return;

    try {
      const { data } = await sendMessage(convId, newMessage.trim());
      setMessages((prev) => [...prev, data]);
      setNewMessage("");
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };

  const handleStartChat = async (friendId) => {
    try {
      const { data } = await createConversation({ participant_ids: [friendId] });
      setShowNewChat(false);
      loadData();
      window.location.href = `/chat/${data.id}`;
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  };

  const handleCreateGroup = async (name, memberIds) => {
    try {
      const { data } = await createConversation({
        participant_ids: memberIds,
        is_group: true,
        group_name: name,
      });
      setShowNewChat(false);
      loadData();
      window.location.href = `/chat/${data.id}`;
    } catch (err) {
      console.error("Failed to create group:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-8rem)]">
      {/* Sidebar */}
      <div className="w-80 border-r border-base-300 flex flex-col">
        <div className="p-4 border-b border-base-300">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-bold text-lg">Messages</h2>
            <button className="btn btn-sm btn-primary" onClick={() => setShowNewChat(true)}>
              + New
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <p className="p-4 text-base-content/50">No conversations yet</p>
          ) : (
            conversations.map((conv) => (
              <Link
                key={conv.id}
                to={`/chat/${conv.id}`}
                className={`p-3 border-b border-base-300 hover:bg-base-200 transition-colors block ${
                  convId === conv.id ? "bg-base-200" : ""
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-content">
                    {conv.is_group ? "G" : conv.participant_details?.[0]?.name?.[0]?.toUpperCase() || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">
                      {conv.is_group
                        ? conv.group_name
                        : conv.participant_details?.find(p => p.id !== conv.participant_details[0]?.id)?.name || "Chat"}
                    </p>
                    {conv.last_message && (
                      <p className="text-sm text-base-content/60 truncate">
                        {conv.last_message.content}
                      </p>
                    )}
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 flex flex-col">
        {activeConv ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-base-300">
              <h3 className="font-bold">
                {activeConv.is_group
                  ? activeConv.group_name
                  : activeConv.participant_details?.find(p => p.id !== activeConv.participant_details[0]?.id)?.name || "Chat"}
              </h3>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.length === 0 ? (
                <p className="text-center text-base-content/50 py-8">No messages yet</p>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.sender === activeConv.participant_details?.[0]?.id ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[70%] rounded-lg p-3 ${
                        msg.sender === activeConv.participant_details?.[0]?.id
                          ? "bg-primary text-primary-content"
                          : "bg-base-200"
                      }`}
                    >
                      <p className="text-sm">{msg.content}</p>
                      <p className="text-xs opacity-60 mt-1">
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="p-4 border-t border-base-300">
              <div className="flex gap-2">
                <input
                  type="text"
                  className="input input-bordered flex-1"
                  placeholder="Type a message..."
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                />
                <button type="submit" className="btn btn-primary">Send</button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <p className="text-lg text-base-content/50 mb-4">Select a conversation or start a new one</p>
              <button className="btn btn-primary" onClick={() => setShowNewChat(true)}>
                Start a Conversation
              </button>
            </div>
          </div>
        )}
      </div>

      {/* New Chat Modal */}
      {showNewChat && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">New Conversation</h3>
            <div className="space-y-2">
              {friends.map((friend) => (
                <button
                  key={friend.id}
                  className="btn btn-ghost btn-block justify-start"
                  onClick={() => handleStartChat(friend.id)}
                >
                  {friend.name || friend.email}
                </button>
              ))}
            </div>
            <div className="modal-action">
              <button className="btn" onClick={() => setShowNewChat(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
