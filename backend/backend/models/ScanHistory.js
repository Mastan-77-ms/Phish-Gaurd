import mongoose from "mongoose";

const ScanHistorySchema = new mongoose.Schema({
  url: { type: String, lowercase: true },
  risk_score: Number,
  status: String,
  risk_label: String,
  response_time: Number,
  risk_reasons: [String],
  timestamp: { type: Date, default: Date.now }
});

export default mongoose.model("ScanHistory", ScanHistorySchema);
