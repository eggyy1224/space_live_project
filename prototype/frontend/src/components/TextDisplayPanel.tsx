import React, { useEffect, useState } from "react";

import { getDisplayText } from "../services/api";

interface TextDisplayPanelProps {
  isVisible: boolean;
  onClose: () => void;
}

const panelStyle: React.CSSProperties = {
  position: "fixed",
  top: "20px",
  left: "20px",
  background: "rgba(0, 0, 0, 0.9)",
  border: "1px solid #555",
  borderRadius: "8px",
  color: "white",
  fontFamily: "Arial, sans-serif",
  fontSize: "14px",
  zIndex: 1000,
  minWidth: "260px",
  maxWidth: "320px",
  padding: "15px",
};

const TextDisplayPanel: React.FC<TextDisplayPanelProps> = ({
  isVisible,
  onClose,
}) => {
  const [text, setText] = useState("");

  useEffect(() => {
    if (!isVisible) return;
    getDisplayText()
      .then((data) => setText(data.text))
      .catch(() => setText(""));
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <div style={panelStyle}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "10px",
        }}
      >
        <h3 style={{ margin: 0, fontSize: "16px" }}>文字顯示</h3>
        <button
          onClick={onClose}
          style={{
            background: "transparent",
            border: "none",
            color: "white",
            cursor: "pointer",
          }}
        >
          ×
        </button>
      </div>
      <div style={{ whiteSpace: "pre-wrap" }}>{text}</div>
    </div>
  );
};

export default TextDisplayPanel;
