import React, { useState } from "react";
import { Container, Typography, Button, Box } from "@mui/material";
import TestGenerator from "./components/TestGenerator";
import LicensePrompt from "./components/LicensePrompt";
import axios from "axios";

const App: React.FC = () => {
  const [licenseToken, setLicenseToken] = useState<string>("");
  const [isLicenseValid, setIsLicenseValid] = useState<boolean>(false);

  const handleLicenseSubmit = async (token: string) => {
    try {
      const res = await axios.post("http://localhost:8000/api/license/verify", {
        license_token: token,
      });

      console.log("🔁 Backend response:", res.data);

      if (res.status === 200 && res.data?.status?.includes("valid")) {
        setLicenseToken(token);
        setIsLicenseValid(true);
      } else {
        alert("❌ License verification failed.");
      }
    } catch (err) {
      console.error("❌ License check error:", err);
      alert("❌ Invalid or expired license. Access denied.");
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 8 }}>
      {!isLicenseValid && <LicensePrompt open={true} onSubmit={handleLicenseSubmit} />}

      {isLicenseValid && (
        <>
          <Box textAlign="center">
            <Typography variant="h3" gutterBottom>
              🧠 Trinity QA Autopilot
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              AI-driven Testing | Healing | CI Debugging | Security | Licensing
            </Typography>
            <Button variant="contained" color="primary" size="large" sx={{ mb: 4 }}>
              Start Trinity
            </Button>
          </Box>

          <TestGenerator licenseToken={licenseToken} />
        </>
      )}
    </Container>
  );
};

export default App;