import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { getUserProfile, getMe, sendFriendRequest, acceptFriendRequest, declineFriendRequest, removeFriend } from "../api/client";

export default function ProfilePage() {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, [userId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [profileRes, meRes] = await Promise.all([
        getUserProfile(userId),
        getMe(),
      ]);
      setProfile(profileRes.data);
      setCurrentUser(meRes.data);
    } catch (err) {
      setError("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleAddFriend = async () => {
    try {
      await sendFriendRequest(profile.email);
      loadData();
    } catch (err) {
      setError(err.response?.data?.error || "Failed to send request");
    }
  };

  const handleAccept = async () => {
    try {
      await acceptFriendRequest(profile.friend_request_id);
      loadData();
    } catch (err) {
      setError("Failed to accept request");
    }
  };

  const handleDecline = async () => {
    try {
      await declineFriendRequest(profile.friend_request_id);
      loadData();
    } catch (err) {
      setError("Failed to decline request");
    }
  };

  const handleRemoveFriend = async () => {
    try {
      await removeFriend(userId);
      loadData();
    } catch (err) {
      setError("Failed to remove friend");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="text-center py-16">
        <p className="text-lg">User not found</p>
        <Link to="/" className="btn btn-primary mt-4">Back to Library</Link>
      </div>
    );
  }

  const isOwnProfile = currentUser && currentUser.id === profile.id;

  return (
    <div className="max-w-2xl mx-auto">
      <Link to="/" className="btn btn-sm btn-ghost mb-4">
        &larr; Back
      </Link>

      <div className="card bg-base-100 shadow-md p-6">
        <div className="flex items-center gap-4 mb-6">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt="" className="w-20 h-20 rounded-full object-cover" />
          ) : (
            <div className="w-20 h-20 rounded-full bg-primary flex items-center justify-center text-2xl text-primary-content">
              {profile.name?.[0]?.toUpperCase() || profile.email[0].toUpperCase()}
            </div>
          )}
          <div className="flex-1">
            <h1 className="text-2xl font-bold">{profile.name || profile.email}</h1>
            <p className="text-base-content/60">{profile.email}</p>
          </div>
          {!isOwnProfile && (
            <div className="flex gap-2">
              {profile.friendship_status === "accepted" && (
                <button className="btn btn-sm btn-error" onClick={handleRemoveFriend}>
                  Remove Friend
                </button>
              )}
              {profile.friendship_status === "pending" && profile.friend_request_id && (
                <>
                  <button className="btn btn-sm btn-primary" onClick={handleAccept}>
                    Accept
                  </button>
                  <button className="btn btn-sm btn-ghost" onClick={handleDecline}>
                    Decline
                  </button>
                </>
              )}
              {!profile.friendship_status && (
                <button className="btn btn-sm btn-primary" onClick={handleAddFriend}>
                  Add Friend
                </button>
              )}
            </div>
          )}
        </div>

        {profile.bio && (
          <div className="mb-4">
            <h3 className="font-bold mb-1">Bio</h3>
            <p className="text-base-content/70">{profile.bio}</p>
          </div>
        )}

        {profile.currently_reading_book && (
          <div className="mb-4">
            <h3 className="font-bold mb-2">Currently Reading</h3>
            <div className="flex items-center gap-3 p-3 rounded bg-base-200">
              {profile.currently_reading_book.cover_url && (
                <img src={profile.currently_reading_book.cover_url} alt="" className="w-12 h-16 object-cover rounded" />
              )}
              <div>
                <p className="font-medium">{profile.currently_reading_book.title}</p>
                <p className="text-sm text-base-content/60">{profile.currently_reading_book.author}</p>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="alert alert-error mt-4">
            <span>{error}</span>
          </div>
        )}
      </div>
    </div>
  );
}
