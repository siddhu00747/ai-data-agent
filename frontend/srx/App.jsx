import React, {useState} from "react";
import UploadComponent from "./UploadComponent";
import ChatComponent from "./ChatComponent";

export default function App(){
  const [uploadInfo, setUploadInfo] = useState(null);
  return (
    <div style={{maxWidth:900, margin:"20px auto", fontFamily:"Inter, Arial"}}>
      <h2>AI Data Agent — Demo (Hinglish ready)</h2>
      {!uploadInfo && <UploadComponent onUploaded={setUploadInfo} />}
      {uploadInfo && <ChatComponent uploadInfo={uploadInfo} />}
    </div>
  );
}
