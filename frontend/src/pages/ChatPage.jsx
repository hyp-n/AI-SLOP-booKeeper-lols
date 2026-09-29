import { useState, useEffect, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import { getConversations, getMessages, sendMessage, createConversation, getFriends } from "../api/client";

export default function ChatPage() {
  const { convId } = useParams();
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [friends, setFriends] = useState([]);
  const [showNewChat, setShowNewChat] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
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

    setSending(true);
    setError("");
    try {
      const { data } = await sendMessage(convId, newMessage.trim());
      setMessages((prev) => [...prev, data]);
      setNewMessage("");
    } catch (err) {
      setError(err.response?.data?.error || "Failed to send message");
    } finally {
      setSending(false);
    }
  };

  const getOtherParticipant = (conv) => {
    if (!conv.participant_details || conv.participant_details.length < 2) return null;
    const currentUser = JSON.parse(localStorage.getItem("user") || "{}");
    return conv.participant_details.find(p => p.id !== currentUser.id) || conv.participant_details[0];
  };

  const getConversationDisplay = (conv) => {
    if (conv.is_group) return conv.group_name;
    const other = getOtherParticipant(conv);
    return other?.name || other?.email || "Chat";
  };

  const getConversationAvatar = (conv) => {
    if (conv.is_group) return "G";
    const other = getOtherParticipant(conv);
    return other?.name?.[0]?.toUpperCase() || other?.email?.[0]?.toUpperCase() || "?";
  };

  const getConversationSubtitle = (conv) => {
    if (conv.is_group) {
      const count = conv.participant_details?.length || 0;
      return `${count} member${count !== 1 ? "s" : ""}`;
    }
    const other = getOtherParticipant(conv);
    return other?.email || "";
  };

  const getLastMessagePreview = (conv) => {
    if (!conv.last_message) return null;
    const content = conv.last_message.content;
    return content.length > 50 ? content.substring(0, 50) + "..." : content;
  };

  const formatTime = (dateString) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return "just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const isOwnMessage = (msg) => {
    const currentUser = JSON.parse(localStorage.getItem("user") || "{}");
    return msg.sender === currentUser.id;
  };

  const getMessageStatus = (msg) => {
    if (!msg.read_by || !Array.isArray(msg.read_by)) return "sent";
    const otherParticipant = getOtherParticipant(activeConv);
    if (!otherParticipant) return "sent";
    return msg.read_by.includes(otherParticipant.id) ? "read" : "delivered";
  };

  const getConversationLastMessageTime = (conv) => {
    if (!conv.last_message) return null;
    return formatTime(conv.last_message.created_at);
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
                    {getConversationAvatar(conv)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="font-medium truncate">
                        {getConversationDisplay(conv)}
                      </p>
                      <p className="text-xs text-base-content/40 ml-2">
                        {getConversationLastMessageTime(conv)}
                      </p>
                    </div>
                    <p className="text-xs text-base-content/50 truncate">
                      {getConversationSubtitle(conv)}
                    </p>
                    {conv.last_message && (
                      <p className="text-sm text-base-content/60 truncate">
                        {getLastMessagePreview(conv)}
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
                {getConversationDisplay(activeConv)}
              </h3>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.length === 0 ? (
                <p className="text-center text-base-content/50 py-8">No messages yet</p>
              ) : (
                messages.map((msg) => {
                  const own = isOwnMessage(msg);
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${own ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[70%] rounded-lg p-3 ${
                          own
                            ? "bg-primary text-primary-content"
                            : "bg-base-200"
                        }`}
                      >
                        <p className="text-sm">{msg.content}</p>
                        <div className="flex items-center justify-between mt-1">
                          <p className="text-xs opacity-60">
                            {formatTime(msg.created_at)}
                          </p>
                          {own && (
                            <p className="text-xs opacity-60">
                              {getMessageStatus(msg)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
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
                <button type="submit" className="btn btn-primary" disabled={!newMessage.trim() || sending}>
                  {sending ? <span className="loading loading-spinner loading-sm"></span> : "Send"}
                </button>
              </div>
              {error && (
                <div className="alert alert-error mt-2">
                  <span>{error}</span>
                </div>
              )}
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
            {friends.length === 0 ? (
              <p className="text-base-content/50">No friends yet. Add friends from the Friends page first.</p>
            ) : (
              <div className="space-y-2">
                {friends.map((friend) => (
                  <button
                    key={friend.id}
                    className="btn btn-ghost btn-block justify-start"
                    onClick={() => handleStartChat(friend.id)}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-primary-content text-sm">
                        {friend.name?.[0]?.toUpperCase() || friend.email[0].toUpperCase()}
                      </div>
                      <div className="flex-1 min-w-0 text-left">
                        <p className="font-medium truncate">{friend.name || friend.email}</p>
                        {friend.name && (
                          <p className="text-sm text-base-content/60 truncate">{friend.email}</p>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}
            <div className="modal-action">
              <button className="btn" onClick={() => setShowNewChat(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
