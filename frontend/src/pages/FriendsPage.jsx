import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getFriends, getFriendRequests, acceptFriendRequest, declineFriendRequest, searchUsers, sendFriendRequest } from "../api/client";

export default function FriendsPage() {
  const [friends, setFriends] = useState([]);
  const [requests, setRequests] = useState({ received: [], sent: [] });
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [friendsRes, requestsRes] = await Promise.all([
        getFriends(),
        getFriendRequests(),
      ]);
      setFriends(friendsRes.data);
      setRequests(requestsRes.data);
    } catch (err) {
      setError("Failed to load friends");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const { data } = await searchUsers(searchQuery.trim());
      setSearchResults(data);
    } catch (err) {
      setError("Search failed");
    } finally {
      setSearchLoading(false);
    }
  };

  const handleAddFriend = async (email) => {
    try {
      await sendFriendRequest(email);
      setSearchResults(searchResults.filter(u => u.email !== email));
      loadData();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to send request");
    }
  };

  const handleAccept = async (requestId) => {
    try {
      await acceptFriendRequest(requestId);
      loadData();
    } catch (err) {
      setError("Failed to accept");
    }
  };

  const handleDecline = async (requestId) => {
    try {
      await declineFriendRequest(requestId);
      loadData();
    } catch (err) {
      setError("Failed to decline");
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
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Friends</h1>

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          type="text"
          className="input input-bordered flex-1"
          placeholder="Search users by name or email..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button type="submit" className="btn btn-primary" disabled={searchLoading}>
          {searchLoading ? <span className="loading loading-spinner loading-sm"></span> : "Search"}
        </button>
      </form>

      {error && (
        <div className="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      )}

      {/* Search Results */}
      {searchResults.length > 0 && (
        <div className="mb-6">
          <h2 className="font-bold text-lg mb-2">Search Results</h2>
          <div className="space-y-2">
            {searchResults.map((user) => (
              <div key={user.id} className="card bg-base-100 shadow-sm p-3 flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-content">
                  {user.name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{user.name || user.email}</p>
                  <p className="text-sm text-base-content/60 truncate">{user.email}</p>
                </div>
                <button className="btn btn-sm btn-primary" onClick={() => handleAddFriend(user.email)}>
                  Add Friend
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Friend Requests */}
      {requests.received.length > 0 && (
        <div className="mb-6">
          <h2 className="font-bold text-lg mb-2">Friend Requests</h2>
          <div className="space-y-2">
            {requests.received.map((req) => (
              <div key={req.id} className="card bg-base-100 shadow-sm p-3 flex items-center gap-3">
                <div className="flex-1">
                  <p className="font-medium">Request from user {req.sender}</p>
                </div>
                <button className="btn btn-sm btn-primary" onClick={() => handleAccept(req.id)}>
                  Accept
                </button>
                <button className="btn btn-sm btn-ghost" onClick={() => handleDecline(req.id)}>
                  Decline
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Friends List */}
      <div>
        <h2 className="font-bold text-lg mb-2">Your Friends ({friends.length})</h2>
        {friends.length === 0 ? (
          <p className="text-base-content/50">No friends yet. Search for people above!</p>
        ) : (
          <div className="space-y-2">
            {friends.map((friend) => (
              <Link
                key={friend.id}
                to={`/profile/${friend.id}`}
                className="card bg-base-100 shadow-sm p-3 flex items-center gap-3 hover:shadow-md transition-shadow"
              >
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-primary-content">
                  {friend.name?.[0]?.toUpperCase() || friend.email[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{friend.name || friend.email}</p>
                  <p className="text-sm text-base-content/60 truncate">{friend.email}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
