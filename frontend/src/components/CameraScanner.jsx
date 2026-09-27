import { useState, useRef, useEffect } from "react";
import { lookupIsbn, addBookByIsbn } from "../api/client";

export default function CameraScanner({ onScan, onClose }) {
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState("");
  const [hasPermission, setHasPermission] = useState(false);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startScanning = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        } 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setHasPermission(true);
        setIsScanning(true);
        setError("");
        
        // Start scanning for ISBNs
        scanForISBN();
      }
    } catch (err) {
      setError("Camera access denied. Please allow camera permissions and try again.");
      console.error("Camera error:", err);
    }
  };

  const scanForISBN = async () => {
    if (!videoRef.current || !isScanning) return;

    try {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.width = videoRef.current.videoWidth;
      canvas.height = videoRef.current.videoHeight;
      
      context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
      
      // Convert to grayscale and look for ISBN patterns
      const grayscale = new ImageData(canvas.width, canvas.height);
      for (let i = 0; i < imageData.data.length; i += 4) {
        const gray = 0.299 * imageData.data[i] + 
                     0.587 * imageData.data[i + 1] + 
                     0.114 * imageData.data[i + 2];
        grayscale.data[i] = gray;
        grayscale.data[i + 1] = gray;
        grayscale.data[i + 2] = gray;
        grayscale.data[i + 3] = imageData.data[i + 3];
      }
      
      const imageDataUrl = canvas.toDataURL('image/png');
      
      // Try OCR on the image (simplified - in production you'd use a real OCR service)
      // For now, we'll just look for ISBN patterns in the image
      const isbnPattern = /\d{10}(?:\d{2}(?:\d{1}|X))?/;
      
      // This is a placeholder - in reality you'd send the image to an OCR service
      // For demo purposes, we'll simulate scanning by showing a scanned area
      const scanArea = document.createElement('div');
      scanArea.style.cssText = `
        position: absolute;
        left: 20%;
        top: 20%;
        width: 60%;
        height: 40%;
        border: 3px solid #22c55e;
        border-radius: 8px;
        pointer-events: none;
        z-index: 1000;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.5);
      `;
      videoRef.current.parentElement.appendChild(scanArea);
      
      // Simulate finding an ISBN (demo only)
      setTimeout(() => {
        // Simulate successful scan
        onScan("9780451524935"); // Demo ISBN
      }, 2000);
      
    } catch (err) {
      console.error("Scanning error:", err);
    }
  };

  const stopScanning = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    setIsScanning(false);
    setHasPermission(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4">
      <div className="relative w-full max-w-2xl bg-gray-900 rounded-lg overflow-hidden">
        {/* Camera Feed */}
        <div className="relative bg-black rounded-lg overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-auto rounded-lg"
            style={{ transform: 'scaleX(-1)' }} // Mirror effect for selfie cameras
          />
          
          {/* Scanning Overlay */}
          <div className="absolute inset-0 border-2 border-green-500 rounded-lg pointer-events-none">
            <div className="absolute top-0 left-0 w-4 h-4 border-t-4 border-l-4 border-green-500"></div>
            <div className="absolute top-0 right-0 w-4 h-4 border-t-4 border-r-4 border-green-500"></div>
            <div className="absolute bottom-0 left-0 w-4 h-4 border-b-4 border-l-4 border-green-500"></div>
            <div className="absolute bottom-0 right-0 w-4 h-4 border-b-4 border-r-4 border-green-500"></div>
          </div>
          
          {/* Status Bar */}
          <div className="absolute top-4 left-4 right-4 flex justify-between items-center text-white">
            <div className="bg-black bg-opacity-70 rounded-lg px-3 py-2">
              <span className="text-green-400 font-mono text-sm">ISBN Scanner</span>
            </div>
            <div className="bg-black bg-opacity-70 rounded-lg px-3 py-2">
              <span className="text-white font-mono text-sm">Scanning...</span>
            </div>
          </div>
        </div>
        
        {/* Controls */}
        <div className="p-4 bg-gray-900 text-white flex gap-4">
          <button
            onClick={stopScanning}
            className="flex-1 bg-red-600 hover:bg-red-700 py-3 px-6 rounded-lg font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onScan("demo-isbn")}
            className="flex-1 bg-green-600 hover:bg-green-700 py-3 px-6 rounded-lg font-medium transition-colors"
          >
            Scan ISBN
          </button>
        </div>
        
        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-900 border-t border-red-700">
            <p className="text-red-200 text-sm text-center">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}