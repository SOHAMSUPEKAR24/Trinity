import React, { useState } from "react";
import { Modal, Box, Typography, TextField, Button, Paper } from "@mui/material";
import axios from "axios";

interface Props {
  open: boolean;
  onSubmit: (token: string) => void;
}

const LicensePrompt: React.FC<Props> = ({ open, onSubmit }) => {
  const [token, setToken] = useState<string>("");

  const handleSubmit = async () => {
    const trimmedToken = token.trim();
    if (!trimmedToken) return;

    try {
      const res = await axios.post("http://localhost:8000/api/license/verify", {
        license_token: trimmedToken,
      });

      // ✅ Backend verified successfully
      if (res.status === 200 && res.data.status?.includes("valid")) {
        onSubmit(trimmedToken); // 🔓 Unlock access
      } else {
        alert("❌ License verification failed.");
      }
    } catch (err) {
      alert("❌ License verification failed.");
    }
  };

  return (
    <Modal open={open}>
      <Box
        sx={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          width: 400,
          p: 4,
          bgcolor: "background.paper",
          borderRadius: 2,
          boxShadow: 24,
        }}
      >
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            🔐 Enter Your License Token
          </Typography>
          <TextField
            label="License Token"
            fullWidth
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Paste your license key here"
            sx={{ mb: 2 }}
          />
          <Button variant="contained" color="primary" fullWidth onClick={handleSubmit}>
            Unlock Access
          </Button>
        </Paper>
      </Box>
    </Modal>
  );
};

export default LicensePrompt;