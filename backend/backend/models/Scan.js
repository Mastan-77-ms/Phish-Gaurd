import mongoose from "mongoose";

const ScanSchema = new mongoose.Schema({
  url: { type: String, unique: true, lowercase: true },
  risk_score: Number,
  status: String,
  risk_label: String,
  response_time: Number,
  risk_reasons: [String],
  scan_count: { type: Number, default: 1 },
  last_scanned: { type: Date, default: Date.now },
  timestamp: { type: Date, default: Date.now }
});

export default mongoose.model("Scan", ScanSchema);
