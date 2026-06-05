const fs = require('fs');
const path = require('path');

async function testVoicePipeline() {
  try {
    console.log("Starting local integration test...");
    
    // 1. Locate the generated file
    const filePath = path.join(__dirname, 'voice-test.wav');
    if (!fs.existsSync(filePath)) {
      console.error(`Error: Could not find voice-test.wav at ${filePath}`);
      return;
    }

    // 2. Read file and wrap into FormData
    const fileBuffer = fs.readFileSync(filePath);
    const audioBlob = new Blob([fileBuffer], { type: 'audio/wav' });
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'voice-test.wav');
    formData.append('language', 'en');

    console.log("Sending multipart request to Express server on port 5000...");
    
    // 3. Fire the request directly to your Express server
    const response = await fetch('http://localhost:5000/api/voice/chat', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    console.log("\n--- [TEST RESPONSE FROM EXPRESS SERVER] ---");
    console.log(JSON.stringify(data, null, 2));
    
  } catch (error) {
    console.error("Test failed with error:", error.message);
  }
}

testVoicePipeline();