import mongoose from "mongoose";

mongoose.connect("mongodb://127.0.0.1:27017/phishingDB")
  .then(() => console.log("MongoDB Connected"))
  .catch(err => console.error(err));
