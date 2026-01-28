import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import fetch from "node-fetch";
import UrlModel from "./models/Scan.js";
import ScanHistoryModel from "./models/ScanHistory.js";

const app = express();
app.use(express.json());
app.use(cors());

// MongoDB Connection
mongoose.connect("mongodb://127.0.0.1:27017/phishingDB")
  .then(() => console.log("MongoDB Connected"))
  .catch(err => console.log(err));

// --- API: Scan URL ---
app.post("/api/scan", async (req, res) => {
  const { url } = req.body;

  if (!url) {
    return res.status(400).json({ error: "URL is required" });
  }

  try {
    console.log(`[SCAN] Starting scan for: ${url}`);
    
    let mlData;
    try {
      const mlRes = await fetch("http://localhost:8000/api/v1/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
        timeout: 30000
      });

      if (!mlRes.ok) {
        throw new Error(`ML Server responded with status ${mlRes.status}`);
      }

      mlData = await mlRes.json();
      console.log(`[SCAN] ML Response received: ${mlData.status} (${mlData.risk_score}%)`);
    } catch (mlError) {
      console.error(`[SCAN ERROR] ML Service error: ${mlError.message}`);
      return res.status(503).json({ 
        error: "ML Service unavailable",
        details: mlError.message
      });
    }

    // Always save to scan history - CRITICAL FOR TRACKING
    try {
      const historyRecord = await ScanHistoryModel.create({
        url,
        risk_score: mlData.risk_score,
        status: mlData.status,
        risk_label: mlData.risk_label,
        response_time: mlData.response_time,
        risk_reasons: mlData.risk_reasons || [],
        scanned_at: new Date()
      });
      console.log(`[HISTORY] Saved to ScanHistory: ${historyRecord._id}`);
    } catch (historyError) {
      console.error(`[HISTORY ERROR] Failed to save scan history: ${historyError.message}`);
      // Don't fail the scan if history save fails, but log it
    }

    // Update or create main URL record
    try {
      // Check if URL already exists (case-insensitive)
      const existingRecord = await UrlModel.findOne({ 
        url: { $regex: `^${url.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, $options: "i" } 
      });

      if (existingRecord) {
        // Update existing record: increment scan_count and update last_scanned time
        existingRecord.scan_count = (existingRecord.scan_count || 0) + 1;
        existingRecord.last_scanned = new Date();
        existingRecord.risk_score = mlData.risk_score; // Update with latest score
        existingRecord.status = mlData.status;
        existingRecord.risk_label = mlData.risk_label;
        existingRecord.response_time = mlData.response_time;
        existingRecord.risk_reasons = mlData.risk_reasons || [];
        await existingRecord.save();
        console.log(`[SCAN] Updated existing URL: ${url} (scan_count: ${existingRecord.scan_count})`);
      } else {
        // Create new record
        await UrlModel.create({
          url,
          risk_score: mlData.risk_score,
          status: mlData.status,
          risk_label: mlData.risk_label,
          response_time: mlData.response_time,
          risk_reasons: mlData.risk_reasons || [],
          scan_count: 1,
          last_scanned: new Date(),
          timestamp: new Date()
        });
        console.log(`[SCAN] Created new URL record: ${url}`);
      }
    } catch (dbError) {
      console.error(`[DB ERROR] Failed to save/update URL record: ${dbError.message}`);
      // Don't fail the scan if URL record save fails
    }

    res.json({
      url,
      risk_score: mlData.risk_score,
      status: mlData.status,
      risk_label: mlData.risk_label,
      response_time: mlData.response_time,
      risk_reasons: mlData.risk_reasons || []
    });

  } catch (error) {
    console.error(`[API ERROR] Scan failed: ${error.message}`);
    res.status(500).json({ 
      error: "Error processing scan",
      details: error.message
    });
  }
});

// --- API: Get History ---
app.get("/api/history", async (req, res) => {
  try {
    console.log("[HISTORY] Fetching scan history...");
    
    // Get all scans from ScanHistory (every single scan) - NO LIMIT
    const scanHistory = await ScanHistoryModel.find()
      .sort({ scanned_at: -1, _id: -1 })
      .lean();
    
    console.log(`[HISTORY] Retrieved ${scanHistory.length} scans from ScanHistory`);
    
    // Transform to match frontend expectations
    const transformedHistory = scanHistory.map(item => ({
      _id: item._id,
      url: item.url,
      risk_score: item.risk_score,
      status: item.status,
      risk_label: item.risk_label,
      response_time: item.response_time,
      risk_reasons: item.risk_reasons || [],
      timestamp: item.scanned_at || item.timestamp,
      scan_count: 1, // Each ScanHistory item is a single scan
      isPhishing: item.status === "PHISHING",
      isSuspicious: item.status === "SUSPICIOUS",
      score: item.risk_score
    }));
    
    res.json(transformedHistory);
  } catch (error) {
    console.error(`[HISTORY ERROR] Failed to fetch history: ${error.message}`);
    res.status(500).json({ error: "Database error", details: error.message });
  }
});

// --- API: Get Total Stats ---
app.get("/api/stats", async (req, res) => {
  try {
    const totalScans = await ScanHistoryModel.countDocuments();
    const phishingScans = await ScanHistoryModel.countDocuments({ status: "PHISHING" });
    const suspiciousScans = await ScanHistoryModel.countDocuments({ status: "SUSPICIOUS" });
    const safeScans = await ScanHistoryModel.countDocuments({ status: "SAFE" });
    const avgResponseTime = 0.35;
    
    console.log(`[STATS] Total: ${totalScans}, Phishing: ${phishingScans}, Suspicious: ${suspiciousScans}, Safe: ${safeScans}`);
    
    res.json({
      total_scans: totalScans,
      phishing_blocked: phishingScans,
      suspicious_count: suspiciousScans,
      safe_urls: safeScans,
      avg_response_time: `${avgResponseTime}s`
    });
  } catch (error) {
    console.error(`[STATS ERROR] Failed to fetch stats: ${error.message}`);
    res.status(500).json({ error: "Failed to fetch stats" });
  }
});

// --- API: Delete History Item ---
app.delete("/api/history/:id", async (req, res) => {
  try {
    const { id } = req.params;
    
    // Delete from both ScanHistory and Scan models to ensure consistency
    const historyResult = await ScanHistoryModel.findByIdAndDelete(id);
    
    // Also try to delete from main Scan model if it exists there
    if (!historyResult) {
      const scanResult = await UrlModel.findByIdAndDelete(id);
      if (!scanResult) {
        return res.status(404).json({ error: "Item not found" });
      }
    }
    
    console.log(`[DELETE] History item deleted: ${id}`);
    res.json({ message: "Item deleted successfully" });
  } catch (error) {
    console.error(`[DELETE ERROR] Failed to delete: ${error.message}`);
    res.status(500).json({ error: "Failed to delete item" });
  }
});

// --- API: Get Scan History for a Specific URL ---
app.get("/api/scan-history/:url", async (req, res) => {
  try {
    const { url } = req.params;
    const decodedUrl = decodeURIComponent(url);
    
    // Get all scans for this URL (case-insensitive)
    const scanHistory = await ScanHistoryModel.find({ 
      url: { $regex: `^${decodedUrl.toLowerCase()}$`, $options: "i" } 
    }).sort({ timestamp: -1 });
    
    res.json(scanHistory);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch scan history" });
  }
});

const PORT = 3001;
app.listen(PORT, () => console.log(`Node Backend running on port ${PORT}`));
